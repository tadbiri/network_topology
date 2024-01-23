#!/usr/bin/python3.6

# Description: Returns the username for authentication.
def username():
    username = 'xxxxxx'
    return username

# Description: Returns the password for authentication.
def password():
    password = 'xxxxxxx'
    return password

# Description: Returns the default SSH port for connections.
def port():
    port = '22'
    return port

# Function: ip
# Description: Reads a file containing a list of IP addresses, removes newline characters,
#              and returns a list of IP addresses.
# Parameters:
#   - ip_list: Path to the file containing the list of IP addresses.
# Returns:
#   - ip_list: List of IP addresses read from the file.
def ip(ip_list):
    with open(ip_list) as list:
        ip_list = list.readlines()

        # Remove newline characters from each IP address
        for i in range(len(ip_list)):
            ip_list[i] = ip_list[i].rstrip("\n")

        return ip_list
