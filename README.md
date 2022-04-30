# CTF-Tools
My own developed tools used in CTF competitions

## packet_sniffer.py
Python script for packet "capture" (only show packets in terminal). Works in Linux only.

During Nahamcon CTF 2022, a challenge requires to capture data within a POST request
but, when a public IP address is provided to the server, the TCP three-way handshake
is not completed, the SYN+ACK packet from the server is not sended. With this tool
I'll try to capture the first SYN packet from the server and the SYN+ACK packet from
the client to craft an spoofed SYN+ACK packet from the server to fool the client and
permit the connection.
![screenshot](https://github.com/stevenvegar/CTF-Tools/blob/main/ContemporaneousOpen.png)

### Usage:
 sudo python3 packet_sniffer.py
 
![screenshot](https://github.com/stevenvegar/CTF-Tools/blob/main/packet_sniffer.png)


### TODO:
- Add support to capture other IP packet types (UDP, ICMP, etc).
- Add filters specifing them with parameters.
- Save output to pcap file.
