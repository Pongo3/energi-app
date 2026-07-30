import streamlit as st
import requests
import pandas as pd
from datetime import datetime

# Sidkonfiguration
st.set_page_config(
    page_title="EnergyIQ | Digital Energianalys & Kalkylator",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Anpassad CSS för ett professionellt SaaS-gränssnitt
st.markdown("""
    <style>
    /* Bakgrundsfärg */
    .main {
        background-color: #f8fafc;
    }
    
    /* Header-banner */
    .main-header {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        padding: 2.2rem 2rem;
        border-radius: 16px;
        color: #ffffff;
        margin-bottom: 2rem;
        box-shadow: 0 10px 25px -5px rgba(15, 23, 42, 0.15);
    }
    
    .main-header h1 {
        color: #ffffff !important;
        font-weight: 800;
        font-size: 2.2rem;
        margin-bottom: 0.4rem;
    }
    
    .main-header p {
        color: #94a3b8;
        font-size: 1.05rem;
        margin: 0;
    }
    
    /* KPI-Kort */
    .metric-card {
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 1.25rem 1.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.02);
        margin-bottom: 1rem;
    }
    
    .metric-label {
        font-size: 0.85rem;
        font-weight: 600;
        color: #64748b;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 0.35rem;
    }
    
    .metric-value {
        font-size: 1.8rem;
        font-weight: 800;
        color: #0f172a;
    }
    
    .metric-subtext {
        font-size: 0.8rem;
        color: #64748b;
        font-weight: 500;
        margin-top: 0.25rem;
    }

    /* Flik-design */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        border-bottom: 2px solid #e2e8f0;
        padding-bottom: 4px;
    }

    .stTabs [data-baseweb="tab"] {
        height: 48px;
        border-radius: 8px;
        padding: 0px 20px;
        font-weight: 600;
        color: #64748b;
        background-color: transparent;
    }

    .stTabs [aria-selected="true"] {
        background-color: #3b82f6 !important;
        color: #ffffff !important;
    }

    /* Info-ruta */
    .info-box {
        background-color: #eff6ff;
        border-left: 4px solid #3b82f6;
        padding: 1rem 1.25rem;
        border-radius: 0 8px 8px 0;
        margin: 1.5rem 0;
        color: #1e40af;
        font-size: 0.95rem;
    }

    .disclaimer-text {
        font-size: 0.8rem;
        color: #94a3b8;
        text-align: center;
        margin-top: 3rem;
        padding-top: 1rem;
        border-top: 1px solid #e2e8f0;
    }
    </style>
""", unsafe_allow_html=True)

# Huvud-banner
st.markdown("""
    <div class="main-header">
        <h1>⚡ EnergyIQ Platform</h1>
        <p>Smart energianalys, realtidsdata från Nord Pool och investeringskalkylatorer för solceller & batterilagring.</p>
    </div>
""", unsafe_allow_html=True)

# Navigation via Flikar
tab1, tab2 = st.tabs(["📊 Elpriser i Realtid", "☀️ Investeringskalkylator"])

# ==========================================
# FLIK 1: ELPRISER I REALTID
# ==========================================
with tab1:
    st.markdown("### 📊 Dagsaktuella Timpriser")
    
    col_sel, _ = st.columns([1, 2])
    with col_sel:
        elomrade = st.selectbox("Välj Elområde:", ["SE1 (Luleå)", "SE2 (Sundsvall)", "SE3 (Stockholm)", "SE4 (Malmö)"], index=2)
        zon = elomrade.split(" ")[0]

    today = datetime.now()
    url = f"https://www.elprisetjustnu.se/api/v1/prices/{today.strftime('%Y')}/{today.strftime('%m-%d')}_{zon}.json"

    @st.cache_data(ttl=3600)
    def hamta_elpriser(api_url):
        try:
            res = requests.get(api_url, timeout=5)
            return res.json() if res.status_code == 200 else None
        except Exception:
            return None

    data = hamta_elpriser(url)

    if data:
        df = pd.DataFrame(data)
        df['SEK_per_kWh'] = df['SEK_per_kWh'].round(2)
        df['Timme'] = pd.to_datetime(df['time_start']).dt.strftime('%H:00')

        snitt_pris = df['SEK_per_kWh'].mean()
        max_pris = df['SEK_per_kWh'].max()
        min_pris = df['SEK_per_kWh'].min()

        # Responsiva KPI-kort
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">Medelpris Idag</div>
                    <div class="metric-value">{snitt_pris:.2f} kr</div>
                    <div class="metric-subtext">per kWh (exkl. nät)</div>
                </div>
            """, unsafe_allow_html=True)
        with c2:
            st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">Högsta Timpris</div>
                    <div class="metric-value" style="color: #ef4444;">{max_pris:.2f} kr</div>
                    <div class="metric-subtext" style="color: #ef4444;">Dagens toppnotering</div>
                </div>
            """, unsafe_allow_html=True)
        with c3:
            st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">Lägsta Timpris</div>
                    <div class="metric-value" style="color: #10b981;">{min_pris:.2f} kr</div>
                    <div class="metric-subtext" style="color: #10b981;">Bästa laddtimme</div>
                </div>
            """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.subheader("📈 Prisvariation över dygnet (SEK/kWh)")
        
        chart_data = df.set_index("Timme")[["SEK_per_kWh"]]
        st.line_chart(chart_data, height=350, use_container_width=True)
        
        st.markdown("""
            <div class="info-box">
                💡 <b>Energiråd:</b> Genom att styra tunga förbrukare (elbilsladdning, värmepump) från dagens dyraste timmar till de billigaste kan ett hushåll eller företag sänka sina rörliga elkostnader avsevärt.
            </div>
        """, unsafe_allow_html=True)

    else:
        st.warning("Går inte att hämta live-data från elmarknaden just nu. Kontrollera anslutningen.")

# ==========================================
# FLIK 2: INVESTERINGSKALKYLATOR
# ==========================================
with tab2:
    st.markdown("### ☀️ Investeringskalkylator (Solceller & Batterilagring)")
    st.write("Skräddarsy parametrarna för att beräkna den uppskattade återbetalningstiden och 15-åriga kassaflödet.")

    col_in1, col_in2 = st.columns(2)

    with col_in1:
        st.markdown("#### 1. Solcellsanläggning")
        effekt_kw = st.number_input("Installerad effekt (kWp):", min_value=1.0, max_value=100.0, value=10.0, step=0.5)
        kostnad_sol = st.number_input("Investeringskostnad solceller (kr e. avdrag):", value=100000, step=5000)
        egenanvandning_pct = st.slider("Egenanvänd el (%):", 20, 80, 40, help="Andel av solenergin som förbrukas direkt i fastigheten.")

    with col_in2:
        st.markdown("#### 2. Batterilagring & Elpris")
        har_batteri = st.checkbox("Inkludera Batterilagring", value=True)
        
        if har_batteri:
            batteri_kwh = st.number_input("Batterikapacitet (kWh):", min_value=1.0, max_value=50.0, value=10.0, step=1.0)
            kostnad_batteri = st.number_input("Investeringskostnad batteri (kr e. avdrag):", value=50000, step=5000)
        else:
            batteri_kwh = 0
            kostnad_batteri = 0

        elpris_snitt = st.number_input("Förväntat medel-elpris inkl. skatt (kr/kWh):", value=1.8, step=0.1)

    # Beräkningslogik
    produktion_ar = effekt_kw * 950  
    egen_sol = produktion_ar * (egenanvandning_pct / 100)
    sold_sol = produktion_ar - egen_sol

    besparing_sol = (egen_sol * elpris_snitt) + (sold_sol * 0.50)
    besparing_batteri = (batteri_kwh * 300 * 1.20) if har_batteri else 0

    total_besparing_ar = besparing_sol + besparing_batteri
    total_investering = kostnad_sol + kostnad_batteri

    payback_ar = total_investering / total_besparing_ar if total_besparing_ar > 0 else 0

    st.markdown("---")
    st.markdown("### 📊 Investeringsresultat")

    r1, r2, r3, r4 = st.columns(4)
    with r1:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Årlig Produktion</div>
                <div class="metric-value">{produktion_ar:,.0f}</div>
                <div class="metric-subtext">kWh / år</div>
            </div>
        """, unsafe_allow_html=True)
    with r2:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Årlig Besparing</div>
                <div class="metric-value" style="color: #10b981;">{total_besparing_ar:,.0f} kr</div>
                <div class="metric-subtext">per år</div>
            </div>
        """, unsafe_allow_html=True)
    with r3:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Total Investering</div>
                <div class="metric-value">{total_investering:,.0f} kr</div>
                <div class="metric-subtext">efter grön teknik</div>
            </div>
        """, unsafe_allow_html=True)
    with r4:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Payback-tid</div>
                <div class="metric-value" style="color: #3b82f6;">{payback_ar:.1f} år</div>
                <div class="metric-subtext">Återbetalningstid</div>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("📉 Ackumulerat Kassaflöde över 15 år")
    
    years = list(range(0, 16))
    cashflow = [-total_investering + (yr * total_besparing_ar) for yr in years]
    df_cf = pd.DataFrame({"Kassaflöde (kr)": cashflow}, index=years)
    
    st.line_chart(df_cf, height=350, use_container_width=True)

# Footer
st.markdown("""
    <div class="disclaimer-text">
        EnergyIQ Version 1.2 • Utvecklad med Python & Streamlit • Data från Elprisetjustnu / Nord Pool • Kalkylen är indikativ.
    </div>
""", unsafe_allow_html=True)
