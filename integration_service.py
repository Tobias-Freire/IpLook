from scapy_service import traceroute_tcp
from geocoder_service import get_location

def get_route_info(host: str, dport: int=80) -> dict:
    data = traceroute_tcp(host, dport)
    for ttl, ip in data.items():
        if ip:
            location = get_location(ip)
            data[ttl] = {
                "ip": ip,
                "location": f"{location['city']}, {location['state']}, {location['country']}"
            }
    return data

if __name__ == "__main__":
    host = str(input("Write your desired host: "))
    route_info = get_route_info(host)
    print(route_info)
