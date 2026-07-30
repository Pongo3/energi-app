import streamlit as st
import requests
import pandas as pd
from datetime import datetime

# Sätt sidans layout
st.set_page_config(page_title="EnergyIQ - Energianalys & Kalkylator", page_icon="⚡", layout="wide")

st.title("⚡ EnergyIQ – Digitalt Energiverktyg")
st.caption("Beslutsunderlag för solceller, batterilagring och elprisoptimering")

# Skapa två flikar
tab1, tab2 = st.tabs(["📊 Live Elpriser", "☀️ Solceller & Batterilagring"])

# ==========================================
# FLIK 1: LIVE ELPRISER
# ==========================================
with tab1:
    st.header("Dagsaktuella Elpriser (Nord Pool API)")
    
    col_sel, _ = st.columns([1, 2])
    with col_sel:
        elomrade = st.selectbox("Välj elområde:", ["SE1 (Luleå)", "SE2 (Sundsvall)", "SE3 (Stockholm)", "SE4 (Malmö)"])
        zon = elomrade.split(" ")[0]

    today = datetime.now()
    url = f"https://www.elprisetjustnu.se/api/v1/prices/{today.strftime('%Y')}/{today.strftime('%m-%d')}_{zon}.json"

    @st.cache_data(ttl=3600)
    def hamta_elpriser(api_url):
        res = requests.get(api_url)
        return res.json() if res.status_code == 200 else None

    data = hamta_elpriser(url)

    if data:
        df = pd.DataFrame(data)
        df['SEK_per_kWh'] = df['SEK_per_kWh'].round(2)
        df['Timme'] = pd.to_datetime(df['time_start']).dt.strftime('%H:00')

        snitt_pris = df['SEK_per_kWh'].mean()
        max_pris = df['SEK_per_kWh'].max()
        min_pris = df['SEK_per_kWh'].min()

        c1, c2, c3 = st.columns(3)
        c1.metric("Medelpris idag", f"{snitt_pris:.2f} kr/kWh")
        c2.metric("Högsta timpris", f"{max_pris:.2f} kr/kWh")
        c3.metric("Lägsta timpris", f"{min_pris:.2f} kr/kWh")

        st.subheader("Elprisets variation idag")
        st.line_chart(data=df, x='Timme', y='SEK_per_kWh')
    else:
        st.error("Kunde inte hämta elprisdata just nu.")

# ==========================================
# FLIK 2: SOLCELLER & BATTERIKALKYLATOR
# ==========================================
with tab2:
    st.header("☀️ Investeringskalkylator för Solceller & Batteri")
    st.write("Beräkna din uppskattade årliga besparing och återbetalningstid.")

    col_in1, col_in2 = st.columns(2)

    with col_in1:
        st.subheader("1. Solcellsanläggning")
        effekt_kw = st.number_input("Installerad effekt solceller (kWp):", min_value=1.0, max_value=100.0, value=10.0, step=0.5)
        kostnad_sol = st.number_input("Investeringskostnad solceller efter grön teknik (kr):", value=100000, step=5000)
        egenanvandning_pct = st.slider("Andel egenanvänd el (%):", 20, 80, 40)

    with col_in2:
        st.subheader("2. Batterilagring & Elpris")
        har_batteri = st.checkbox("Lägg till batterilagring i kalkylen", value=True)
        
        if har_batteri:
            batteri_kwh = st.number_input("Batterikapacitet (kWh):", min_value=1.0, max_value=50.0, value=10.0, step=1.0)
            kostnad_batteri = st.number_input("Investeringskostnad batteri efter grön teknik (kr):", value=50000, step=5000)
        else:
            batteri_kwh = 0
            kostnad_batteri = 0

        elpris_snitt = st.number_input("Uppskattat framtida elpris inkl. nät/skatt (kr/kWh):", value=1.8, step=0.1)

    # Logik & Beräkningar
    # Schablon: 1 kWp ger ca 950 kWh/år i Sverige
    produktion_ar = effekt_kw * 950  
    
    # Egenanvänd solenergi vs såld el
    egen_sol = produktion_ar * (egenanvandning_pct / 100)
    sold_sol = produktion_ar - egen_sol

    # Besparing solceller (minskad köpt el + ersättning för såld el)
    besparing_sol = (egen_sol * elpris_snitt) + (sold_sol * 0.50) # Schablon 50 öre för såld el

    # Besparing batteri (arbitrage/toppkapning): Schablon ca 300 cykler/år x kapacitet x prisskillnad
    besparing_batteri = (batteri_kwh * 300 * 1.20) if har_batteri else 0

    total_besparing_ar = besparing_sol + besparing_batteri
    total_investering = kostnad_sol + kostnad_batteri

    payback_ar = total_investering / total_besparing_ar if total_besparing_ar > 0 else 0

    st.divider()
    st.subheader("📈 Resultat & Återbetalningstid")

    res1, res2, res3, res4 = st.columns(4)
    res1.metric("Uppskattad produktion", f"{produktion_ar:,.0f} kWh/år")
    res2.metric("Total årlig besparing", f"{total_besparing_ar:,.0f} kr/år")
    res3.metric("Total investering", f"{total_investering:,.0f} kr")
    res4.metric("Återbetalningstid (Payback)", f"{payback_ar:.1f} år")

    # Visualisera ackumulerat kassaflöde över 15 år
    st.subheader("Kassaflöde över 15 år (Investering vs Besparing)")
    
    years = list(range(0, 16))
    cashflow = [-total_investering + (yr * total_besparing_ar) for yr in years]
    df_cf = pd.DataFrame({"År": years, "Netto Kassaflöde (kr)": cashflow})

    st.line_chart(df_cf, x="År", y="Netto Kassaflöde (kr)")
    