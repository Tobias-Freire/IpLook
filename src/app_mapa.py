import streamlit as st
import socket
import json
import folium
from streamlit_folium import st_folium
import integration_service
from streamlit_js_eval import get_geolocation

st.set_page_config(layout="centered")
st.title("📍 Rastreamento de Rota do Usuário até o Domínio")

dominio_alvo = st.text_input("Digite o domínio para rastrear a rota:")

user_location = get_geolocation()

st.write("Resultado da localização:", user_location)

if dominio_alvo:
    try:
        ip_alvo = socket.gethostbyname(dominio_alvo)
        st.info(f"Rastreando rota de sua localização até: {dominio_alvo} ({ip_alvo})")

        if user_location and user_location.get("coords"):
            coords = user_location["coords"]
            user_lat = coords.get("latitude")
            user_lon = coords.get("longitude")

            with st.spinner(f"Rastreando rotas para {dominio_alvo}..."):
                resultados = integration_service.get_route_info(dominio_alvo)
                if isinstance(resultados, dict) and "error" in resultados:
                    st.error(f"Erro ao executar o traceroute: {resultados['error']}")
                    st.stop()

                if not resultados:
                    st.error("Não foi possível rastrear a rota. O destino pode estar inacessível.")
                    st.stop()

            st.subheader(f"Rota até {dominio_alvo} ({ip_alvo})")
            st.write(resultados)

            map_points = [{
                'latitude': user_lat,
                'longitude': user_lon,
                'tipo': 'Você',
                'info': 'Sua localização'
            }]

            for hop, info in resultados.items():
                if info and info.get('loc'):
                    try:
                        lat, lon = map(float, info['loc'].split(','))
                    except (ValueError, AttributeError):
                        continue # Skip invalid locations
                    map_points.append({
                        'latitude': lat,
                        'longitude': lon,
                        'tipo': f'Hop {hop}',
                        'info': f"Hop: {hop}<br>IP: {info.get('ip')}<br>Cidade: {info.get('city')}<br>País: {info.get('country')}"
                    })

            if map_points:
                map_points.append({
                    'latitude': float(map_points[-1]['latitude']),
                    'longitude': float(map_points[-1]['longitude']),
                    'tipo': 'Destino',
                    'info': f'Destino: {dominio_alvo} ({ip_alvo})'
                })

            latitudes = [p['latitude'] for p in map_points]
            longitudes = [p['longitude'] for p in map_points]
            media_lat = sum(latitudes) / len(latitudes)
            media_lon = sum(longitudes) / len(longitudes)

            m = folium.Map(location=[media_lat, media_lon], zoom_start=4)

            for point in map_points:
                folium.Marker(
                    [point['latitude'], point['longitude']],
                    popup=point['info'],
                    tooltip=point['tipo'],
                    icon=folium.Icon(
                        color='red' if point['tipo'] == 'Você' else
                        'green' if point['tipo'] == 'Destino' else 'blue'
                    )
                ).add_to(m)

            st_folium(m, width=700, height=500)
        else:
            st.warning("Não foi possível obter sua localização. Verifique permissões do navegador.")
    except socket.gaierror:
        st.error(f"Domínio inválido: {dominio_alvo}")
else:
    st.info("Digite um domínio para começar.")