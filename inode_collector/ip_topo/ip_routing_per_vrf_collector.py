#!/usr/local/bin/python3.12
import pandas as pd
from cfg.connector import connector, connector_invoke
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
from concurrent.futures import ThreadPoolExecutor

#####################################################
def is_pingable(i):
    """
    Checks if a given IP address is pingable.

    Args:
    - i (str): IP address to be checked.

    Returns:
    - None: Prints "PINGABLE" if the IP is pingable, "NOT PINGABLE" otherwise.
    """
    try:
        subprocess.check_output(["ping", "-c", "1", i])
        print("PINGABLE")
    except subprocess.CalledProcessError:
        print("NOT PINGABLE")

######################################################################

def ipvrf_schedule(i):
    """
    Collects information about IP routes and VPN instances for a given IP address.

    Args:
    - i (str): IP address to collect information for.

    Returns:
    - None: Prints the collected information and saves it to a CSV file.
    """
    idate = str(dt.today()).replace("-", "")
    insert_path = f"/home/data/ipvrf/{idate}/"
    makedirs(path.dirname(insert_path), exist_ok=True)

    try:
        # Commands and credentials
        vrf_cmd = 'screen-length 0 temporary \n dis ip vpn-instance \n'
        username = cred.username()
        password = cred.password()
        port = cred.port()

        print("IP ADDRESS: ", i)
        is_pingable(i)

        # Invoke commands and get VPN instances
        vrf_cmd = connector(i, username, password, port, vrf_cmd)
        vrf_cmd = str(vrf_cmd)
        vrfs = re.findall(r'(MCCI\_[^\s]+)', vrf_cmd)

        def shift_rows(df):
            # Shift rows with non-numeric IPs
            for index, row in df.iterrows():
                if any(char.isalpha() for char in str(row['ip'])):
                    df.loc[index, 'ip'] = df.loc[index - 1, 'ip']

        hostname = re.findall(r'\<([^\s]+)\>', vrf_cmd)[0]
        df_main = pd.DataFrame(dtype=str, columns=["shost", "sip", "vrf", "ip", "proto", "pre", "cost", "flags", "nexthop", "interface"])

        # Iterate over VPN instances
        for vrf in vrfs:
            # Command to get routing table for a specific VPN instance
            routing_cmd = f'screen-length 0 temporary \n dis ip routing-table vpn-instance {vrf} \n'
            routing = connector(i, username, password, port, routing_cmd)
            routing = str(re.findall(r'(?s)(?=Destination/Mask)(.*?)(?>\<[^\s]+\>)', routing)).replace("\\r\\n", "\n").replace(r"\s+", " ").replace("['", "").replace("']", "")

            df_tmp = StringIO(routing)
            df_tmp = pd.read_csv(df_tmp, delim_whitespace=True, skiprows=2, names=["ip", "proto", "pre", "cost", "flags", "nexthop", "interface"])
            df_tmp = df_tmp.astype(str)
            mask = df_tmp['ip'].str.contains('[a-zA-Z]')
            df_tmp.loc[mask, 'proto':] = df_tmp.loc[mask, "ip":"interface"].shift(axis=1)
            shift_rows(df_tmp)

            df_tmp["shost"] = str(hostname)
            df_tmp["sip"] = str(i)
            df_tmp["vrf"] = str(vrf)
            new_columns = ["shost", "sip", "vrf", "ip", "proto", "pre", "cost", "flags", "nexthop", "interface"]
            df_tmp = df_tmp.reindex(columns=new_columns)

            frames = [df_main, df_tmp]
            df_main = pd.concat(frames, ignore_index=True)

        def sys2ip(ip):
            # Convert system IP format to standard IP format
            ip = str(ip).replace(".", "")
            ip = re.findall(r'...', ip)
            ip = [int(i) for i in ip]
            ip = ".".join(str(element) for element in ip)
            return pd.Series([ip])

        # Command to get ISIS information
        isis_cmd = f'screen-length 0 temporary \n dis isis name-table \n'
        isis_cmd = connector(i, username, password, port, isis_cmd)
        isis_cmd = str(re.findall(r'(?s)(?=System)(.*?)(?>\<[^\s]+\>)', isis_cmd)).replace("\\r\\n", "\n").replace(r"\s+", " ").replace("['", "").replace("']", "")
        df_isis = StringIO(isis_cmd)
        df_isis = pd.read_csv(df_isis, delim_whitespace=True, skiprows=2, names=["pid", "pname", "type"])
        df_isis["pid"] = df_isis["pid"].apply(sys2ip)
        df_isis.drop(["type"], axis=1, inplace=True)

        print(df_isis, "\n")

        # Merge main DataFrame with ISIS information
        df_total = pd.merge(df_main, df_isis, how="left", left_on=["nexthop"], right_on=["pid"])

        print(df_total, "\n")

        # Save the result to a CSV file
        csv_filename = hostname + "-" + i + ".csv"
        filename = insert_path + '/' + csv_filename
        df_total.to_csv(filename, index=False)
        
        # Remove IP address from temporary file
        with open(tmp_ip, "r") as f:
            lines = f.readlines()
        with open(tmp_ip, "w") as f:
            for line in lines:
                if line.strip("\n") != i:
                    f.write(line)

        print("END\n\n")

    except Exception as e:
        print("Error:", str(e))


if __name__ == "__main__":
    # Setup
    idate = str(dt.today()).replace("-", "")
    main_ip = f"/home/ip_list/ipvrf/ip_list.txt"
    log_path = f"/home/log/ipvrf/"
    makedirs(path.dirname(log_path), exist_ok=True)
    tmp_ip = f"/home/log/ipvrf/{idate}.txt"
    cp(main_ip, tmp_ip)
    ip_list = cred.ip(tmp_ip)
    
    # Multi-threading execution
    with ThreadPoolExecutor(max_workers=10) as executor:
        ip_list = [i for i in ip_list]
        executor.map(ipvrf_schedule, ip_list)
