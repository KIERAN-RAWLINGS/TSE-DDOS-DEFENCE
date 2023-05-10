
New-NetFirewallRule -DisplayName «DDOS IP address - block» -Direction Inbound –LocalPort Any -Protocol Any -Action Block -RemoteAddress $ip
echo "IP BLOCKED - DONE"
