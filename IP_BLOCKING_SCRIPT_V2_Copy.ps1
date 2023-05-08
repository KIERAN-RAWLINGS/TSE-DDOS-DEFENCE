$temp_ip = $args[0]
#$temp_ip_2 = "127.0.0.5"

New-NetFirewallRule -DisplayName "DDOS IP address - block" -Direction Inbound -LocalPort Any -Protocol TCP -Action Block -RemoteAddress $temp_ip
echo "IP BLOCKED - DONE"