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

        if reply and reply.haslayer(TCP) and reply[TCP].flags == 0x12:  # SYN-ACK recebido
            return data


