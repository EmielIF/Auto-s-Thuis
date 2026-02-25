import streamlit as st
import random
import pandas as pd

# Titels en Styling
st.set_page_config(page_title="Parkeer-Planner", page_icon="🚗")
st.title("🚗 Wie staat er ver weg?")

# --- DATABASE SIMULATIE ---
# Voor een echte app koppel je hier Google Sheets. 
# Voor nu gebruiken we even een tijdelijke lijst.
if 'scores' not in st.session_state:
    st.session_state.scores = {"Emiel": 0, "Anouk": 0, "Mama": 0}

# Toon de tussenstand
st.subheader("📊 De Tussenstand (Punten)")
cols = st.columns(3)
for i, (naam, score) in enumerate(st.session_state.scores.items()):
    cols[i].metric(naam, f"{score} pnt")

st.divider()

# --- INPUT ---
st.subheader("📅 Planning voor morgen")
vroege_vogels = st.multiselect("Wie moet er vóór 08:30 weg?", ["Emiel", "Anouk", "Mama"])

# Weer-bonus
st.subheader("🌦️ Weer-check")
slecht_weer = st.toggle("Het regent of is erg koud (Bonuspunten!)")

if st.button("⚖️ Bereken Parkeerplek"):
    # Filter de mensen die NIET vroeg weg hoeven
    kandidaten = [n for n in ["Emiel", "Anouk", "Mama"] if n not in vroege_vogels]
    
    if not kandidaten:
        st.warning("Iedereen moet vroeg weg! We kiezen willekeurig.")
        sjaak = random.choice(["Emiel", "Anouk", "Mama"])
    else:
        # Kies de persoon met de minste punten
        min_pnt = min(st.session_state.scores[k] for k in kandidaten)
        potentiële_sjaaks = [k for k in kandidaten if st.session_state.scores[k] == min_pnt]
        sjaak = random.choice(potentiële_sjaaks)

    # Punten toekennen
    pnt_erbij = 2 if slecht_weer else 1
    st.session_state.scores[sjaak] += pnt_erbij
    
    st.error(f"❌ **{sjaak}** is de sjaak en moet ver weg staan!")
    if slecht_weer:
        st.caption(f"Je krijgt {pnt_erbij} punten omdat je door de regen moet.")
    else:
        st.caption(f"Je krijgt {pnt_erbij} punt voor deze wandeling.")
