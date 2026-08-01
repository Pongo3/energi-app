import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import folium
from streamlit_folium import st_folium
import io
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors

# Sidkonfiguration
st.set_page_config(
    page_title="EnergyIQ | Digital Energianalys & Interaktiv Karta",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Kartläggning från Svenska Städer till Elområden
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
        padding: 1.4rem 1.6rem;
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
        font-size: 1.9rem; 
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
        box-shadow: 0 2px 8px rgba(37, 99, 235, 0.05);
    }

    .disclaimer-box {
        background-color: #ffffff;
        border: 1px solid #cbd5e1;
        border-left: 5px solid #64748b;
        padding: 1.4rem;
        border-radius: 10px;
        margin-top: 2rem;
        font-size: 0.88rem;
        color: #334155;
        box-shadow: 0 2px 8px rgba(0,0,0,0.02);
    }

    /* B2B Contact Card */
    .b2b-card {
        background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
        border: 1px solid #cbd5e1;
        border-left: 6px solid #2563eb;
        border-radius: 14px;
        padding: 1.8rem 2rem;
        margin-top: 3rem;
        box-shadow: 0 6px 18px rgba(0,0,0,0.04);
    }

    .b2b-card h3 {
        color: #0f172a !important;
        font-size: 1.3rem;
        font-weight: 800;
        margin-bottom: 0.5rem;
    }

    .b2b-card p {
        color: #475569;
        font-size: 0.98rem;
        margin-bottom: 1rem;
        line-height: 1.5;
    }

    .disclaimer-text { 
        font-size: 0.82rem; 
        color: #94a3b8; 
        text-align: center; 
        margin-top: 2.5rem; 
        padding-top: 1.2rem; 
        border-top: 1px solid #e2e8f0; 
    }
    </style>
""", unsafe_allow_html=True)

# Funktion för att skapa PDF-rapporter
def skape_pdf_rapport(effekt_kw, batteri_kwh, sol_degradering, bat_degradering, kostnad_sol, kostnad_batteri, total_investering, elpris_snitt, elpris_inflation, effekt_kapat_kw, effekt_taxa_kr_kw, payback_str, besparing_ar1, nettonytta_25ar):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    # Header Banner
    c.setFillColor(colors.HexColor("#0f172a"))
    c.rect(0, height - 100, width, 100, fill=1, stroke=0)

    # Titel
    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 22)
    c.drawString(40, height - 45, "EnergyIQ - Investeringsrapport")
    c.setFont("Helvetica", 11)
    c.drawString(40, height - 70, f"Genererad: {datetime.now().strftime('%Y-%m-%d %H:%M')} | Licensierad Energimodell")

    # Sektion 1: Specifikation
    y = height - 140
    c.setFillColor(colors.HexColor("#0f172a"))
    c.setFont("Helvetica-Bold", 14)
    c.drawString(40, y, "1. Anläggningsspecifikation & Indata")
    c.setStrokeColor(colors.HexColor("#cbd5e1"))
    c.setLineWidth(1)
    c.line(40, y - 5, width - 40, y - 5)

    y -= 30
    c.setFont("Helvetica", 10)
    c.setFillColor(colors.HexColor("#334155"))
    
    spec_rader = [
        f"• Installerad Solcellseffekt: {effekt_kw} kWp",
        f"• Batterilagringskapacitet: {batteri_kwh} kWh",
        f"• Årlig degradering (Solceller / Batteri): {sol_degradering}% / {bat_degradering}%",
        f"• Investeringskostnad Solceller (efter avdrag): {kostnad_sol:,.0f} kr",
        f"• Investeringskostnad Batteri (efter avdrag): {kostnad_batteri:,.0f} kr",
        f"• Total Nettoinvestering: {total_investering:,.0f} kr",
        f"• Förväntat medel-elpris: {elpris_snitt} kr/kWh (Inflation: {elpris_inflation}%/år)",
        f"• Kapad effekttopp: {effekt_kapat_kw} kW (Effekttaxa: {effekt_taxa_kr_kw} kr/kW/mån)"
    ]

    for rad in spec_rader:
        c.drawString(50, y, rad)
        y -= 18

    # Sektion 2: Resultat
    y -= 20
    c.setFillColor(colors.HexColor("#0f172a"))
    c.setFont("Helvetica-Bold", 14)
    c.drawString(40, y, "2. Ekonomiskt Resultat & Livscykelanalys (25 År)")
    c.line(40, y - 5, width - 40, y - 5)

    y -= 35
    c.setFillColor(colors.HexColor("#f8fafc"))
    c.rect(40, y - 50, 160, 60, fill=1, stroke=1)
    c.rect(215, y - 50, 160, 60, fill=1, stroke=1)
    c.rect(390, y - 50, 165, 60, fill=1, stroke=1)

    c.setFillColor(colors.HexColor("#64748b"))
    c.setFont("Helvetica-Bold", 9)
    c.drawString(50, y, "ÅRLIG BESPARING (ÅR 1)")
    c.drawString(225, y, "PAYBACK-TID")
    c.drawString(400, y, "NETTONYTTA (25 ÅR)")

    c.setFont("Helvetica-Bold", 16)
    c.setFillColor(colors.HexColor("#10b981"))
    c.drawString(50, y - 25, f"{besparing_ar1:,.0f} kr")
    
    c.setFillColor(colors.HexColor("#2563eb"))
    c.drawString(225, y - 25, payback_str)
    
    c.setFillColor(colors.HexColor("#10b981"))
    c.drawString(400, y - 25, f"{nettonytta_25ar:,.0f} kr")

    y -= 100
    c.setFillColor(colors.HexColor("#64748b"))
    c.setFont("Helvetica-Oblique", 8)
    c.drawString(40, y, "* Kalkylen baseras på schabloniserade beräkningar för solproduktion, effekttariffer och årlig degradering.")
    c.drawString(40, y - 12, "  Faktiskt utfall kan variera beroende på lokala väderförhållanden, elnätsavtal samt framtida elprisutveckling.")

    c.setFont("Helvetica", 9)
    c.drawString(40, 30, "EnergyIQ Platform • Ingenjörsmässig Energimodellering")

    c.showPage()
    c.save()
    
    buffer.seek(0)
    return buffer

# Huvud-banner
st.markdown("""
    <div class="main-header">
        <h1>EnergyIQ Platform</h1>
        <p>Avancerad energianalys, elområdeskarta, effekttariffer & degraderingsmodellering.</p>
    </div>
""", unsafe_allow_html=True)

# Navigation via 4 Flikar
tab1, tab2, tab3, tab4 = st.tabs(["Sverigekarta", "Stadsanalys", "Avancerad Ekonomi & ROI", "CO₂ & Klimatnytta"])

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
    st.markdown("### Interaktiv Elpriskarta över Sveriges Elområden")
    st.write("Klicka eller för muspekaren över regionerna för att se aktuella priser och ingående städer per elområde.")

    zon_stats = {}
    for z_kod in ["SE1", "SE2", "SE3", "SE4"]:
        z_data = hamta_zon_data(z_kod)
        if z_data:
            df_z = pd.DataFrame(z_data)
            snitt = df_z['SEK_per_kWh'].mean()
            max_p = df_z['SEK_per_kWh'].max()
            min_p = df_z['SEK_per_kWh'].min()
            nuvarande_timme = datetime.now().hour
            nu_pris = df_z['SEK_per_kWh'].iloc[nuvarande_timme] if nuvarande_timme < len(df_z) else snitt
            zon_stats[z_kod] = {"snitt": snitt, "nu": nu_pris, "max": max_p, "min": min_p}

    if zon_stats:
        c1, c2, c3, c4 = st.columns(4)
        meddelanden = [
            ("SE1 Norrbotten", "SE1", c1, "#3b82f6"),
            ("SE2 Sundsvall", "SE2", c2, "#10b981"),
            ("SE3 Sthlm / Gbg", "SE3", c3, "#f59e0b"),
            ("SE4 Malmö / Syd", "SE4", c4, "#ef4444")
        ]
        
        for titel, z_kod, col, farg in meddelanden:
            with col:
                st.markdown(f"""
                    <div class="metric-card" style="border-top: 6px solid {farg};">
                        <div class="metric-label">{titel}</div>
                        <div class="metric-value">{zon_stats[z_kod]['snitt']:.2f} kr</div>
                        <div class="metric-subtext">Just nu: <span style="color:{farg}; font-weight:700;">{zon_stats[z_kod]['nu']:.2f} kr/kWh</span></div>
                    </div>
                """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        m = folium.Map(location=[62.5, 16.5], zoom_start=5.0, tiles="cartodbpositron")

        REGION_POLYGONER = {
            "SE1": {
                "farg": "#3b82f6",
                "coords": [
                    [69.06, 20.55], [68.90, 21.00], [68.50, 22.20], [68.20, 23.10], [67.80, 23.60],
                    [66.50, 24.15], [65.80, 24.10], [65.50, 22.20], [65.20, 21.50], [65.00, 21.30],
                    [65.00, 18.00], [65.00, 15.00], [65.50, 14.50], [66.00, 14.70], [66.80, 15.50],
                    [67.80, 16.50], [68.40, 18.20], [69.06, 20.55]
                ],
                "namn": "SE1 – Norra Sverige",
                "stader": "Luleå, Kiruna, Boden, Piteå, Skellefteå"
            },
            "SE2": {
                "farg": "#10b981",
                "coords": [
                    [65.00, 15.00], [65.00, 18.00], [65.00, 21.30], [64.80, 21.00], [63.80, 20.30],
                    [62.80, 18.20], [61.70, 17.50], [60.60, 17.20], [60.60, 15.50], [60.60, 13.00],
                    [61.50, 12.20], [62.20, 12.00], [63.20, 12.00], [64.20, 13.80], [65.00, 15.00]
                ],
                "namn": "SE2 – Norra Mellansverige",
                "stader": "Sundsvall, Umeå, Östersund, Gävle, Härnösand"
            },
            "SE3": {
                "farg": "#f59e0b",
                "coords": [
                    [60.60, 13.00], [60.60, 15.50], [60.60, 17.20], [60.30, 18.00], [59.80, 19.00],
                    [58.90, 18.20], [58.60, 17.20], [57.30, 16.80], [57.30, 14.00], [57.30, 12.00],
                    [58.50, 11.20], [59.00, 11.20], [59.90, 12.20], [60.60, 13.00]
                ],
                "namn": "SE3 – Södra Mellansverige",
                "stader": "Stockholm, Göteborg, Uppsala, Västerås, Örebro"
            },
            "SE4": {
                "farg": "#ef4444",
                "coords": [
                    [57.30, 12.00], [57.30, 14.00], [57.30, 16.80], [56.60, 16.40], [56.10, 15.60],
                    [56.00, 14.80], [55.40, 14.20], [55.35, 13.30], [55.40, 12.80], [56.20, 12.50],
                    [56.50, 12.90], [57.30, 12.00]
                ],
                "namn": "SE4 – Södra Sverige",
                "stader": "Malmö, Helsingborg, Lund, Växjö, Karlskrona"
            }
        }

        for z_kod, reg in REGION_POLYGONER.items():
            stats = zon_stats[z_kod]
            popup_html = f"""
                <div style="font-family: Arial, sans-serif; width: 220px; padding: 4px;">
                    <h4 style="margin:0 0 6px 0; color:{reg['farg']};">{reg['namn']}</h4>
                    <p style="margin:2px 0;"><b>Medelpris idag:</b> {stats['snitt']:.2f} kr/kWh</p>
                    <p style="margin:2px 0; color:#ef4444;"><b>Högsta timpris:</b> {stats['max']:.2f} kr/kWh</p>
                    <p style="margin:2px 0; color:#10b981;"><b>Lägsta timpris:</b> {stats['min']:.2f} kr/kWh</p>
                    <hr style="margin:6px 0; border:0; border-top:1px solid #e2e8f0;">
                    <small style="color:#64748b;"><b>Ingående städer:</b><br>{reg['stader']}</small>
                </div>
            """

            folium.Polygon(
                locations=reg["coords"],
                color=reg["farg"],
                weight=2,
                fill=True,
                fill_color=reg["farg"],
                fill_opacity=0.45,
                popup=folium.Popup(popup_html, max_width=250),
                tooltip=f"{reg['namn']} — Medelpris: {stats['snitt']:.2f} kr/kWh"
            ).add_to(m)

        st_folium(m, width="100%", height=540)

    else:
        st.warning("Kunde inte hämta kartdata just nu.")

# ==========================================
# FLIK 2: STADSANALYS
# ==========================================
with tab2:
    st.markdown("### Dagsaktuella Timpriser per Stad / Kommun")
    col_sel1, col_sel2 = st.columns(2)
    with col_sel1:
        valdv_stad = st.selectbox(
            "Välj Stad / Kommun:", 
            options=sorted(list(STAD_TILL_ELOMRADE.keys())),
            index=sorted(list(STAD_TILL_ELOMRADE.keys())).index("Stockholm")
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
            st.markdown(f'<div class="metric-card" style="border-top: 5px solid #2563eb;"><div class="metric-label">Medelpris ({valdv_stad})</div><div class="metric-value">{snitt_pris:.2f} kr</div></div>', unsafe_allow_html=True)
        with c2:
            st.markdown(f'<div class="metric-card" style="border-top: 5px solid #ef4444;"><div class="metric-label">Högsta Timpris</div><div class="metric-value" style="color: #ef4444;">{max_pris:.2f} kr</div></div>', unsafe_allow_html=True)
        with c3:
            st.markdown(f'<div class="metric-card" style="border-top: 5px solid #10b981;"><div class="metric-label">Lägsta Timpris</div><div class="metric-value" style="color: #10b981;">{min_pris:.2f} kr</div></div>', unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.subheader(f"Prisvariation i {valdv_stad} idag")
        chart_data = df.set_index("Timme")[["SEK_per_kWh"]]
        st.line_chart(chart_data, height=350, use_container_width=True)

# ==========================================
# FLIK 3: AVANCERAD EKONOMI, EFFEKTTAXA & DEGRADERING
# ==========================================
with tab3:
    st.markdown("### Avancerad Investeringskalkylator (20–25 Års Livscykelmodell)")
    st.caption("Modellen tar hänsyn till solcellers och batteriers årliga degradering samt besparing via effekttariffer (peak shaving).")
    
    col_in1, col_in2, col_in3 = st.columns(3)
    with col_in1:
        st.markdown("#### 1. Solcellsanläggning")
        effekt_kw = st.number_input(
            "Installerad effekt (kWp):", min_value=1.0, max_value=100.0, value=10.0, step=0.5,
            help="Toppeffekt i kWp. Schablonen ger ~950 kWh/kWp år 1."
        )
        kostnad_sol = st.number_input(
            "Kostnad solceller (kr e. avdrag):", value=100000, step=5000,
            help="Nettokostnad efter 20% Grön Teknik-avdrag."
        )
        egenanvandning_pct = st.slider("Egenanvänd el (%):", 20, 80, 40)
        sol_degradering = st.slider("Årlig solcellsdegradering (%):", 0.1, 1.5, 0.5, step=0.1, help="Standard är ~0.5% effekttapp per år.")

    with col_in2:
        st.markdown("#### 2. Batterilagring")
        har_batteri = st.checkbox("Inkludera Batteri", value=True)
        if har_batteri:
            batteri_kwh = st.number_input("Batterikapacitet (kWh):", min_value=1.0, max_value=50.0, value=10.0, step=1.0)
            kostnad_batteri = st.number_input("Kostnad
