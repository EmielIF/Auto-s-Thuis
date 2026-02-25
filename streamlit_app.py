import streamlit as st
import pandas as pd
import random
import requests

st.set_page_config(page_title="Parkeer-Planner", page_icon="🚗")
st.title("🚗 Slimme Parkeer-Planner")

# --- WEER AUTOMATISERING ---
def check_slecht_weer():
    try:
        url = "https://api.open-meteo.com/v1/forecast?latitude=52.0783&longitude=5.4883&current=precipitation&timezone=Europe%2FAmsterdam"
        response = requests.get(url).json()
        return response['current']['precipitation'] > 0
    except:
        return False

is_het_slecht_weer = check_slecht_weer()

# --- DATA OPHALEN ---
sheet_url = st.secrets["connections"]["gsheets"]["spreadsheet"]
script_url = st.secrets["connections"]["gsheets"]["script_url"]
csv_url = sheet_url.replace("/edit?usp=sharing", "/export?format=csv").replace("/edit#gid=0", "/export?format=csv")

try:
    df = pd.read_csv(csv_url)
    st.subheader("📊 Huidige Stand")
    st.dataframe(df, use_container_width=True, hide_index=True)

    st.subheader("📋 Wie gaat wanneer weg?")
    reizigers = []
    vroege_vogels = []
    
    for naam in df["Naam"].tolist():
        keuze = st.radio(
            f"Status voor **{naam}**:",
            ["🏠 Thuis", "🚗 Weg (> 07:30)", "🌅 Weg (< 07:30)"],
            horizontal=True,
            key=f"status_{naam}"
        )
        if "Weg" in keuze:
            reizigers.append(naam)
            if "< 07:30" in keuze:
                vroege_vogels.append(naam)

    st.divider()

    if is_het_slecht_weer:
        st.warning("🌧️ Weer:
