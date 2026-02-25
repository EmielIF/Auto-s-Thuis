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
    df = pd.read_csv(csv_url)
    st.subheader("📊 Huidige Stand")
    st.table(df)

    # NIEUW: Eerst vragen wie er überhaupt weg gaat
    st.subheader("❓ Wie gebruikt de auto?")
    reizigers = st.multiselect("Wie gaan er morgen met de auto op pad?", df["Naam"].tolist())
    
    # Alleen als je weg gaat, kun je een vroege vogel zijn
    vroege_vogels = []
    if reizigers:
        vroege_vogels = st.multiselect("Wie van hen moet er vóór 07:30 weg?", reizigers)
    
    if is_het_slecht_weer:
        st.warning("🌧️ Weer-update: Het regent/sneeuwt. Bonuspunten (2) actief!")
    else:
        st.info("☀️ Weer-update: Het is droog. Normale punten (1) actief.")

    if st.button("⚖️ Bereken & Update"):
        # De 'kandidaten' zijn mensen die WEG gaan, maar NIET vroeg.
        kandidaten = [n for n in reizigers if n not in vroege_vogels]
        
        if not reizigers:
            st.warning("Niemand gaat weg? Dan hoeft er ook niemand te verplaatsen!")
        else:
            if not kandidaten:
                st.info("Iedereen die weg gaat is een vroege vogel of niemand is kandidaat. We loten uit de reizigers.")
                sjaak = random.choice(reizigers)
            else:
                kandidaat_df = df[df["Naam"].isin(kandidaten)]
                min_pnt = kandidaat_df["Punten"].min()
                potentiële_sjaaks = kandidaat_df[kandidaat_df["Punten"] == min_pnt]["Naam"].tolist()
                sjaak = random.choice(potentiële_sjaaks)

            pnt_erbij = 2 if is_het_slecht_weer else 1
            
            with st.spinner('Update versturen naar Google Sheets...'):
                response = requests.get(f"{script_url}?naam={sjaak}&punten={pnt_erbij}")
                
            if response.status_code == 200:
                # Sla de uitslag op in een tijdelijke 'session state' om het te tonen na de rerun
                st.session_state.laatste_sjaak = sjaak
                st.session_state.laatste_punten = pnt_erbij
                
                # Geef een melding en ververs de boel
                st.success(f"De punten zijn bijgewerkt voor {sjaak}!")
                st.balloons()
                
                # Dit is de magie: herstart het script om de tabel te vernieuwen
                st.rerun()
            else:
                st.error("Update mislukt. Controleer je Google Script URL.")

# Toon de uitslag van de laatste berekening bovenaan of onderaan als die er is
if 'laatste_sjaak' in st.session_state:
    st.divider()
    st.error(f"❌ **{st.session_state.laatste_sjaak}** moet ver weg parkeren! (+{st.session_state.laatste_punten} pnt)")
