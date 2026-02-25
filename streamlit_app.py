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
    st.dataframe(df, use_container_width=True, hide_index=True)

    # --- INPUT MET CHECKBOXES ---
    st.subheader("❓ Wie gebruikt de auto?")
    reizigers = []
    
    # Maak vinkjes naast elkaar voor de bewoners
    cols = st.columns(len(df["Naam"]))
    for i, naam in enumerate(df["Naam"].tolist()):
        with cols[i]:
            if st.checkbox(naam, key=f"weg_{naam}"):
                reizigers.append(naam)

    vroege_vogels = []
    if reizigers:
        st.subheader("🌅 Wie moet er vóór 08:30 weg?")
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
        if not reizigers:
            st.warning("Niemand gaat weg? Dan hoeft er ook niemand te verplaatsen!")
        else:
            kandidaten = [n for n in reizigers if n not in vroege_vogels]
            
            if not kandidaten:
                # Als iedereen vroege vogel is, loot uit alle reizigers
                sjaak = random.choice(reizigers)
            else:
                # Filter de kandidaten en zoek de laagste score
                kandidaat_df = df[df["Naam"].isin(kandidaten)]
                min_pnt = kandidaat_df["Punten"].min()
                potentiële_sjaaks = kandidaat_df[kandidaat_df["Punten"] == min_pnt]["Naam"].tolist()
                sjaak = random.choice(potentiële_sjaaks)

            pnt_erbij = 2 if is_het_slecht_weer else 1
            
            with st.spinner('Update versturen naar Google Sheets...'):
                update_url = f"{script_url}?naam={sjaak}&punten={pnt_erbij}"
                response = requests.get(update_url)
                
            if response.status_code == 200:
                st.session_state.laatste_sjaak = sjaak
                st.session_state.laatste_punten = pnt_erbij
                st.balloons()
                st.rerun()
            else:
                st.error("Update mislukt. Controleer je Google Script URL.")

    # Laat de uitslag zien na de verversing
    if 'laatste_sjaak' in st.session_state:
        st.divider()
        st.error(f"❌ **{st.session_state.laatste_sjaak}** moet ver weg parkeren! (+{st.session_state.laatste_punten} pnt)")

except Exception as e:
    st.error(f"Fout: {e}")
