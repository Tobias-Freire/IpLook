from src.scapy_service import traceroute_tcp
from ipinfo_service import get_location_from_ip

def get_route_info(host: str, dport: int=80) -> dict:
    """
    Integrates the traceroute and IPinfo services to get detailed route information.

    Args:
        host (str): The destination host for the traceroute.
        dport (int): The destination port for the TCP traceroute. Default is 80.
    Returns:
        dict: A dictionary containing the hop number (TTL) as keys and a dictionary with 
              IP address and location information as values.
    """
    data = traceroute_tcp(host, dport)
    for ttl, ip in data.items():
        if ip:
            location = get_location_from_ip(ip)
            data[ttl] = {
                "ip": ip,
                "city": location.get("city"),
                "region": location.get("region"),
                "country": location.get("country"),
                "loc": location.get("loc"),
                "provider": location.get("provider")
            }
    return data

if __name__ == "__main__":
    host = str(input("Write your desired host: "))
    route_info = get_route_info(host)
    print(route_info)
