import streamlit as st
import socket
import folium
from streamlit_folium import st_folium
import integration_service
from streamlit_js_eval import get_geolocation

# Configuração inicial
st.set_page_config(layout="centered")
st.title("📍 Rastreamento de Rota do Usuário até o Domínio")

# Estado inicial da sessão
if "last_processed_domain" not in st.session_state:
    st.session_state.last_processed_domain = None
    st.session_state.route_info = None
    st.session_state.target_ip = None
    st.session_state.user_location = None

def get_user_location():
    """Obtém e armazena a localização do usuário"""
    with st.spinner("Obtendo sua localização..."):
        location = get_geolocation()
        if location and location.get("coords"):
            st.session_state.user_location = location
            return True
    st.warning("Não foi possível obter sua localização.")
    return False

def process_domain(domain):
    """Processa o domínio alvo e obtém informações de rota"""
    try:
        ip_alvo = socket.gethostbyname(domain)
        st.session_state.target_ip = ip_alvo
        st.session_state.route_info = integration_service.get_route_info(domain)
        return True
    except socket.gaierror:
        st.error(f"Domínio inválido: {domain}")
        return False

def create_map(user_coords, route_info, target_domain):
    """Cria o mapa com a rota traçada corretamente"""
    # Prepara pontos do mapa começando com a localização do usuário
    map_points = [{
        'latitude': user_coords['latitude'],
        'longitude': user_coords['longitude'],
        'tipo': 'Você',
        'info': 'Sua localização',
        'order': 0  # Mantém a ordem original
    }]
    
    # Adiciona todos os hops com suas informações
    for hop, info in sorted(route_info.items(), key=lambda x: x[0]):
        if info:
            hop_data = {
                'latitude': None,
                'longitude': None,
                'tipo': f'Hop {hop}',
                'info': f"Hop: {hop}<br>IP: {info.get('ip')}<br>Cidade: {info.get('city')}<br>Estado: {info.get('region')}<br>País: {info.get('country')}<br>Provedor: {info.get('provider')}<br>Localização: {info.get('loc')}",
                'order': hop,  # Mantém a ordem original dos hops
                'is_last': hop == max(route_info.keys())  # Marca o último hop
            }
            if info.get('loc'):
                try:
                    lat, lon = map(float, info['loc'].split(','))
                    hop_data['latitude'] = lat
                    hop_data['longitude'] = lon
                except (ValueError, AttributeError):
                    pass
            map_points.append(hop_data)
    
    # Filtra apenas pontos com localização válida, mantendo a ordem original
    valid_points = sorted(
        [p for p in map_points if p['latitude'] is not None and p['longitude'] is not None],
        key=lambda x: x['order']
    )
    
    if len(valid_points) < 2:
        st.warning("Não há pontos suficientes com localização válida para traçar a rota.")
        return None
    
    # Calcula o centro do mapa
    media_lat = sum(p['latitude'] for p in valid_points) / len(valid_points)
    media_lon = sum(p['longitude'] for p in valid_points) / len(valid_points)
    
    # Cria o mapa
    m = folium.Map(location=[media_lat, media_lon], zoom_start=4)
    
    # Adiciona marcadores com cores diferentes
    for point in valid_points:
        # Determina a cor do ícone
        if point['tipo'] == 'Você':
            icon_color = 'red'  # Sua localização
        elif point.get('is_last'):
            icon_color = 'blue'  # Destino final
        else:
            icon_color = 'green'  # Hops intermediários
        
        folium.Marker(
            [point['latitude'], point['longitude']],
            popup=point['info'],
            tooltip=f"{point['tipo']} - {target_domain}" if point.get('is_last') else point['tipo'],
            icon=folium.Icon(
                color=icon_color,
                icon='server' if point.get('is_last') else 'info-sign',
                prefix='fa' if point.get('is_last') else None  # Usa Font Awesome para o ícone de destino
            )
        ).add_to(m)
    
    # Conecta os pontos na ordem correta
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
    dominio_alvo = st.text_input("Digite o domínio para rastrear a rota:")

# Obtém localização do usuário se ainda não tiver
if not st.session_state.user_location:
    if not get_user_location():
        st.stop()
with st.expander("Localização do Usuário"):
    st.write(st.session_state.user_location)

# Processa domínio apenas se for novo
if dominio_alvo and dominio_alvo != st.session_state.last_processed_domain:
    st.session_state.last_processed_domain = dominio_alvo
    if process_domain(dominio_alvo):
        st.rerun()
    else:
        st.stop()

# Exibe informações se disponíveis
if dominio_alvo and st.session_state.route_info and st.session_state.user_location:
    coords = st.session_state.user_location["coords"]
    st.info(f"Rastreando rota de sua localização até: {dominio_alvo} ({st.session_state.target_ip})")
    
    with st.expander("Detalhes do resultado do rastreamento"):
        st.write(st.session_state.route_info)
    
    # Cria e exibe o mapa
    mapa = create_map(
        {'latitude': coords.get('latitude'), 'longitude': coords.get('longitude')},
        st.session_state.route_info,
        dominio_alvo
    )
    
    if mapa:
        st_folium(mapa, width=700, height=500)
else:
    st.info("Digite um domínio válido para começar o rastreamento.")