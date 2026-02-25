import streamlit as st
import pandas as pd
import random

# Pagina instellingen
st.set_page_config(page_title="Parkeer-Planner", page_icon="🚗")
st.title("🚗 Wie staat er ver weg?")

# 1. Haal de URL uit de Secrets
# We bouwen de URL om naar een directe CSV-export link
sheet_url = st.secrets["connections"]["gsheets"]["spreadsheet"]
csv_url = sheet_url.replace("/edit?usp=sharing", "/export?format=csv")
csv_url = csv_url.replace("/edit#gid=0", "/export?format=csv")

# 2. Lees de data in
try:
    df = pd.read_csv(csv_url)
    
    st.subheader("📊 De Tussenstand")
    st.table(df)

    # Input van de gebruikers
    vroege_vogels = st.multiselect("Wie moet er morgen vóór 08:30 weg?", df["Naam"].tolist())
    slecht_weer = st.toggle("Het regent of is erg koud (2 punten)")

    if st.button("⚖️ Bereken Parkeerplek"):
        kandidaten = [n for n in df["Naam"].tolist() if n not in vroege_vogels]
        
        if not kandidaten:
            st.warning("Iedereen moet vroeg weg! We kiezen willekeurig.")
            sjaak = random.choice(df["Naam"].tolist())
        else:
            # Filter de kandidaten en zoek de laagste score
            kandidaat_df = df[df["Naam"].isin(kandidaten)]
            min_pnt = kandidaat_df["Punten"].min()
            potentiële_sjaaks = kandidaat_df[kandidaat_df["Punten"] == min_pnt]["Naam"].tolist()
            sjaak = random.choice(potentiële_sjaaks)

        # Punten toekennen
        pnt_erbij = 2 if slecht_weer else 1
        
        st.error(f"❌ **{sjaak}** moet ver weg staan!")
        st.info(f"Open de Google Sheet om {pnt_erbij} punt(en) bij de score van {sjaak} op te tellen.")
        st.balloons()
        
        # Link naar de sheet zodat je het makkelijk handmatig kunt doen
        st.markdown(f"[Klik hier om de score in de Google Sheet aan te passen]({sheet_url})")

except Exception as e:
    st.error("Er gaat iets mis bij het ophalen van de Sheet.")
    st.write(f"Foutmelding: {e}")
