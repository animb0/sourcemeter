# -*- coding: utf-8 -*-
"""
Created on Tue Mar  4 15:13:15 2025

@author: ZahndN
"""

import paramiko
import os

# Define connection details
hostname = "raspberrypi.local"  # Your Raspberry Pi IP address or hostname
username = "pi"  # Default username for Raspberry Pi
password = "raspberry"  # Default password (you may have set your own)
remote_dir = "/home/pi/"  # The directory where your files are located
local_path = "C:/Users/YourUsername/Desktop/voltage_data.txt"  # Local path on your PC

# Establish SSH connection to the Raspberry Pi
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(hostname, username=username, password=password)

# Get the list of files in the remote directory
stdin, stdout, stderr = ssh.exec_command(f'ls -lt {remote_dir}')

# Read the output of the 'ls' command, which lists files sorted by modification time
files = stdout.read().decode().splitlines()

# Get the most recent file
latest_file = files[0]

# Construct the full remote file path
remote_path = os.path.join(remote_dir, latest_file)

# Print the file that will be transferred
print(f"Transferring file: {remote_path}")

# Use SCP to copy the latest file from the Raspberry Pi to the local PC
scp_command = f"pscp {username}@{hostname}:{remote_path} {local_path}"

# Run the SCP command to download the file
os.system(scp_command)

# Close the SSH connection
ssh.close()

print("File transfer completed.")
