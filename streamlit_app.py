import streamlit as st
from streamlit_gsheets import GSheetsConnection
import random

st.set_page_config(page_title="Parkeer-Planner", page_icon="🚗")
st.title("🚗 Wie staat er ver weg?")

# Verbinding maken met Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

# Punten inlezen uit de Sheet
df = conn.read(worksheet="Blad1") # Of de naam van jouw tabblad

st.subheader("📊 De Tussenstand")
st.table(df)

vroege_vogels = st.multiselect("Wie moet er morgen vóór 08:30 weg?", df["Naam"].tolist())
slecht_weer = st.toggle("Het regent of is erg koud (2 punten)")

if st.button("⚖️ Bereken Parkeerplek"):
    kandidaten = [n for n in df["Naam"].tolist() if n not in vroege_vogels]
    
    if not kandidaten:
        st.warning("Iedereen moet vroeg weg! We kiezen willekeurig.")
        sjaak = random.choice(df["Naam"].tolist())
    else:
        # Zoek de persoon met de minste punten in de dataframe
        kandidaat_df = df[df["Naam"].isin(kandidaten)]
        min_pnt = kandidaat_df["Punten"].min()
        potentiële_sjaaks = kandidaat_df[kandidaat_df["Punten"] == min_pnt]["Naam"].tolist()
        sjaak = random.choice(potentiële_sjaaks)

    # Punten updaten in de dataframe
    pnt_erbij = 2 if slecht_weer else 1
    df.loc[df["Naam"] == sjaak, "Punten"] += pnt_erbij
    
    # De nieuwe stand terugschrijven naar de Google Sheet
    conn.update(worksheet="Blad1", data=df)
    
    st.error(f"❌ **{sjaak}** moet ver weg staan!")
    st.balloons()
