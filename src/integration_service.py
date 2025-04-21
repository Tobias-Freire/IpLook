import subprocess
import json
from ipinfo_service import get_location_from_ip

def get_route_info(host: str, dport: int=80) -> dict:
    try:
        cmd = ["./venv/bin/python", "src/traceroute_runner.py", host, str(dport)]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        data = json.loads(result.stdout)

        route_info = {}
        for hop, ip in data.items():
            hop = int(hop)
            if ip is not None:
                location_info = get_location_from_ip(ip)
                route_info[hop] = {
                    "ip": ip,
                    "city": location_info.get("city"),
                    "country": location_info.get("country"),
                    "loc": location_info.get("loc")
                }
            else:
                route_info[hop] = None

        return route_info
    except Exception as e:
        return {"error": str(e)}
