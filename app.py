import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import folium
from streamlit_folium import st_folium

# Sidkonfiguration
st.set_page_config(
    page_title="EnergyIQ | Nordisk Energianalys & Interaktiv Karta",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Kartläggning från Nordiska Städer till Elområden
STAD_TILL_ELOMRADE = {
    # Sverige (SE)
    "Luleå (SE1)": "SE1", "Kiruna (SE1)": "SE1", "Boden (SE1)": "SE1", "Umeå (SE2)": "SE2",
    "Sundsvall (SE2)": "SE2", "Östersund (SE2)": "SE2", "Gävle (SE2)": "SE2",
    "Stockholm (SE3)": "SE3", "Göteborg (SE3)": "SE3", "Uppsala (SE3)": "SE3", "Västerås (SE3)": "SE3",
    "Örebro (SE3)": "SE3", "Linköping (SE3)": "SE3", "Karlstad (SE3)": "SE3",
    "Malmö (SE4)": "SE4", "Helsingborg (SE4)": "SE4", "Lund (SE4)": "SE4", "Växjö (SE4)": "SE4",
    
    # Norge (NO)
    "Oslo (NO1)": "NO1", "Kristiansand (NO2)": "NO2", "Stavanger (NO2)": "NO2",
    "Trondheim (NO3)": "NO3", "Molde (NO3)": "NO3", "Tromsø (NO4)": "NO4",
    "Bodø (NO4)": "NO4", "Bergen (NO5)": "NO5",
    
    # Finland (FI)
    "Helsingfors (FI)": "FI", "Tammerfors (FI)": "FI", "Åbo (FI)": "FI", "Uleåborg (FI)": "FI",
    
    # Danmark (DK)
    "Århus (DK1)": "DK1", "Aalborg (DK1)": "DK1", "Esbjerg (DK1)": "DK1",
    "Köpenhamn (DK2)": "DK2", "Roskilde (DK2)": "DK2"
}

# CSS Styling
st.markdown("""
    <style>
    div[data-baseweb="tab-highlight"], div[data-baseweb="tab-border"] {
        display: none !important;
    }

    *:focus, button:focus, [tabindex]:focus, div:focus {
        outline: none !important;
        box-shadow: none !important;
        border-color: transparent !important;
    }
    
    .main { background-color: #f1f5f9; }
    
    .main-header {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 60%, #1e3a8a 100%);
        padding: 2.5rem 2.2rem;
        border-radius: 16px;
        color: #ffffff;
        margin-bottom: 2rem;
        box-shadow: 0 12px 28px -5px rgba(15, 23, 42, 0.2);
        border-bottom: 4px solid #3b82f6;
    }
    
    .main-header h1 { 
        color: #ffffff !important; 
        font-weight: 800; 
        font-size: 2.3rem; 
        margin-bottom: 0.4rem;
        letter-spacing: -0.02em;
    }
    
    .main-header p { 
        color: #cbd5e1; 
        font-size: 1.05rem; 
        margin: 0;
        font-weight: 500;
    }
    
    .metric-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 14px;
        padding: 1.2rem 1.4rem;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.03);
        margin-bottom: 1rem;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(0,0,0,0.06);
    }
    
    .metric-label { 
        font-size: 0.82rem; 
        font-weight: 700; 
        color: #64748b; 
        text-transform: uppercase; 
        letter-spacing: 0.06em; 
        margin-bottom: 0.4rem; 
    }
    
    .metric-value { 
        font-size: 1.8rem; 
        font-weight: 800; 
        color: #0f172a; 
    }
    
    .metric-subtext { 
        font-size: 0.82rem; 
        color: #64748b; 
        font-weight: 600; 
        margin-top: 0.3rem; 
    }

    .stTabs [data-baseweb="tab-list"] { 
        gap: 12px; 
        border-bottom: 2px solid #cbd5e1; 
        padding-bottom: 8px; 
    }

    .stTabs [data-baseweb="tab"] { 
        height: 54px; 
        border-radius: 10px; 
        padding: 0px 24px; 
        font-weight: 700; 
        font-size: 1.05rem;
        color: #475569; 
        background-color: #ffffff;
        border: 1px solid #cbd5e1;
        box-shadow: 0 2px 5px rgba(0,0,0,0.02);
    }

    .stTabs [aria-selected="true"] { 
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%) !important; 
        color: #ffffff !important; 
        border: none !important;
        box-shadow: 0 6px 16px rgba(15, 23, 42, 0.3) !important;
    }

    .info-box {
        background-color: #eff6ff;
        border-left: 5px solid #2563eb;
        padding: 1.1rem 1.3rem;
        border-radius: 0 10px 10px 0;
        margin: 1.5rem 0;
        color: #1e40af;
        font-size: 0.95rem;
    }
    </style>
""", unsafe_allow_html=True)

# Huvud-banner
st.markdown("""
    <div class="main-header">
        <h1>EnergyIQ Norden</h1>
        <p>Nordisk elprisanalys (Sverige, Norge, Finland, Danmark), interaktiv karta & kalkylatorer.</p>
    </div>
""", unsafe_allow_html=True)

tab1, tab2, tab3, tab4 = st.tabs(["Nordisk Elpriskarta", "Stadsanalys", "Ekonomi & Payback", "CO₂ & Klimatnytta"])

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
# FLIK 1: NORDISK ELPRISKARTA
# ==========================================
with tab1:
    st.markdown("### Interaktiv Elpriskarta över Norden")
    
    land_val = st.radio(
        "Välj land för nyckeltal:", 
        ["Alla / Hela Norden", "Sverige (SE)", "Norge (NO)", "Finland (FI)", "Danmark (DK)"],
        horizontal=True
    )

    NORDEN_ZONER = {
        "SE1": {"namn": "SE1 Norrbotten", "land": "Sverige (SE)", "farg": "#3b82f6", "stader": "Luleå, Kiruna, Boden"},
        "SE2": {"namn": "SE2 Sundsvall", "land": "Sverige (SE)", "farg": "#10b981", "stader": "Sundsvall, Umeå, Östersund"},
        "SE3": {"namn": "SE3 Sthlm / Gbg", "land": "Sverige (SE)", "farg": "#f59e0b", "stader": "Stockholm, Göteborg, Uppsala"},
        "SE4": {"namn": "SE4 Malmö / Syd", "land": "Sverige (SE)", "farg": "#ef4444", "stader": "Malmö, Helsingborg, Lund"},
        
        "NO1": {"namn": "NO1 Oslo", "land": "Norge (NO)", "farg": "#8b5cf6", "stader": "Oslo, Drammen"},
        "NO2": {"namn": "NO2 Kristiansand", "land": "Norge (NO)", "farg": "#6366f1", "stader": "Kristiansand, Stavanger"},
        "NO3": {"namn": "NO3 Trondheim", "land": "Norge (NO)", "farg": "#06b6d4", "stader": "Trondheim, Molde"},
        "NO4": {"namn": "NO4 Tromsø", "land": "Norge (NO)", "farg": "#0284c7", "stader": "Tromsø, Bodø"},
        "NO5": {"namn": "NO5 Bergen", "land": "Norge (NO)", "farg": "#a855f7", "stader": "Bergen"},
        
        "FI": {"namn": "FI Finland", "land": "Finland (FI)", "farg": "#14b8a6", "stader": "Helsingfors, Tammerfors, Åbo"},
        
        "DK1": {"namn": "DK1 Jylland/Fyn", "land": "Danmark (DK)", "farg": "#ec4899", "stader": "Århus, Aalborg, Esbjerg"},
        "DK2": {"namn": "DK2 Själland", "land": "Danmark (DK)", "farg": "#f43f5e", "stader": "Köpenhamn, Roskilde"}
    }

    zon_stats = {}
    for z_kod in NORDEN_ZONER.keys():
        z_data = hamta_zon_data(z_kod)
        if z_data:
            df_z = pd.DataFrame(z_data)
            snitt = df_z['SEK_per_kWh'].mean()
            max_p = df_z['SEK_per_kWh'].max()
            min_p = df_z['SEK_per_kWh'].min()
            nu_h = datetime.now().hour
            nu_pris = df_z['SEK_per_kWh'].iloc[nu_h] if nu_h < len(df_z) else snitt
            zon_stats[z_kod] = {"snitt": snitt, "nu": nu_pris, "max": max_p, "min": min_p}

    # Visa relevanta kort
    filtrerade_zoner = [
        k for k, v in NORDEN_ZONER.items() 
        if land_val == "Alla / Hela Norden" or v["land"] == land_val
    ]

    cols = st.columns(min(len(filtrerade_zoner), 4))
    for i, z_kod in enumerate(filtrerade_zoner):
        col = cols[i % len(cols)]
        meta = NORDEN_ZONER[z_kod]
        if z_kod in zon_stats:
            st_data = zon_stats[z_kod]
            with col:
                st.markdown(f"""
                    <div class="metric-card" style="border-top: 5px solid {meta['farg']};">
                        <div class="metric-label">{meta['namn']}</div>
                        <div class="metric-value">{st_data['snitt']:.2f} kr</div>
                        <div class="metric-subtext">Just nu: <span style="color:{meta['farg']}; font-weight:700;">{st_data['nu']:.2f} kr/kWh</span></div>
                    </div>
                """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Norden Folium Karta
    m = folium.Map(location=[62.5, 15.0], zoom_start=4.4, tiles="cartodbpositron")

    NORDEN_POLYGONER = {
        # Sverige
        "SE1": [[69.0, 20.5], [68.5, 22.2], [65.8, 24.1], [65.0, 21.3], [65.0, 15.0], [67.8, 16.5], [69.0, 20.5]],
        "SE2": [[65.0, 15.0], [65.0, 21.3], [60.6, 17.2], [60.6, 13.0], [63.2, 12.0], [65.0, 15.0]],
        "SE3": [[60.6, 13.0], [60.6, 17.2], [57.3, 16.8], [57.3, 12.0], [59.9, 12.2], [60.6, 13.0]],
        "SE4": [[57.3, 12.0], [57.3, 16.8], [55.4, 14.2], [55.4, 12.8], [57.3, 12.0]],
        
        # Norge
        "NO1": [[60.5, 9.5], [60.8, 11.8], [59.0, 11.8], [59.0, 9.5], [60.5, 9.5]],
        "NO2": [[59.5, 5.0], [59.5, 9.5], [58.0, 9.5], [58.0, 5.0], [59.5, 5.0]],
        "NO3": [[65.0, 11.0], [65.0, 14.5], [62.0, 12.0], [62.0, 8.5], [65.0, 11.0]],
        "NO4": [[71.2, 24.0], [70.0, 31.0], [65.0, 15.0], [65.0, 11.0], [68.0, 14.0], [71.2, 24.0]],
        "NO5": [[62.0, 4.5], [62.0, 8.5], [60.0, 8.5], [60.0, 4.5], [62.0, 4.5]],
        
        # Finland
        "FI": [[70.0, 28.0], [69.0, 29.0], [65.0, 30.0], [60.0, 27.0], [59.8, 22.5], [63.0, 21.0], [66.0, 24.0], [70.0, 28.0]],
        
        # Danmark
        "DK1": [[57.7, 8.0], [57.5, 10.8], [55.3, 10.8], [54.8, 8.5], [57.7, 8.0]],
        "DK2": [[56.2, 11.0], [56.0, 12.6], [54.9, 12.6], [54.9, 11.0], [56.2, 11.0]]
    }

    for z_kod, coords in NORDEN_POLYGONER.items():
        meta = NORDEN_ZONER[z_kod]
        stats = zon_stats.get(z_kod, {"snitt": 0, "max": 0, "min": 0})
        
        popup_html = f"""
            <div style="font-family: Arial, sans-serif; width: 220px;">
                <h4 style="margin:0 0 6px 0; color:{meta['farg']};">{meta['namn']}</h4>
                <p style="margin:2px 0;"><b>Medelpris:</b> {stats['snitt']:.2f} kr/kWh</p>
                <p style="margin:2px 0; color:#ef4444;"><b>Max:</b> {stats['max']:.2f} kr/kWh</p>
                <p style="margin:2px 0; color:#10b981;"><b>Min:</b> {stats['min']:.2f} kr/kWh</p>
                <hr style="margin:6px 0; border:0; border-top:1px solid #e2e8f0;">
                <small style="color:#64748b;"><b>Städer:</b> {meta['stader']}</small>
            </div>
        """

        folium.Polygon(
            locations=coords,
            color=meta["farg"],
            weight=2,
            fill=True,
            fill_color=meta["farg"],
            fill_opacity=0.45,
            popup=folium.Popup(popup_html, max_width=250),
            tooltip=f"{meta['namn']} — Medel: {stats['snitt']:.2f} kr/kWh"
        ).add_to(m)

    st_folium(m, width="100%", height=560)

# ==========================================
# FLIK 2: STADSANALYS
# ==========================================
with tab2:
    st.markdown("### Dagsaktuella Timpriser per Nordisk Stad / Kommun")
    col_sel1, col_sel2 = st.columns(2)
    with col_sel1:
        valdv_stad = st.selectbox(
            "Välj Stad / Kommun i Norden:", 
            options=sorted(list(STAD_TILL_ELOMRADE.keys())),
            index=sorted(list(STAD_TILL_ELOMRADE.keys())).index("Stockholm (SE3)")
        )
        zon = STAD_TILL_ELOMRADE[valdv_stad]

    with col_sel2:
        st.write("")
        st.info(f"**{valdv_stad}** tillhör elområde **{zon}**")

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
            st.markdown(f'<div class="metric-card" style="border-top: 5px solid #2563eb;"><div class="metric-label">Medelpris</div><div class="metric-value">{snitt_pris:.2f} kr</div></div>', unsafe_allow_html=True)
        with c2:
            st.markdown(f'<div class="metric-card" style="border-top: 5px solid #ef4444;"><div class="metric-label">Högsta Timpris</div><div class="metric-value" style="color: #ef4444;">{max_pris:.2f} kr</div></div>', unsafe_allow_html=True)
        with c3:
            st.markdown(f'<div class="metric-card" style="border-top: 5px solid #10b981;"><div class="metric-label">Lägsta Timpris</div><div class="metric-value" style="color: #10b981;">{min_pris:.2f} kr</div></div>', unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.subheader(f"Prisvariation i {valdv_stad} idag")
        st.line_chart(df.set_index("Timme")[["SEK_per_kWh"]], height=350, use_container_width=True)

# ==========================================
# FLIK 3: EKONOMI & PAYBACK
# ==========================================
with tab3:
    st.markdown("### Investeringskalkylator (Solceller & Batterilagring)")
    st.caption("Håll muspekaren över frågetecken-ikonerna (?) för att se förklaringar av beräkningarna.")
    
    col_in1, col_in2 = st.columns(2)
    with col_in1:
        effekt_kw = st.number_input(
            "Installerad effekt (kWp):", 
            min_value=1.0, max_value=100.0, value=10.0, step=0.5, key="kw_ekonomi",
            help="Solcellsanläggningens maximala toppeffekt i kilowatt-peak (kWp) under ideala förhållanden."
        )
        kostnad_sol = st.number_input(
            "Investeringskostnad solceller (kr e. avdrag):", 
            value=100000, step=5000,
            help="Den totala investeringskostnaden efter nyttjat skatteavdrag/stöd."
        )
        egenanvandning_pct = st.slider(
            "Egenanvänd el (%):", 
            20, 80, 40,
            help="Hur stor andel av din producerade solel som du förbrukar själv i fastigheten."
        )

    with col_in2:
        har_batteri = st.checkbox("Inkludera Batterilagring", value=True, key="bat_ekonomi")
        if har_batteri:
            batteri_kwh = st.number_input("Batterikapacitet (kWh):", min_value=1.0, max_value=50.0, value=10.0, step=1.0)
            kostnad_batteri = st.number_input("Investeringskostnad batteri (kr e. avdrag):", value=50000, step=5000)
        else:
            batteri_kwh, kostnad_batteri = 0, 0

        elpris_snitt = st.number_input("Förväntat medel-elpris (kr/kWh):", value=1.8, step=0.1)

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
        st.markdown(f'<div class="metric-card" style="border-top: 5px solid #2563eb;"><div class="metric-label">Årlig Produktion</div><div class="metric-value">{produktion_ar:,.0f} kWh</div></div>', unsafe_allow_html=True)
    with r2:
        st.markdown(f'<div class="metric-card" style="border-top: 5px solid #10b981;"><div class="metric-label">Årlig Besparing</div><div class="metric-value" style="color:#10b981;">{total_besparing_ar:,.0f} kr</div></div>', unsafe_allow_html=True)
    with r3:
        st.markdown(f'<div class="metric-card" style="border-top: 5px solid #64748b;"><div class="metric-label">Total Investering</div><div class="metric-value">{total_investering:,.0f} kr</div></div>', unsafe_allow_html=True)
    with r4:
        st.markdown(f'<div class="metric-card" style="border-top: 5px solid #3b82f6;"><div class="metric-label">Payback-tid</div><div class="metric-value" style="color:#3b82f6;">{payback_ar:.1f} år</div></div>', unsafe_allow_html=True)

# ==========================================
# FLIK 4: CO2 OCH KLIMATNYTTA
# ==========================================
with tab4:
    st.markdown("### Klimatberäkning & Utsläppsminskning (CO₂e)")
    c_co1, c_co2 = st.columns(2)
    with c_co1:
        effekt_kw_co2 = st.number_input("Installerad solcellseffekt (kWp):", min_value=1.0, max_value=100.0, value=10.0, step=0.5, key="kw_co2")
        jamforelse_kraft = st.selectbox(
            "Jämför mot ersatt energikälla (Marginalel):",
            ["Europeisk Marginalel (Kol/Gas ~ 400 g/kWh)", "Nordisk Mix (~ 120 g/kWh)", "Svenskt Elnät (~ 45 g/kWh)", "Kolkraft (~ 900 g/kWh)"]
        )

    with c_co2:
        anlaggning_livslangd = st.slider("Anläggningens livslängd (År):", 10, 30, 25)

    val_g_co2 = {"Europeisk Marginalel (Kol/Gas ~ 400 g/kWh)": 400, "Nordisk Mix (~ 120 g/kWh)": 120, "Svenskt Elnät (~ 45 g/kWh)": 45, "Kolkraft (~ 900 g/kWh)": 900}[jamforelse_kraft]
    prod_ar_kwh = effekt_kw_co2 * 950
    netto_sparad_co2_g_kwh = max(0, val_g_co2 - 40)
    co2_sparad_ar_ton = (prod_ar_kwh * netto_sparad_co2_g_kwh) / 1_000_000
    co2_sparad_total_ton = co2_sparad_ar_ton * anlaggning_livslangd

    st.markdown("---")
    k1, k2, k3 = st.columns(3)
    with k1:
        st.markdown(f'<div class="metric-card" style="border-top: 5px solid #10b981;"><div class="metric-label">Årlig CO₂-Inbesparing</div><div class="metric-value" style="color:#10b981;">{co2_sparad_ar_ton:.2f} ton</div></div>', unsafe_allow_html=True)
    with k2:
        st.markdown(f'<div class="metric-card" style="border-top: 5px solid #10b981;"><div class="metric-label">Total CO₂-Minskning</div><div class="metric-value" style="color:#10b981;">{co2_sparad_total_ton:.1f} ton</div></div>', unsafe_allow_html=True)
    with k3:
        st.markdown(f'<div class="metric-card" style="border-top: 5px solid #3b82f6;"><div class="metric-label">Klimatskuld Betald</div><div class="metric-value" style="color:#3b82f6;">1.8 år</div></div>', unsafe_allow_html=True)
