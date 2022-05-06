# Contemporaneous Open

This is a challenge where we need to manipulate TCP packets. When we connect to the server, we need to provide an IP to ther server, then it
can send the flag in a POST request form, it explicitly says that no SYN+ACK packets will be received to the server, so the 3-way handshake will
not be possible. But, is there another way to connect with the server using TCP ? The answer is yes! and the hint is in the challenge's name.
There is a alternative way to create a TCP connection called "TCP Simultaneous Open" (explanation [here](https://diameter-protocol.blogspot.com/2014/03/simultaneous-open-tcp-connections.html)) which consists in the two devices will
act as a server and client at the same time, and the connection is established when both responds to a special SYN packet.

So, in this challenge we need to create that kind connection first in order the server can be able to send us the flag.

I had in my pending projects, write a packet sniffer with Python, so I put my hands on this. This can be simply done with the Scapy framework
but, I prefer to do it using sockets, this way I can see and manipulate raw data.
![screenshot](https://github.com/stevenvegar/CTF-Tools/blob/main/ContemporaneousOpen.png)


## frames_sniffer.py
This script captures the ethernet frames, here we can grab the information from OSI-layer 2, which means, we can clasify frames depending on 
their [EtherType](https://en.wikipedia.org/wiki/EtherType). In this case, we will capture IPv4 only frames. The script grabs all the raw information and declare them into variables, useful 
when we need to manipulate or get a specific packet field. This script captures <ins>inbound and outbound frames</ins>, works in Linux only.
![screenshot](https://github.com/stevenvegar/CTF-Tools/blob/main/ContemporaneousOpen.png)


## packet_sniffer.py
This script is similar to the above, but this captures only TCP <ins>inbound packets</ins> and doesn't shows link layer info.
![screenshot](https://github.com/stevenvegar/CTF-Tools/blob/main/packet_sniffer.png)


### TODO:
- Add support to capture other IP packet types (UDP, ICMP, etc).
- Add filters specifing them with parameters.
- Save output to pcap file.
