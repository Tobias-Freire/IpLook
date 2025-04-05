"""
This module contains the implementation of a simple TCP traceroute using Scapy.

Given a host (hostname), a destination port (default is 80 for HTTP), 
and a maximum number of hops (default is 30), the function returns a dictionary 
containing the IP address of each router or server the packet passes through.

How does it work?

A packet in Scapy can encapsulate multiple protocol layers into a single packet.
In this case, we build an IP packet (which contains information such as the destination 
host and the TTL value) and a TCP segment (which contains the destination port and the 
SYN flag — used to initiate a connection). These layers are combined using 
`IP(dst=host, ttl=ttl) / TCP(dport=dport, flags="S")`. Note: this is not a division, 
but rather a composition of layers.

The packet is then sent using `sr1(pkt, verbose=False, timeout=1)`, which transmits the packet 
and waits up to 1 second for a single response.

If no reply is received, the dictionary stores `None` for that hop. If a reply is received, 
the source IP address (`reply.src`) is added to the dictionary.

If the reply comes from a TCP layer and has the flags set to 0x12 (SYN-ACK), it indicates 
that the destination host has been reached and is acknowledging the connection.
"""


from scapy.all import IP, TCP, sr1

def traceroute_tcp(host, dport=80, max_hops=30) -> dict:
    data = {}
    for ttl in range(1, max_hops + 1):
        pkt = IP(dst=host, ttl=ttl) / TCP(dport=dport, flags="S")
        reply = sr1(pkt, verbose=False, timeout=1)

        if reply is None:
            data[ttl] = None
        else:
            data[ttl] = reply.src

        if reply and reply.haslayer(TCP) and reply[TCP].flags == 0x12:  # SYN-ACK 
            return data


