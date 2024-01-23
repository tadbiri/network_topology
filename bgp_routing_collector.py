#!/usr/local/bin/python3.12
import sys
sys.path.append('/home/app/collector')
from cfg.connector import connector
from time import sleep 
import re
import pandas as pd
from datetime import datetime, date
from io import StringIO
from os import remove, getcwd, makedirs, path
import cfg.postgres_connector as pg
import cfg.credential as cred
from schedule import every, run_pending
##############################################################

def ipbb_routing_schedule():
    """
    Performs IP Broadband (IPBB) routing schedule to collect BGP routing table information
    and store it in CSV files and PostgreSQL database.

    The script connects to multiple IP addresses specified in the 'ip_list.txt' file, gathers BGP routing table data,
    and stores it in CSV files organized by date. The information is then inserted into a PostgreSQL database table.

    Returns:
    None
    """

    # Path to the main IP list file
    main_ip = "/home/ip_list/ipbb_routing/ip_list.txt"

    # Retrieve IP list, credentials, and current date
    ip_list = cred.ip(main_ip)
    username = cred.username()
    password = cred.password()
    port = cred.port()
    idate = str(date.today()).replace("-", "")
    time = datetime.now().strftime("%H-%M-%S")

    # Create directory for storing CSV files
    insert_path = f"/home/data/ipbb_route/{idate}/"
    makedirs(path.dirname(insert_path), exist_ok=True)

    # PostgreSQL table details
    table_col = '"shost","destination","proto","pre","cost","flags","nexthop","interface"'
    table = "ipbb_routing_table_log"

    # Commands to retrieve hostname and BGP routing table information
    host_cmd = 'display current-configuration | include sysname\n'
    command_c = 'screen-length 0 temporary \n dis ip routing-table protocol bgp \n' 

    # Loop through each IP in the list
    for ip in ip_list:
        try:
            print(ip)

            # Retrieve BGP routing table information
            output = connector(ip, username, password, port, command_c)
            host = connector(ip, username, password, port, host_cmd)

            # Extract hostname from the command output
            hostname = host.split("sysname")[-1].split("\n")[0].upper().replace(" ", "").replace("\r", "")

            # Process active and inactive routes
            active = re.findall('(?s)(?=<Active>)(.*?)(?=<Inactive>)', output)
            active = str(active).replace("\\r\\n", "\n").replace("['", "").replace("']", "")
            inactive = re.findall('(?s)(?=<Inactive>)(.*?)(?=<IGSZVA>)', output)
            inactive = str(inactive).replace("\\r\\n", "\n").replace("['", "").replace("']", "")

            # Read data into Pandas DataFrames
            active = StringIO(active)
            inactive = StringIO(inactive)
            df1 = pd.read_csv(active, delim_whitespace=True, skiprows=4, skipfooter=1, engine="python",
                              names=["destination", "proto", "pre", "cost", "flags", "nexthop", "interface"])
            df2 = pd.read_csv(inactive, delim_whitespace=True, skiprows=4, engine="python",
                              names=["destination", "proto", "pre", "cost", "flags", "nexthop", "interface"])

            # Concatenate DataFrames
            frames = [df1, df2]
            df = pd.concat(frames)

            # Add hostname as a new column
            df['shost'] = hostname  

            # Reorganize columns
            new_cols = ["shost", "destination", "proto", "pre", "cost", "flags", "nexthop", "interface"]
            df = df.reindex(columns=new_cols)

            # Define CSV filename and path
            csv_filename = hostname + "-" + time + ".csv"
            filename = insert_path + '/' + csv_filename

            # Save DataFrame to CSV file
            df.to_csv(filename, index=False, header=False)

            # Insert data into PostgreSQL database
            pg.postgres_insert(filename, table, table_col)

            # Pause for 1 second between iterations
            sleep(1)

        except Exception as e:
            print(f"An error occurred: {e}")
            continue

# Schedule the script to run every day at 08:00
every().day.at("08:00").do(ipbb_routing_schedule)

# Run the scheduled tasks
while True:
    run_pending()
    sleep(60)
