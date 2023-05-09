import pyshark, socket, time, sys, subprocess
import smtplib, sendgrid, os
from sendgrid.helpers.mail import Mail, Email, To, Content
from datetime import datetime

def email_alert(ip_addr):

    # Valid api key with mail send permissions
    my_sg = sendgrid.SendGridAPIClient(api_key='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')
    
    # Verified sender of the email (API side)
    from_email = Email("TSE.PTS.Notification@proton.me")  

    #---------------------------------------------------------------------#
    # Please enter the address you would like alerts sent to...
    to_email = To("liamthefliam@gmail.com")
    #---------------------------------------------------------------------#

    # Get timestamp & device info
    now = datetime.now()
    dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
    device = socket.gethostname()

    # Create email
    subject = "Suspected DDoS attack on " + device + "!"
    body = "Potentially malicious packets recieved from IP:" + ip_addr + " at " + dt_string + ". Traffic from that IP has been blocked and" + " can be reviewed from that devices firewall rules. Stay safe!"       
    content = Content("text/plain", body)
    mail = Mail(from_email, to_email, subject, content)
    
    # Send an HTTP POST request to /mail/send
    response = my_sg.client.mail.send.post(request_body=mail.get())
    
def detect_ddos(ip_addr, port):
    # Live packet sniffing
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

        # If an address has more connections than is deemed safe flag it
        if len(connections[client_addr[0]]) > connection_limit:
            print(f'Potential DDOS attack from {client_addr[0]}')

            # Get IP address, send to an admin requested powershell script to block IP, if result.returncode = 0 then success!
            # Also when the IP is blocked, no more packets are recieved.
            temp_ip = client_addr[0]

            ps_script = f"""
                New-NetFirewallRule -DisplayName "Block {temp_ip}" -Description "Suspicious number of connections from {temp_ip} flagged it as a potential DDoS attack." -Direction Inbound -LocalPort Any -Protocol Any -Action Block -RemoteAddress {temp_ip}
                """
            ps_script_2 = f"""
                Add-Type -AssemblyName PresentationCore,PresentationFramework
                $MessageBody = "DDOS suspected from IP address:{temp_ip}. Firewall Block created."
                $MessageIcon = [System.Windows.MessageBoxImage]::Warning
                $Result = [System.Windows.MessageBox]::Show($MessageBody, $messageicon)
                """
            


            powershell_cmd = ["powershell.exe", "-Command", ps_script]

            result = subprocess.run(powershell_cmd, capture_output=True)

            powershell_cmd_2 = ["powershell.exe", "-Command", ps_script_2]

            output = subprocess.run(powershell_cmd_2, capture_output=True)
            

            

            if result.returncode == 0:
                email_alert(temp_ip)
                connections[client_addr[0]] = []
                
        client_sock.close()



        

    

detect_ddos('0.0.0.0', 80)
