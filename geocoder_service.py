import geocoder

# run = True
# while(run):
#     ip = str(input("Write your desired IP address: "))
#     if ip == "q": break
#     location = geocoder.ip(ip)
#     print(f"""
#     Cidade: {location.city}
#     Estado: {location.state}
#     País: {location.country}\n
#     """)

def get_location(ip: str) -> dict:
    location = geocoder.ip(ip)
    return {
        "city": location.city,
        "state": location.state,
        "country": location.country
    }