#!/usr/local/bin/python3.12
import pandas as pd
from cfg.connector import connector
import cfg.credential as cred
from os import remove, getcwd, makedirs, path
from time import sleep
import re
from datetime import date as dt
from shutil import copyfile as cp
from io import StringIO
import numpy as np
from schedule import every, run_pending
import threading
import subprocess

#################### Function to check node connectivity with Ping Protocol
def is_pingable(i):
    try:
        subprocess.check_output(["ping", "-c", "1", i])
        print("PINGABLE")
    except subprocess.CalledProcessError:
        print("NOT PINGABLE")

#################### Main collector Function
def ip_schedule():

    ### Preparation ### 

    # Get the current date in the format YYYYMMDD
    idate = str(dt.today()).replace("-", "")

    # Path to the main IP list of nodes
    main_ip = f"/home/ip_list/ip/ip_list.txt"

    # Path to log of the remaining unsuccessful IPs of nodes 
    log_path = f"/home/log/ip/"
    makedirs(path.dirname(log_path), exist_ok=True)

    # Create log file with time
    tmp_ip = f"/home/log/ip/{idate}.txt"
    cp(main_ip, tmp_ip)

    # Go through IP list Line by line
    ip_list = cred.ip(tmp_ip)
    total_ip = len(ip_list)
    remained_ip = total_ip

    # Path to final csv output 
    insert_path = f"/home/data/ip/{idate}/"
    makedirs(path.dirname(insert_path), exist_ok=True)

    ### LOOP Through the IP LIST ###
    for i in ip_list:
        try:

            with open(tmp_ip, 'r') as fp:
                for count, line in enumerate(fp):
                    pass
            print("TOTAL IP: ", total_ip, "REMAINED IP: ", count + 1)

            # Define commands and credentials
            peer_cmd = 'screen-length 0 temporary \n dis bgp peer verbose \n'
            username = cred.username()
            password = cred.password()
            port = cred.port()

            print("IP ADDRESS: ", i)
            is_pingable(i)

            # Establish connection using custom connector
            peer_cmd = connector(i, username, password, port, peer_cmd)
            peer_cmd = str(peer_cmd)

            # Extract hostname from the command output
            hostname = re.findall(r'\<([^\s]+)\>', peer_cmd)[0]
            print("HOSTNAME: ", hostname)

            # Split the command output into BGP peer sections
            peers = re.split('BGP Peer is', peer_cmd)
            df_main = pd.DataFrame(dtype=str, columns=["phost", "pip", "interface"])

            for peer in peers:
                pip = str(re.findall(r'\s+(\d+\.\d+\.\d+.\d+)\,', peer)).replace("['", "").replace("']", "")
                if pip == "[]":
                    continue

                phost = str(re.findall(r'Peer\'s description: \"(.+)\"', peer)).replace("['", "").replace("']", "")
                interface = np.nan
                
                # Create a temporary DataFrame and concatenate with the main DataFrame
                df_tmp = str(phost) + " " + str(pip) + " " + str(interface)
                df_tmp = StringIO(df_tmp)
                df_tmp = pd.read_csv(df_tmp, delim_whitespace=True, names=["phost", "pip", "interface"])

                frames = [df_main, df_tmp]
                df_main = pd.concat(frames, ignore_index=True)
                df_main["shost"] = hostname
                df_main["sip"] = i

                new_col = ["shost", "sip", "phost", "pip", "interface"]
                df_main = df_main.reindex(columns=new_col)
                print(df_main, "\n\n")

            # Save the temporary DataFrame to a CSV file
            csv_filename = hostname + "-" + i + ".csv"
            filename = insert_path + '/' + csv_filename
            df_main.to_csv(filename, index=False)

            # Remove the processed IP from the log file
            with open(tmp_ip, "r") as f:
                lines = f.readlines()
            with open(tmp_ip, "w") as f:
                for line in lines:
                    if line.strip("\n") != i:
                        f.write(line)

            print("END\n\n")
            
        except ConnectionError as conn_error:
            print(f"ConnectionError: {conn_error}")
            # Handle connection-related errors (e.g., unable to connect to the device)

        except TimeoutError as timeout_error:
            print(f"TimeoutError: {timeout_error}")
            # Handle timeout-related errors (e.g., connection or operation timeout)

        except Exception as general_error:
            print(f"An unexpected error occurred: {general_error}")
            # Handle other unexpected errors

        else:
            print("DONE Successfully")

# Execute the main function
ip_schedule()
# Uncomment the following lines to schedule the function for daily execution
# every().day.at("07:00").do(ip_schedule)
# while True:
#    run_pending()
#    sleep(60)
