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

    # Path to the log of the remaining unsuccessful IPs of nodes
    log_path = f"/home/log/ip/"
    makedirs(path.dirname(log_path), exist_ok=True)

    # Create a log file with the current date
    tmp_ip = f"/home/log/ip/{idate}.txt"
    cp(main_ip, tmp_ip)

    # Go through the IP list line by line
    ip_list = cred.ip(tmp_ip)
    total_ip = len(ip_list)
    remained_ip = total_ip

    # Path to the final CSV output
    insert_path = f"/home/data/ip/{idate}/"
    makedirs(path.dirname(insert_path), exist_ok=True)
    df_main = pd.DataFrame(dtype=str, columns=["shost", "sip", "ospf-sip", "ospf-sint", "ospf-dip"])

    ### LOOP Through the IP LIST ###
    for i in ip_list:
        try:

            with open(tmp_ip, 'r') as fp:
                for count, line in enumerate(fp):
                    pass
            print("TOTAL IP: ", total_ip, "REMAINED IP: ", count + 1)

            # Define commands and credentials
            peer_cmd = 'screen-length 0 temporary \n dis ospf peer  \n'
            username = cred.username()
            password = cred.password()
            port = cred.port()

            print("IP ADDRESS: ", i)
            is_pingable(i)

            # Establish connection using custom connector
            peer_cmd = connector(i, username, password, port, peer_cmd)
            peer_cmd = str(peer_cmd)

            hostname = str(re.findall(r'\<([^\s]+)\>', peer_cmd)[0])
            sip = str(i)

            # Extract OSPF peers from the command output
            ospf_peers = re.findall(r'\sArea 0.0.0.0 interface (\d+\.\d+\.\d+\.\d+)\((\S+\.301)\)\'s\sneighbors\r\n\sRouter ID: \d+\.\d+\.\d+\.\d+\s+Address: (\d+\.\d+\.\d+\.\d+)', peer_cmd)

            for ospf_peer in ospf_peers:
                ospf_sip = ospf_peer[0]
                ospf_sint = ospf_peer[1]
                ospf_dip = ospf_peer[2]

                # Create a temporary DataFrame and concatenate with the main DataFrame
                df_tmp = str(hostname) + " " + str(sip) + " " + str(ospf_sip) + " " + str(ospf_sint) + " " + str(ospf_dip)
                df_tmp = StringIO(df_tmp)
                df_tmp = pd.read_csv(df_tmp, delim_whitespace=True, names=["shost", "sip", "ospf-sip", "ospf-sint", "ospf-dip"])
                frames = [df_main, df_tmp]
                df_main = pd.concat(frames, ignore_index=True)

            print(df_main, "\n\n")

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

    # Save the final DataFrame to a CSV file
    csv_filename = "IL_OSPF_PEERS.csv"
    filename = insert_path + '/' + csv_filename
    df_main.to_csv(filename, index=False)

# Execute the main function
ip_schedule()

# Uncomment the following lines to schedule the function for daily execution
# every().day.at("07:00").do(ip_schedule)
# while True:
#     run_pending()
#     sleep(60)