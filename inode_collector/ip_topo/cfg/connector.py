#!/usr/local/bin/python3.12
from paramiko import SSHClient, AutoAddPolicy
from time import sleep

############################################################
# Function: connector
# Description: Establishes an SSH connection to a remote host and executes a specified command.
# Parameters:
#   - h: Hostname or IP address of the remote server.
#   - u: Username for authentication.
#   - p: Password for authentication.
#   - port: SSH port of the remote server.
#   - cmd: Command to be executed on the remote server.
# Returns:
#   - output: Output of the executed command on the remote server.
def connector(h, u, p, port, cmd):
    # Create an SSH client instance
    ssh_client = SSHClient()

    # Automatically add the host to the list of known hosts
    ssh_client.set_missing_host_key_policy(AutoAddPolicy)

    # Connect to the remote server
    ssh_client.connect(hostname=h, username=u, password=p, port=port, timeout=20)

    # Open an SSH channel
    channel = ssh_client.invoke_shell()

    # Send the specified command to the remote server
    channel.send(cmd)

    # Wait for the command to be executed (5 seconds in this case)
    sleep(5)

    # Receive the output of the command
    output = channel.recv(9999999)

    # Decode the output from bytes to utf-8
    output = output.decode("utf-8")

    # Close the SSH channel
    channel.close()

    # Close the SSH connection
    ssh_client.close()

    # Return the output of the executed command
    return output
