import streamlit as st
import pandas as pd
import random
import requests

st.set_page_config(page_title="Parkeer-Planner", page_icon="🚗")
st.title("🚗 Slimme Parkeer-Planner")

# --- WEER AUTOMATISERING ---
def check_slecht_weer():
    try:
        url = "https://api.open-meteo.com/v1/forecast?latitude=52.0783&longitude=5.4883&current=precipitation,rain,showers,snowfall&timezone=Europe%2FAmsterdam"
        response = requests.get(url).json()
        neerslag = response['current']['precipitation'] > 0
        return neerslag
    except:
        return False

is_het_slecht_weer = check_slecht_weer()

# --- DATA OPHALEN ---
sheet_url = st.secrets["connections"]["gsheets"]["spreadsheet"]
script_url = st.secrets["connections"]["gsheets"]["script_url"]
csv_url = sheet_url.replace("/edit?usp=sharing", "/export?format=csv").replace("/edit#gid=0", "/export?format=csv")

try:
    # Lees de huidige stand
    df = pd.read_csv(csv_url)
    st.subheader("📊 Huidige Stand")
    st.dataframe(df, use_container_width=True, hide_index=True)

    # Namenlijst uit de sheet halen
    alle_namen = df["Naam"].tolist()

    # --- INPUT MET CHECKBOXES (GEEN DROPDOWN) ---
    st.subheader("❓ Wie gebruikt de auto?")
    reizigers = []
    col1, col2, col3 = st.columns(3)
    
    # Maak vinkjes voor wie er weg gaat
    with col1:
        if st.checkbox("Emiel", key="weg_emiel"): reizigers.append("Emiel")
    with col2:
        if st.checkbox("Anouk", key="weg_anouk"): reizigers.append("Anouk")
    with col3:
        if st.checkbox("Mama", key="weg_mama"): reizigers.append("Mama")

    vroege_vogels = []
    if reizigers:
        st.subheader("🌅 Wie moet er vóór 08:30 weg?")
        # Alleen vinkjes laten zien voor de mensen die ook echt weg gaan
        vroeg_cols = st.columns(len(reizigers))
        for i, naam in enumerate(reizigers):
            with vroeg_cols[i]:
                if st.checkbox(naam, key=f"vroeg_{naam}"):
                    vroege_vogels.append(naam)
    
    st.divider()

    if is_het_slecht_weer:
        st.warning("🌧️ Weer-update: Het regent/sneeuwt. Bonuspunten (2) actief!")
    else:
        st.info("☀️ Weer-update: Het is droog. Normale punten (1) actief.")

    # --- BEREKENING ---
    if st.button("⚖️ Bereken & Update"):
        kandidaten = [n for n in reizigers if n not in vroege_vogels]
        
        if not reizigers:
            st.warning("Niemand gaat weg? Dan hoeft er ook niemand te verplaatsen!")
        else:
            if
