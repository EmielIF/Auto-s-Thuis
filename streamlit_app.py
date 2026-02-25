import streamlit as st
import pandas as pd
import random
import requests

# We gebruiken een link naar een echt plaatje (PNG) in plaats van een emoji
st.set_page_config(
    page_title="Parkeer-Planner", 
    page_icon="https://www.iconpacks.net/icons/2/free-parking-sign-icon-1641-thumb.png"
)

st.set_page_config(page_title="Parkeer-Planner", page_icon="🚗")
st.title("🚗 Slimme Parkeer-Planner")

# --- WEER AUTOMATISERING ---
def check_slecht_weer():
    try:
        url = "https://api.open-meteo.com/v1/forecast?latitude=52.0783&longitude=5.4883&current=precipitation&timezone=Europe%2FAmsterdam"
        r = requests.get(url).json()
        return r['current']['precipitation'] > 0
    except:
        return False

weer_bonus = check_slecht_weer()

# --- DATA OPHALEN ---
conf = st.secrets["connections"]["gsheets"]
csv_url = conf["spreadsheet"].replace("/edit?usp=sharing", "/export?format=csv").replace("/edit#gid=0", "/export?format=csv")
##
try:
    # We voegen 'decimal=","' toe zodat Python begrijpt dat 0,5 een getal is
    df = pd.read_csv(csv_url, decimal=",")
    
    # Voor de zekerheid dwingen we de kolom 'Punten' naar getallen (floats)
    df["Punten"] = pd.to_numeric(df["Punten"], errors='coerce').fillna(0)

    st.subheader("📊 Relatieve Stand")
    st.dataframe(
        df, 
        use_container_width=True, 
        hide_index=True,
        column_config={
            "Punten": st.column_config.NumberColumn(
                "Punten",
                format="%.1f", # Toon altijd 1 cijfer achter de komma
            )
        }
    )
##
    st.subheader("📋 Planning morgen")
    reizigers, vroege_vogels = [], []
    
    for n in df["Naam"].tolist():
        k = st.radio(f"Status **{n}**:", ["🌅 Weg (voor 07:30)", "🚗 Weg (na 07:30)", "🏠 Ik blijf thuis"], horizontal=True, key=f"s_{n}")
        if "Weg" in k:
            reizigers.append(n)
            if "voor 07:30" in k:
                vroege_vogels.append(n)

    st.divider()
    p_beurt = 2 if weer_bonus else 1
    woord = "punten" if p_beurt > 1 else "punt"
    weer_tekst = "🌧️ Regen" if weer_bonus else "☀️ Droog"
    st.info(f"{weer_tekst}: deze beurt is {p_beurt} {woord}.")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("⚖️ Bereken & Update", use_container_width=True):
            if not reizigers:
                st.warning("Niemand weg!")
            else:
                kand = [n for n in reizigers if n not in vroege_vogels]
                if not kand:
                    kand = reizigers
                k_df = df[df["Naam"].isin(kand)]
                min_p = k_df["Punten"].min()
                sjaak = random.choice(k_df[k_df["Punten"] == min_p]["Naam"].tolist())
                
                with st.spinner('Updaten...'):
                    res = requests.get(f"{conf['script_url']}?naam={sjaak}&punten={p_beurt}")
                if res.status_code == 200:
                    st.session_state.sjaak, st.session_state.p = sjaak, p_beurt
                    st.rerun()

    with col2:
        vrijwilliger = st.selectbox("Vrijwillig de auto verplaatsen?", ["Kies naam..."] + df["Naam"].tolist())
        if vrijwilliger != "Kies naam...":
            if st.button(f"Bevestig verplaatsing {vrijwilliger}", use_container_width=True):
                with st.spinner('Verwerken...'):
                    # 0.5 punt bonus
                    res = requests.get(f"{conf['script_url']}?naam={vrijwilliger}&punten=0.5")
                if res.status_code == 200:
                    st.success(f"Top! {vrijwilliger} krijgt 0.5 punt.")
                    st.rerun()

    if 'sjaak' in st.session_state:
        st.error(f"❌ **{st.session_state.sjaak}** parkeert ver weg! (+{st.session_state.p} pnt)")

except Exception as e:
    st.error(f"Fout: {e}")
