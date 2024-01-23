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
from concurrent.futures import ThreadPoolExecutor

######################################################################

# Description: Splits a string at the first occurrence of a dot and returns a pandas Series.
def split_by_dot(s):
    if '.' in s:
        return pd.Series(s.split('.', 1))
    else:
        return pd.Series([None, None])

# Description: Splits a string at the first occurrence of 'Vlanif' and returns a pandas Series.
def split_by_Vlanif(s):
    if 'Vlanif' in s:
        return pd.Series(s.split('Vlanif', 1))
    else:
        return pd.Series([None, None])

# Description: Splits a string at the first occurrence of '/-' and returns a pandas Series.
def split_by_slash(s):
    if '/-' in s:
        return pd.Series(s.split('/-', 1))
    else:
        return pd.Series([None, None])

########################################################################

# Function: ipbb_schedule
# Description: Performs IP Broadband (IPBB) schedule to collect ARP information and create CSV files.
# Parameters:
#   - i: IP address of the device.
def ipbb_schedule(i):
    idate = str(dt.today()).replace("-", "")
    insert_path = f"/home/data/ipbb/{idate}/"
    makedirs(path.dirname(insert_path), exist_ok=True)

    try:
        print("IP ADDRESS: ", i)
        arp_cmd = 'screen-length 0 temporary \n dis arp all \n'
        mac_cmd = 'display bridge mac-address\n'
        host_cmd = 'display current-configuration | include sysname\n'
        username = cred.username()
        password = cred.password()
        port = cred.port()

        # Get MAC address and hostname information
        mac = connector(i, username, password, port, mac_cmd)
        mac = str(mac)
        mac = mac.split("address:")[1].split("\n")[0].rstrip(" ")
        mac = mac.replace("-", "").upper().replace(" ", "").replace("\r", "")
        hostname = connector(i, username, password, port, host_cmd)
        hostname = hostname.split("sysname")[-1].split("\n")[0].upper().replace(" ", "").replace("\r", "")
        filename = str(hostname + "-" + i)

        # Get ARP information
        output = connector(i, username, password, port, arp_cmd)
        output = str(re.findall('(?s)(?=IP ADDRESS)(.*?)(?>Total)', output))
        output = str(re.sub(r"\\r\\n\s+", " ", output))
        output = str(output).replace("\\r\\n", "\n").replace("['", "").replace("']", "").replace("\\t", "")

        # Convert ARP information to DataFrame
        data = StringIO(output)
        df = pd.read_csv(data, delim_whitespace=True, skiprows=2, skipfooter=1, engine="python",
                         names=["ip", "mac", "expire", "type", "interface", "vrf", "vlan"])

        # Manipulate and clean 
        df.vlan = df.vlan.astype(str)
        df.vrf = df.vrf.astype(str)
        df["smac"] = mac
        df["shost"] = hostname
        df["sip"] = i
        df["mac"] = df.mac.str.replace("-", "").str.upper()
        df.vlan.str.replace("/-", "")
        df[["new1", "new2"]] = df["interface"].apply(split_by_dot)
        df.loc[~df.new2.isnull(), "vlan"] = df["new2"]
        df.drop(["new1", "new2"], axis=1, inplace=True)
        df[["new1", "new2"]] = df["interface"].apply(split_by_Vlanif)
        df.loc[~df.new2.isnull(), "vlan"] = df["new2"]
        df.drop(["new1", "new2"], axis=1, inplace=True)
        df[["new1", "new2"]] = df["vrf"].apply(split_by_slash)
        df.loc[~df.new1.isnull(), "vlan"] = df["new1"]
        df.drop(["new1", "new2"], axis=1, inplace=True)
        df["vrf"] = df["vrf"].str.replace("/-", "")
        df["vrf"] = df["vrf"].str.replace(r'^\d+$', "None", regex=True)
        df["vlan"] = df["vlan"].str.replace(r'^\D+$', "None", regex=True)
        df["vlan"] = df["vlan"].str.replace("/-", "")
        new_cols = ["shost", "sip", "smac", "ip", "mac", "expire", "type", "interface", "vrf", "vlan"]
        df = df.reindex(columns=new_cols)
        print(df)
        print("DONE Successfully")
        csv_filename = filename + ".csv"
        filename = insert_path + '/' + csv_filename
        df.to_csv(filename, index=False)
    
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

if __name__ == "__main__":
    idate = str(dt.today()).replace("-", "")
    main_ip = f"/home/ip_list/ipbb/ip_list.txt.bak"
    log_path = f"/home/log/ipbb/{idate}/"
    makedirs(path.dirname(log_path), exist_ok=True)
    tmp_ip = f"/home/log/ipbb/{idate}/ip_list.txt.bak"
    cp(main_ip, tmp_ip)
    ip_list = cred.ip(tmp_ip)
    
    # Use ThreadPoolExecutor for concurrent execution of IPBB schedule on multiple devices
    with ThreadPoolExecutor(max_workers=200) as executor:
        ip_list = [i for i in ip_list]
        executor.map(ipbb_schedule, ip_list)