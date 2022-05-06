# Contemporaneous Open

This is a challenge where we need to manipulate TCP packets. When we connect to the server, we need to provide an IP to ther server, then it
can send the flag in a POST request form, it explicitly says that no SYN+ACK packets will be received to the server, so the 3-way handshake will
not be possible. But, is there another way to connect with the server using TCP ? The answer is yes! and the hint is in the challenge's name.
There is a alternative way to create a TCP connection called "TCP Simultaneous Open" (explanation [here](https://diameter-protocol.blogspot.com/2014/03/simultaneous-open-tcp-connections.html)) which consists in the two devices will
act as a server and client at the same time, and the connection is established when both responds to a special SYN packet.

So, in this challenge we need to create that kind connection first in order the server can be able to send us the flag.

I had in my pending projects, write a packet sniffer with Python, so I put my hands on this. This can be simply done with the Scapy framework
but, I prefer to do it using sockets, this way I can see and manipulate raw data.
![screenshot](https://github.com/stevenvegar/CTF-Tools/blob/main/NahamCon22/ContemporaneousOpen/ContemporaneousOpen.png)


## [frame_sniffer.py](https://github.com/stevenvegar/CTF-Tools/blob/main/NahamCon22/ContemporaneousOpen/frame_sniffer.py)
This script captures the ethernet frames, here we can grab the information from OSI-layer 2, which means, we can clasify frames depending on 
their [EtherType](https://en.wikipedia.org/wiki/EtherType). In this case, we will capture IPv4 only frames. The script grabs all the raw information and declare them into variables, useful 
when we need to manipulate or get a specific packet field. This script captures <ins>inbound and outbound frames</ins>, works in Linux only.
```bash
└──╼ $sudo python3 frame_sniffer.py 
SourceMAC:08:00:27:xx:xx:xx  DestinationMAC:e4:8d:8c:xx:xx:xx  Protocol:8
Version:4  Protocol:TCP(6)  DSCP:0  ID:23257  Offset:0x4000  TTL:64
TotalLength:412  IPHeadLength:20  Checksum:0xcfdc  TCPHeadLength:32  Checksum:0x1035
SrcAddress:192.168.XX.XX  SrcPort:36880  DstAddress:23.239.29.5  DstPort:80
SeqNum:54073446  AckNum:2448585548  Flags:PSH+ACK  WindowSize:501  Pointer:0
Data: 360
GET / HTTP/1.1
Host: openspeedtest.com
User-Agent: Mozilla/5.0 (Windows NT 10.0; rv:91.0) Gecko/20100101 Firefox/91.0
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8
Accept-Language: en-US,en;q=0.5
Accept-Encoding: gzip, deflate
DNT: 1
Connection: keep-alive
Upgrade-Insecure-Requests: 1
Cache-Control: max-age=0

-------------------------------------------------------------------------------------

SourceMAC:e4:8d:8c:xx:xx:xx  DestinationMAC:08:00:27:xx:xx:xx  Protocol:8
Version:4  Protocol:TCP(6)  DSCP:0  ID:52906  Offset:0x4000  TTL:51
TotalLength:52  IPHeadLength:20  Checksum:0x6a73  TCPHeadLength:32  Checksum:0x5d9c
SrcAddress:23.239.29.5  SrcPort:80  DstAddress:192.168.XX.XX  DstPort:36880
SeqNum:2448585548  AckNum:54073806  Flags:ACK  WindowSize:505  Pointer:0
Data: 0

-------------------------------------------------------------------------------------
```

## [packet_sniffer.py](https://github.com/stevenvegar/CTF-Tools/blob/main/NahamCon22/ContemporaneousOpen/packet_sniffer.py)
This script is similar to the above, but this captures only TCP <ins>inbound packets</ins> and doesn't shows link layer info.
```bash
```

### TODO:
- Add support to capture other IP packet types (UDP, ICMP, etc).
- Add filters specifing them with parameters.
- Save output to pcap file.


## Solving the challenge






















