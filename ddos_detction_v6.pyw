## SEND TO CHAR for comments 

import pyshark
import socket
import time
import sys
import subprocess
import smtplib

def email_alert(ip_addr):
    print("Sending email to {TBD}")

def detect_ddos(ip_addr, port):
    capture = pyshark.LiveCapture(interface='eth0', bpf_filter='tcp')
    connection_limit = 100
    time_window = 40
    addr = (ip_addr, port)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(addr)
    
    sock.listen(connection_limit)

    connections = {}
    while True:
        client_sock, client_addr = sock.accept()
        now = time.time()

        if client_addr[0] not in connections:
            connections[client_addr[0]] = []
        
        connections[client_addr[0]].append(now)
        connections[client_addr[0]] = [t for t in connections[client_addr[0]] if t > now - time_window]
        
        if len(connections[client_addr[0]]) > connection_limit:
            print(f'Potential DDOS attack from {client_addr[0]}')

            # Get IP address, send to an admin requested powershell script to block IP, if result.returncode = 0 then success!
            # Also when the IP is blocked, no more packets are recieved.
            temp_ip = client_addr[0]

            ps_script = f"""
                New-NetFirewallRule -DisplayName "Block {temp_ip}" -Direction Inbound -LocalPort Any -Protocol Any -Action Block -RemoteAddress {temp_ip}
                """
            ps_script_2 = f"""
                Add-Type -AssemblyName PresentationCore,PresentationFramework
                $MessageBody = "DDOS detected!!! {temp_ip} blocked"
                $MessageIcon = [System.Windows.MessageBoxImage]::Warning
                $Result = [System.Windows.MessageBox]::Show($MessageBody, $messageicon)
                """
            


            powershell_cmd = ["powershell.exe", "-Command", ps_script]

            result = subprocess.run(powershell_cmd, capture_output=True)

            powershell_cmd_2 = ["powershell.exe", "-Command", ps_script_2]

            output = subprocess.run(powershell_cmd_2, capture_output=True)
            

            

            if result.returncode == 0:
                connections[client_addr[0]] = []
                
        client_sock.close()



        

    

detect_ddos('0.0.0.0', 80)
