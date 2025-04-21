import streamlit as st
from streamlit_js_eval import get_geolocation

st.title("Teste")
loc = get_geolocation()
st.write("Localização:", loc)