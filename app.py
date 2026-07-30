import streamlit as st
import requests
import pandas as pd
from datetime import datetime

# Sidkonfiguration
st.set_page_config(
    page_title="EnergyIQ | Digital Energianalys & Klimatberäkning",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Kartläggning från Städer till Elområden
STAD_TILL_ELOMRADE = {
    # SE1
    "Luleå": "SE1", "Kiruna": "SE1", "Gällivare": "SE1", "Boden": "SE1", "Piteå": "SE1", 
    "Skellefteå": "SE1", "Jokkmokk": "SE1", "Haparanda": "SE1", "Kalix": "SE1",
    # SE2
    "Sundsvall": "SE2", "Umeå": "SE2", "Östersund": "SE2", "Gävle": "SE2", "Härnösand": "SE2", 
    "Örnsköldsvik": "SE2", "Hudiksvall": "SE2", "Söderhamn": "SE2", "Åre": "SE2",
    # SE3
    "Stockholm": "SE3", "Göteborg": "SE3", "Uppsala": "SE3", "Västerås": "SE3", "Örebro": "SE3", 
    "Linköping": "SE3", "Norrköping": "SE3", "Jönköping": "SE3", "Karlstad": "SE3", "Borås": "SE3", 
    "Eskilstuna": "SE3", "Halmstad": "SE3", "Trollhättan": "SE3", "Skövde": "SE3", "Nyköping": "SE3",
    # SE4
    "Malmö": "SE4", "Helsingborg": "SE4", "Lund": "SE4", "Kristianstad": "SE4", "Växjö": "SE4", 
    "Karlskrona": "SE4", "Kalmar": "SE4", "Ystad": "SE4", "Hässleholm": "SE4"
}

ZON_KOORDINATER = {
    "SE1": {"lat": 66.0, "lon": 19.0, "namn": "SE1 (Norra Sverige)"},
    "SE2": {"lat": 63.0, "lon": 16.5, "namn": "SE2 (Norra Mellansverige)"},
    "SE3": {"lat": 59.3, "lon": 15.0, "namn": "SE3 (Södra Mellansverige)"},
    "SE4": {"lat": 56.5, "lon": 13.8, "namn": "SE4 (Södra Sverige)"}
}

# CSS Styling
st.markdown("""
    <style>
    .main { background-color: #f8fafc; }
    
    .main-header {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        padding: 2.2rem 2rem;
        border-radius: 16px;
        color: #ffffff;
        margin-bottom: 2rem;
        box-shadow: 0 10px 25px -5px rgba(15, 23, 42, 0.15);
    }
    
    .main-header h1 { color: #ffffff !important; font-weight: 800; font-size: 2.2rem; margin-bottom: 0.4rem; }
    .main-header p { color: #94a3b8; font-size: 1.05rem; margin: 0; }
    
    .metric-card {
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 1.25rem 1.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.02);
        margin-bottom: 1rem;
    }
    
    .metric-label { font-size: 0.85rem; font-weight: 600; color: #64748b; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.35rem; }
    .metric-value { font-size: 1.8rem; font-weight: 800; color: #0f172a; }
    .metric-subtext { font-size: 0.8rem; color: #64748b; font-weight: 500; margin-top: 0.25rem; }

    .stTabs [data-baseweb="tab-list"] { gap: 8px; border-bottom: 2px solid #e2e8f0; padding-bottom: 4px; }
    .stTabs [data-baseweb="tab"] { height: 48px; border-radius: 8px; padding: 0px 20px; font-weight: 600; color: #64748b; }
    .stTabs [aria-selected="true"] { background-color: #3b82f6 !important; color: #ffffff !important; }

    .info-box {
        background-color: #eff6ff;
        border-left: 4px solid #3b82f6;
        padding: 1rem 1.25rem;
        border-radius: 0 8px 8px 0;
        margin: 1.5rem 0;
        color: #1e40af;
        font-size: 0.95rem;
    }

    .disclaimer-box {
        background-color: #f8fafc;
        border: 1px solid #cbd5e1;
        border-left: 4px solid #64748b;
        padding: 1.25rem;
        border-radius: 8px;
        margin-top: 2rem;
        font-size: 0.88rem;
        color: #334155;
    }

    .disclaimer-text { font-size: 0.8rem; color: #94a3b8; text-align: center; margin-top: 3rem; padding-top: 1rem; border-top: 1px solid #e2e8f0; }
    </style>
""", unsafe_allow_html=True)

# Huvud-banner
st.markdown("""
    <div class="main-header">
        <h1>⚡ EnergyIQ Platform</h1>
        <p>Smart energianalys, realtidskarta över Sverige, ekonomi- & CO₂-kalkylatorer.</p>
    </div>
""", unsafe_allow_html=True)

# Navigation via 4 Flikar
tab1, tab2, tab3, tab4 = st.tabs(["🗺️ Sverigekarta", "📊 Stadsanalys", "☀️ Ekonomi & Payback", "🌱 CO₂ & Klimatnytta"])

today = datetime.now()

@st.cache_data(ttl=3600)
def hamta_zon_data(zon_kod):
    url = f"https://www.elprisetjustnu.se/api/v1/prices/{today.strftime('%Y')}/{today.strftime('%m-%d')}_{zon_kod}.json"
    try:
        res = requests.get(url, timeout=5)
        return res.json() if res.status_code == 200 else None
    except Exception:
        return None

# ==========================================
# FLIK 1: SVERIGEKARTA
# ==========================================
with tab1:
    st.markdown("### 🗺️ Elpriser i Sverige i Realtid")
    map_rows = []
    zon_stats = {}

    for z_kod, z_info in ZON_KOORDINATER.items():
        z_data = hamta_zon_data(z_kod)
        if z_data:
            df_z = pd.DataFrame(z_data)
            snitt = df_z['SEK_per_kWh'].mean()
            nuvarande_timme = datetime.now().hour
            nu_pris = df_z['SEK_per_kWh'].iloc[nuvarande_timme] if nuvarande_timme < len(df_z) else snitt
            
            zon_stats[z_kod] = {"snitt": snitt, "nu": nu_pris}
            map_rows.append({
                "lat": z_info["lat"],
                "lon": z_info["lon"],
                "Zon": z_info["namn"],
                "Medelpris (kr/kWh)": round(snitt, 2)
            })

    if zon_stats:
        c1, c2, c3, c4 = st.columns(4)
        zon_cols = [c1, c2, c3, c4]
        for idx, (z_kod, z_info) in enumerate(ZON_KOORDINATER.items()):
            with zon_cols[idx]:
                st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-label">{z_kod} ({z_info['namn'].split(' ')[1]})</div>
                        <div class="metric-value">{zon_stats[z_kod]['snitt']:.2f} kr</div>
                        <div class="metric-subtext">Just nu: {zon_stats[z_kod]['nu']:.2f} kr/kWh</div>
                    </div>
                """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.subheader("📍 Geografisk översikt över Elområdena")
        df_map = pd.DataFrame(map_rows)
        st.map(df_map, latitude="lat", longitude="lon", zoom=4)

# ==========================================
# FLIK 2: STADSANALYS
# ==========================================
with tab2:
    st.markdown("### 📊 Dagsaktuella Timpriser per Stad/Kommun")
    col_sel1, col_sel2 = st.columns(2)
    with col_sel1:
        valdv_stad = st.selectbox(
            "📍 Välj din Stad / Kommun:", 
            options=sorted(list(STAD_TILL_ELOMRADE.keys())),
            index=sorted(list(STAD_TILL_ELOMRADE.keys())).index("Stockholm")
        )
        zon = STAD_TILL_ELOMRADE[valdv_stad]

    with col_sel2:
        st.write("")
        st.info(f"📍 **{valdv_stad}** tillhör elområde **{zon}**")

    data = hamta_zon_data(zon)
    if data:
        df = pd.DataFrame(data)
        df['SEK_per_kWh'] = df['SEK_per_kWh'].round(2)
        df['Timme'] = pd.to_datetime(df['time_start']).dt.strftime('%H:00')

        snitt_pris = df['SEK_per_kWh'].mean()
        max_pris = df['SEK_per_kWh'].max()
        min_pris = df['SEK_per_kWh'].min()

        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown(f'<div class="metric-card"><div class="metric-label">Medelpris ({valdv_stad})</div><div class="metric-value">{snitt_pris:.2f} kr</div></div>', unsafe_allow_html=True)
        with c2:
            st.markdown(f'<div class="metric-card"><div class="metric-label">Högsta Timpris</div><div class="metric-value" style="color: #ef4444;">{max_pris:.2f} kr</div></div>', unsafe_allow_html=True)
        with c3:
            st.markdown(f'<div class="metric-card"><div class="metric-label">Lägsta Timpris</div><div class="metric-value" style="color: #10b981;">{min_pris:.2f} kr</div></div>', unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.subheader(f"📈 Prisvariation i {valdv_stad} idag")
        chart_data = df.set_index("Timme")[["SEK_per_kWh"]]
        st.line_chart(chart_data, height=350, use_container_width=True)

# ==========================================
# FLIK 3: EKONOMI & PAYBACK
# ==========================================
with tab3:
    st.markdown("### ☀️ Investeringskalkylator (Solceller & Batterilagring)")
    col_in1, col_in2 = st.columns(2)
    with col_in1:
        effekt_kw = st.number_input("Installerad effekt (kWp):", min_value=1.0, max_value=100.0, value=10.0, step=0.5, key="kw_ekonomi")
        kostnad_sol = st.number_input("Investeringskostnad solceller (kr e. avdrag):", value=100000, step=5000)
        egenanvandning_pct = st.slider("Egenanvänd el (%):", 20, 80, 40)

    with col_in2:
        har_batteri = st.checkbox("Inkludera Batterilagring", value=True, key="bat_ekonomi")
        if har_batteri:
            batteri_kwh = st.number_input("Batterikapacitet (kWh):", min_value=1.0, max_value=50.0, value=10.0, step=1.0)
            kostnad_batteri = st.number_input("Investeringskostnad batteri (kr e. avdrag):", value=50000, step=5000)
        else:
            batteri_kwh = 0
            kostnad_batteri = 0

        elpris_snitt = st.number_input("Förväntat medel-elpris inkl. skatt (kr/kWh):", value=1.8, step=0.1)

    produktion_ar = effekt_kw * 950  
    egen_sol = produktion_ar * (egenanvandning_pct / 100)
    sold_sol = produktion_ar - egen_sol

    besparing_sol = (egen_sol * elpris_snitt) + (sold_sol * 0.50)
    besparing_batteri = (batteri_kwh * 300 * 1.20) if har_batteri else 0

    total_besparing_ar = besparing_sol + besparing_batteri
    total_investering = kostnad_sol + kostnad_batteri
    payback_ar = total_investering / total_besparing_ar if total_besparing_ar > 0 else 0

    st.markdown("---")
    r1, r2, r3, r4 = st.columns(4)
    with r1:
        st.markdown(f'<div class="metric-card"><div class="metric-label">Årlig Produktion</div><div class="metric-value">{produktion_ar:,.0f}</div><div class="metric-subtext">kWh / år</div></div>', unsafe_allow_html=True)
    with r2:
        st.markdown(f'<div class="metric-card"><div class="metric-label">Årlig Besparing</div><div class="metric-value" style="color: #10b981;">{total_besparing_ar:,.0f} kr</div><div class="metric-subtext">per år</div></div>', unsafe_allow_html=True)
    with r3:
        st.markdown(f'<div class="metric-card"><div class="metric-label">Total Investering</div><div class="metric-value">{total_investering:,.0f} kr</div><div class="metric-subtext">efter avdrag</div></div>', unsafe_allow_html=True)
    with r4:
        st.markdown(f'<div class="metric-card"><div class="metric-label">Payback-tid</div><div class="metric-value" style="color: #3b82f6;">{payback_ar:.1f} år</div><div class="metric-subtext">Återbetalningstid</div></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("📉 Ackumulerat Kassaflöde över 15 år")
    years = list(range(0, 16))
    cashflow = [-total_investering + (yr * total_besparing_ar) for yr in years]
    df_cf = pd.DataFrame({"Kassaflöde (kr)": cashflow}, index=years)
    st.line_chart(df_cf, height=350, use_container_width=True)

# ==========================================
# FLIK 4: CO2 OCH KLIMATNYTTA
# ==========================================
with tab4:
    st.markdown("### 🌱 Klimatberäkning & Utsläppsminskning (CO₂e)")
    st.write("Se hur mycket koldioxidutsläpp din anläggning sparar över tid jämfört med fossila och traditionella energikällor.")

    c_co1, c_co2 = st.columns(2)
    with c_co1:
        effekt_kw_co2 = st.number_input("Installerad solcellseffekt (kWp):", min_value=1.0, max_value=100.0, value=10.0, step=0.5, key="kw_co2")
        jamforelse_kraft = st.selectbox(
            "Jämför mot ersatt energikälla (Marginalel):",
            ["Europeisk Marginalel (Kol/Gas ~ 400 g/kWh)", "Nordisk Mix (~ 120 g/kWh)", "Svenskt Elnät (~ 45 g/kWh)", "Kolkraft (~ 900 g/kWh)"]
        )

    with c_co2:
        anlaggning_livslangd = st.slider("Anläggningens livslängd (År):", 10, 30, 25)

    CO2_FAKTORER = {
        "Europeisk Marginalel (Kol/Gas ~ 400 g/kWh)": 400,
        "Nordisk Mix (~ 120 g/kWh)": 120,
        "Svenskt Elnät (~ 45 g/kWh)": 45,
        "Kolkraft (~ 900 g/kWh)": 900
    }

    val_g_co2 = CO2_FAKTORER[jamforelse_kraft]
    
    prod_ar_kwh = effekt_kw_co2 * 950
    netto_sparad_co2_g_kwh = max(0, val_g_co2 - 40) # 40g/kWh = schablon för tillverkning
    
    co2_sparad_ar_ton = (prod_ar_kwh * netto_sparad_co2_g_kwh) / 1_000_000
    co2_sparad_total_ton = co2_sparad_ar_ton * anlaggning_livslangd

    bensin_mil = co2_sparad_total_ton * 650
    antal_trad = co2_sparad_total_ton * 50

    st.markdown("---")
    st.markdown("### 📊 Uppskattad Klimatnytta")

    k1, k2, k3 = st.columns(3)
    with k1:
        st.markdown(f'<div class="metric-card"><div class="metric-label">Årlig CO₂-Inbesparing</div><div class="metric-value" style="color: #10b981;">{co2_sparad_ar_ton:.2f} ton</div><div class="metric-subtext">CO₂e per år</div></div>', unsafe_allow_html=True)
    with k2:
        st.markdown(f'<div class="metric-card"><div class="metric-label">Total CO₂-Minskning ({anlaggning_livslangd} år)</div><div class="metric-value" style="color: #10b981;">{co2_sparad_total_ton:.1f} ton</div><div class="metric-subtext">nettoinbesparing</div></div>', unsafe_allow_html=True)
    with k3:
        st.markdown(f'<div class="metric-card"><div class="metric-label">Klimatskuld Betald efter</div><div class="metric-value" style="color: #3b82f6;">1.8 år</div><div class="metric-subtext">Energetisk återbetalningstid</div></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("#### 🚗 Vad motsvarar koldioxidminskningen?")
    
    e1, e2 = st.columns(2)
    with e1:
        st.markdown(f'<div class="info-box" style="border-left-color: #10b981; background-color: #f0fdf4; color: #166534;">🚗 <b>Motsvarar Bensinbil:</b> ca <b>{bensin_mil:,.0f} mil</b> i körtsträcka med en normal bensinbil över {anlaggning_livslangd} år.</div>', unsafe_allow_html=True)
    with e2:
        st.markdown(f'<div class="info-box" style="border-left-color: #10b981; background-color: #f0fdf4; color: #166534;">🌲 <b>Motsvarar Trädplantering:</b> ca <b>{antal_trad:,.0f} växande träd</b> som binder koldioxid i 10 år.</div>', unsafe_allow_html=True)

    # LCA DISCLAIMER & METODRUTA
    st.markdown("""
        <div class="disclaimer-box">
            <b>📋 Metod, Avgränsning & LCA-Disclaimer:</b><br>
            • <b>Vad som ingår i kalkylen:</b> Kalkylen baseras på en schabloniserad Livscykelanalys (LCA) där solcellernas tillverkning beräknas generera <b>~40 g CO₂e/kWh</b> under sin livslängd. Nettoinbesparingen beräknas som differensen mellan den ersatta elens koldioxidintensitet och solcellernas tillverkningsavtryck.<br>
            • <b>Vad som INTE ingår:</b> Specifik transportsträcka från tillverkningsland till installationsplats, utsläpp kopplade till fysiskt monteringsarbete/ställningar på plats, inverkan av växelriktares utbyte under livslängden samt sluthantering/återvinning (End-of-Life).<br>
            • <i>Kalkylen är indikativ och utformad för att ge ett pedagogiskt beslutsunderlag. För officiella ESG- och GHG-rapporter rekommenderas specifik LCA-analys från leverantören.</i>
        </div>
    """, unsafe_allow_html=True)

    # Jämförelsegraf över energislagens CO2-avtryck
    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("⚖️ CO₂-utsläpp per kWh för olika energislag (g CO₂e/kWh)")
    
    df_co2_comp = pd.DataFrame({
        "Energislag": ["Kolkraft", "Naturgas", "Solceller (Tillverkning)", "Vattenkraft", "Kärnkraft"],
        "Gram CO2 per kWh": [820, 490, 40, 24, 12]
    }).set_index("Energislag")

    st.bar_chart(df_co2_comp, height=350, use_container_width=True)

# Footer
st.markdown('<div class="disclaimer-text">EnergyIQ Version 1.6 • Utvecklad med Python & Streamlit • Live Sverigekarta, Ekonomi & CO₂-klimatberäkningar med LCA-disclaimer.</div>', unsafe_allow_html=True)
