import streamlit as st
import pandas as pd
import random
import requests

st.set_page_config(page_title="Parkeer-Planner", page_icon="🚗")
st.title("🚗 Automatische Parkeer-Planner")

# 1. URLs ophalen uit Secrets
sheet_url = st.secrets["connections"]["gsheets"]["spreadsheet"]
# Zorg dat je deze nieuwe regel toevoegt aan je Secrets (zie stap 3)
script_url = st.secrets["connections"]["gsheets"]["script_url"]

csv_url = sheet_url.replace("/edit?usp=sharing", "/export?format=csv").replace("/edit#gid=0", "/export?format=csv")

try:
    # Lees de huidige stand
    df = pd.read_csv(csv_url)
    st.subheader("📊 Huidige Stand")
    st.table(df)

    vroege_vogels = st.multiselect("Wie moet er morgen vóór 08:30 weg?", df["Naam"].tolist())
    slecht_weer = st.toggle("Het regent of is erg koud (2 punten)")

    if st.button("⚖️ Bereken & Update"):
        kandidaten = [n for n in df["Naam"].tolist() if n not in vroege_vogels]
        
        if not kandidaten:
            sjaak = random.choice(df["Naam"].tolist())
        else:
            min_pnt = df[df["Naam"].isin(kandidaten)]["Punten"].min()
            potentiële_sjaaks = df[(df["Naam"].isin(kandidaten)) & (df["Punten"] == min_pnt)]["Naam"].tolist()
            sjaak = random.choice(potentiële_sjaaks)

        pnt_erbij = 2 if slecht_weer else 1
        
        # --- DIT IS DE AUTOMATISCHE UPDATE ---
        with st.spinner('Punten worden bijgeschreven in Google Sheets...'):
            response = requests.get(f"{script_url}?naam={sjaak}&punten={pnt_erbij}")
            
        if response.status_code == 200:
            st.error(f"❌ **{sjaak}** staat vandaag ver weg!")
            st.success(f"De Google Sheet is automatisch bijgewerkt (+{pnt_erbij} pnt).")
            st.balloons()
            # Pagina even refreshen om de nieuwe tabel te zien
            st.button("Tabel vernieuwen")
        else:
            st.warning("De berekening is gelukt, maar de automatische update mislukte.")

except Exception as e:
    st.error(f"Fout bij het laden: {e}")
