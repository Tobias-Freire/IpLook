import streamlit as st
import socket
import folium
from streamlit_folium import st_folium
import integration_service
from streamlit_js_eval import get_geolocation

st.set_page_config(layout="centered")
st.title("📍 User Route Tracking to Domain")

if "last_processed_domain" not in st.session_state:
    st.session_state.last_processed_domain = None
    st.session_state.route_info = None
    st.session_state.target_ip = None
    st.session_state.user_location = None

def get_user_location():
    """Obtains and stores the user's location"""
    with st.spinner("Getting your location..."):
        location = get_geolocation()
        if location and location.get("coords"):
            st.session_state.user_location = location
            return True
    st.warning("Could not obtain your location.")
    return False

def process_domain(domain):
    """Processes the target domain and obtains route information"""
    try:
        ip_alvo = socket.gethostbyname(domain)
        st.session_state.target_ip = ip_alvo
        st.session_state.route_info = integration_service.get_route_info(domain)
        return True
    except socket.gaierror:
        st.error(f"Invalid domain: {domain}")
        return False

def create_map(user_coords, route_info, target_domain):
    """Creates the map with the correctly traced route"""
    map_points = [{
        'latitude': user_coords['latitude'],
        'longitude': user_coords['longitude'],
        'tipo': 'You',
        'info': 'Your location',
        'order': 0  
    }]

    for hop, info in sorted(route_info.items(), key=lambda x: x[0]):
        if info:
            hop_data = {
                'latitude': None,
                'longitude': None,
                'tipo': f'Hop {hop}',
                'info': f"Hop: {hop}<br>IP: {info.get('ip')}<br>City: {info.get('city')}<br>Region: {info.get('region')}<br>Country: {info.get('country')}<br>Provider: {info.get('provider')}<br>Location: {info.get('loc')}",
                'order': hop,  
                'is_last': hop == max(route_info.keys())  
            }
            if info.get('loc'):
                try:
                    lat, lon = map(float, info['loc'].split(','))
                    hop_data['latitude'] = lat
                    hop_data['longitude'] = lon
                except (ValueError, AttributeError):
                    pass
            map_points.append(hop_data)

    valid_points = sorted(
        [p for p in map_points if p['latitude'] is not None and p['longitude'] is not None],
        key=lambda x: x['order']
    )
    
    if len(valid_points) < 2:
        st.warning("There are not enough points with valid location to trace the route.")
        return None

    media_lat = sum(p['latitude'] for p in valid_points) / len(valid_points)
    media_lon = sum(p['longitude'] for p in valid_points) / len(valid_points)

    m = folium.Map(location=[media_lat, media_lon], zoom_start=4)

    for point in valid_points:
        if point['tipo'] == 'You':
            icon_color = 'red'  # Your location
        elif point.get('is_last'):
            icon_color = 'blue'  # Final destination
        else:
            icon_color = 'green'  # Intermediate hops
        
        folium.Marker(
            [point['latitude'], point['longitude']],
            popup=point['info'],
            tooltip=f"{point['tipo']} - {target_domain}" if point.get('is_last') else point['tipo'],
            icon=folium.Icon(
                color=icon_color,
                icon='server' if point.get('is_last') else 'info-sign',
                prefix='fa' if point.get('is_last') else None  
            )
        ).add_to(m)

    folium.PolyLine(
        [(p['latitude'], p['longitude']) for p in valid_points],
        color="blue",
        weight=2.5,
        opacity=1,
        tooltip=f"Rota para {target_domain}"
    ).add_to(m)
    
    return m

container = st.container()
with container:
    dominio_alvo = st.text_input("Enter the domain to track the route:")

if not st.session_state.user_location:
    if not get_user_location():
        st.stop()
with st.expander("User Location"):
    st.write(st.session_state.user_location)

if dominio_alvo and dominio_alvo != st.session_state.last_processed_domain:
    st.session_state.last_processed_domain = dominio_alvo
    if process_domain(dominio_alvo):
        st.rerun()
    else:
        st.stop()

if dominio_alvo and st.session_state.route_info and st.session_state.user_location:
    coords = st.session_state.user_location["coords"]
    st.info(f"Tracking route from your location to: {dominio_alvo} ({st.session_state.target_ip})")
    
    with st.expander("Tracking result details"):
        st.write(st.session_state.route_info)

    mapa = create_map(
        {'latitude': coords.get('latitude'), 'longitude': coords.get('longitude')},
        st.session_state.route_info,
        dominio_alvo
    )
    
    if mapa:
        st_folium(mapa, width=700, height=500)
else:
    st.info("Enter a valid domain to start tracking.")