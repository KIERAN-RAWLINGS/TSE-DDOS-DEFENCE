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

        client_sock.close()

        for packet in capture:
            if 'TCP' in packet:
                src_ip = packet['IP'].src
                dst_ip = packet['IP'].dst

                if src_ip not in connections:
                    connections[src_ip] = []

                connections[src_ip].append(packet.sniff_time.timestamp())
                connections[src_ip] = [t for t in connections[src_ip] if t > packet.sniff_time.timestamp() - time_window]

                if len(connections[src_ip]) > connection_limit:
                    print(f'Potential DDOS attack from {src_ip} to {dst_ip}')
                    print(f'\n {src_ip} has been blocked')
                    # Call email alert function gaining the attention of senior secuirty staff
                    email_alert(connections[src_ip]) 
                    # Call a powershell script to block the responsible IP addresses
                    temp_ip = connections[src_ip]
                    fileloc = "C:\\Users\\Danie\\Desktop\\Temp TSE Assignment\\IP_BLOCKING_SCRIPT.ps1"
                    p = subprocess.Popen(["powershell.exe", '-command', "C:\\Users\\Target\\Desktop\\IP_BLOCKING_SCRIPT.ps1", temp_ip], stdout=sys.stdout)

        

    

detect_ddos('0.0.0.0', 80)
