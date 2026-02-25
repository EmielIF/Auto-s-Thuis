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
        r = requests.get(url).json()
        return r['current']['precipitation'] > 0
    except:
        return False

weer_bonus = check_slecht_weer()

# --- DATA OPHALEN ---
conf = st.secrets["connections"]["gsheets"]
csv_url = conf["spreadsheet"].replace("/edit?usp=sharing", "/export?format=csv").replace("/edit#gid=0", "/export?format=csv")

try:
    df = pd.read_csv(csv_url)
    st.subheader("📊 Stand")
    st.dataframe(df, use_container_width=True, hide_index=True)

    st.subheader("📋 Planning morgen")
    reizigers, vroege_vogels = [], []
    
    for n in df["Naam"].tolist():
        # Aangepaste volgorde van opties
        k = st.radio(
            f"Status **{n}**:", 
            ["🌅 Weg (voor 07:30)", "🚗 Weg (na 07:30)", "🏠 Ik blijf thuis"], 
            horizontal=True, 
            key=f"s_{n}"
        )
        if "Weg" in k:
            reizigers.append(n)
            # Check of het een vroege vogel is
            if "voor 07:30" in k: 
                vroege_vogels.append(n)

    st.divider()
    msg = "🌧️ Regen: 2 pnt" if weer_bonus else "☀️ Droog: 1 pnt"
    st.info(msg)

    if st.button("⚖️ Bereken & Update"):
        if not reizigers:
            st.warning("Niemand weg!")
        else:
            kand = [n for n in reizigers if n not in vroege_vogels]
            if not kand: kand = reizigers
            
            k_df = df[df["Naam"].isin(kand)]
            min_p = k_df["Punten"].min()
            sjaak_naam = random.choice(k_df[k_df["Punten"] == min_p]["Naam"].tolist())
            p = 2 if weer_bonus else 1
            
            with st.spinner('Bezig...'):
                res = requests.get(f"{conf['script_url']}?naam={sjaak_naam}&punten={p}")
                
            if res.status_code == 200:
                st.session_state.sjaak, st.session_state.p = sjaak_naam, p
                st.balloons()
                st.rerun()
            else:
                st.error("Sheet update mislukt.")

    if 'sjaak' in st.session_state:
        st.error(f"❌ **{st.session_state.sjaak}** parkeert ver weg! (+{st.session_state.p} pnt)")

except Exception as e:
    st.error(f"Fout: {e}")
