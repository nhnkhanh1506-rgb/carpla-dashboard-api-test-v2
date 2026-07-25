import streamlit as st


# ============================================================
# MÀU SẮC CHUNG
# ============================================================

BG_COLOR = "#EEF3F9"
TEXT_DARK = "#1F2937"
TEXT_MUTED = "#64748B"
CARD_BG = "#FFFFFF"
CARD_BORDER = "#DBE3EE"

PRIMARY_BLUE = "#3B6FD8"
PRIMARY_BLUE_DARK = "#2F5FBE"
PRIMARY_BLUE_LIGHT = "#7FA7E6"

LINE_BLUE = "#8EC5FF"
LINE_BLUE_SOFT = "#A8D3FF"
PCT_TEXT_COLOR = "#DCEEFF"
BAR_LABEL_COLOR = "#E45858"

CPUS_BAR_COLOR = "#FEDD65"
CPUS_BAR_BORDER = "#E7BE33"

REVENUE_BAR_COLOR = "#FE9E2C"
REVENUE_BAR_BORDER = "#E88713"

CUMULATIVE_LINE_COLOR = "#E45858"
CUMULATIVE_MARKER_COLOR = "#FFFFFF"
CUMULATIVE_MARKER_BORDER = "#E45858"

DAILY_CHART_BG = "#FFFFFF"
DAILY_CHART_GRID = "#E9ECF3"
DAILY_CHART_TEXT = "#1E2F6E"
DAILY_CHART_TITLE = "#1E2F6E"
DAILY_CHART_AXIS = "#59657A"

RED_MAIN = "#E45858"
RED_DARK = "#D64545"

DARK_PANEL = "#0B1530"
DARK_GRID = "rgba(255,255,255,0.10)"
WHITE = "#F8FAFC"

MUTED_BAR_COLORS = [
    "#335C99",
    "#426AA4",
    "#5278AF",
    "#6185BA",
    "#7193C4",
    "#80A0CE",
    "#90ADD7",
    "#9FB9DF",
    "#AFC6E7",
    "#BED2EE",
]

DONUT_MAIN = "#3C64A6"
DONUT_SECOND = "#9CC0DF"


# ============================================================
# ÁP DỤNG CSS CHO TOÀN BỘ APP
# ============================================================

def apply_global_style():
    st.markdown(
        f"""
<style>

/* =========================================================
   TOÀN BỘ ỨNG DỤNG
   ========================================================= */

.stApp {{
    background-color: {BG_COLOR};
}}

.block-container {{
    padding-top: 1.2rem;
    padding-bottom: 2rem;
    max-width: 1500px;
}}

h1,
h2,
h3 {{
    color: {TEXT_DARK};
    font-weight: 800 !important;
}}


/* =========================================================
   SIDEBAR
   ========================================================= */

[data-testid="stSidebar"] {{
    background:
        linear-gradient(
            180deg,
            #1F2937 0%,
            #111827 100%
        );
}}


/* Chỉ giữ chữ tiêu đề và nhãn trong sidebar màu trắng */
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] p {{
    color: white !important;
}}


/* =========================================================
   SELECTBOX TRONG SIDEBAR
   ========================================================= */

[data-testid="stSidebar"] div[data-baseweb="select"] > div {{
    background-color: white !important;
    border: 1px solid #D1D5DB !important;
    color: #111827 !important;
    min-height: 44px;
    border-radius: 10px !important;
}}


/* Chữ giá trị đang được chọn */
[data-testid="stSidebar"] div[data-baseweb="select"] span {{
    color: #111827 !important;
    -webkit-text-fill-color: #111827 !important;
}}


/* Input bên trong selectbox */
[data-testid="stSidebar"] div[data-baseweb="select"] input {{
    color: #111827 !important;
    -webkit-text-fill-color: #111827 !important;
    caret-color: #111827 !important;
}}


/* Placeholder */
[data-testid="stSidebar"] div[data-baseweb="select"] input::placeholder {{
    color: #64748B !important;
    -webkit-text-fill-color: #64748B !important;
    opacity: 1 !important;
}}


/* Mũi tên dropdown */
[data-testid="stSidebar"] div[data-baseweb="select"] svg {{
    fill: #475569 !important;
    color: #475569 !important;
}}


/* Viền khi selectbox được chọn */
[data-testid="stSidebar"] div[data-baseweb="select"] > div:focus-within {{
    border-color: #3B82F6 !important;
    box-shadow: 0 0 0 1px #3B82F6 !important;
}}


/* =========================================================
   DANH SÁCH DROPDOWN
   ========================================================= */

div[data-baseweb="popover"] {{
    color: #111827 !important;
}}

div[data-baseweb="popover"] ul {{
    background-color: white !important;
}}

div[data-baseweb="popover"] li {{
    color: #111827 !important;
    background-color: white !important;
}}

div[data-baseweb="popover"] li span {{
    color: #111827 !important;
    -webkit-text-fill-color: #111827 !important;
}}

div[data-baseweb="popover"] li:hover {{
    background-color: #E8F0FF !important;
    color: #111827 !important;
}}

div[data-baseweb="popover"] li:hover span {{
    color: #111827 !important;
    -webkit-text-fill-color: #111827 !important;
}}


/* =========================================================
   NÚT TRONG SIDEBAR
   ========================================================= */

[data-testid="stSidebar"] div.stButton > button {{
    min-height: 48px;
    border-radius: 14px;
    font-weight: 800;
    width: 100%;
}}


/* Nút XEM DASHBOARD */
[data-testid="stSidebar"] div.stButton > button[kind="primary"] {{
    background-color: #FF4B4B !important;
    color: white !important;
    border: 1px solid #FF4B4B !important;
}}

[data-testid="stSidebar"] div.stButton > button[kind="primary"] p {{
    color: white !important;
}}

[data-testid="stSidebar"] div.stButton > button[kind="primary"]:hover {{
    background-color: #E94242 !important;
    color: white !important;
    border-color: #E94242 !important;
}}

[data-testid="stSidebar"] div.stButton > button[kind="primary"]:hover p {{
    color: white !important;
}}


/* Nút TRANG CHỦ */
[data-testid="stSidebar"] div.stButton > button[kind="secondary"] {{
    background-color: #273449 !important;
    color: white !important;
    border: 1px solid #334155 !important;
}}

[data-testid="stSidebar"] div.stButton > button[kind="secondary"] p {{
    color: white !important;
}}

[data-testid="stSidebar"] div.stButton > button[kind="secondary"]:hover {{
    background-color: #334155 !important;
    color: white !important;
    border-color: #475569 !important;
}}

[data-testid="stSidebar"] div.stButton > button[kind="secondary"]:hover p {{
    color: white !important;
}}

[data-testid="stSidebar"] div.stButton > button[kind="secondary"]:disabled {{
    background-color: #273449 !important;
    color: white !important;
    opacity: 1 !important;
}}

[data-testid="stSidebar"] div.stButton > button[kind="secondary"]:disabled p {{
    color: white !important;
    opacity: 1 !important;
}}


/* =========================================================
   HERO BANNER
   ========================================================= */

.hero-box {{
    background:
        linear-gradient(
            135deg,
            #FFF7CC 0%,
            #FFE98A 18%,
            #FFD94D 38%,
            #FFE17A 58%,
            #FFF0A8 78%,
            #FFF7D6 100%
        );

    border-radius: 24px;
    padding: 28px 32px;
    margin-bottom: 24px;

    border: 1px solid rgba(255, 255, 255, 0.55);

    box-shadow:
        0 10px 30px rgba(201, 152, 0, 0.16),
        inset 0 1px 0 rgba(255, 255, 255, 0.35);
}}

.hero-title {{
    font-size: 42px;
    font-weight: 900;
    line-height: 1.1;
    margin-bottom: 8px;
    color: #1E2F6E;
}}

.hero-subtitle {{
    font-size: 15px;
    color: #44536B;
    font-weight: 600;
}}


/* =========================================================
   KPI CARDS
   ========================================================= */

.card {{
    background: {CARD_BG};
    border-radius: 22px;
    padding: 22px 24px;
    border: 1px solid {CARD_BORDER};

    box-shadow:
        0 8px 24px
        rgba(15, 23, 42, 0.06);

    min-height: 170px;
}}

.card-title {{
    font-size: 15px;
    font-weight: 700;
    color: {TEXT_MUTED};
    margin-bottom: 16px;
}}

.card-value {{
    font-size: 48px;
    font-weight: 900;
    color: #0F172A;
    line-height: 1;
    margin-bottom: 18px;
}}

.card-badge {{
    display: inline-block;
    padding: 8px 14px;
    border-radius: 999px;
    background: #E8F0FF;
    color: #1D4ED8;
    font-size: 13px;
    font-weight: 700;
}}


/* =========================================================
   PROGRESS CARDS
   ========================================================= */

.section-card {{
    background: {CARD_BG};
    border-radius: 22px;
    padding: 22px 22px 18px 22px;
    border: 1px solid {CARD_BORDER};

    box-shadow:
        0 8px 24px
        rgba(15, 23, 42, 0.05);

    min-height: 170px;
    margin-bottom: 22px;
}}

.progress-title {{
    font-size: 16px;
    font-weight: 800;
    color: {TEXT_DARK};
    margin-bottom: 14px;
}}

.progress-sub {{
    font-size: 15px;
    color: #475569;
    margin-bottom: 8px;
    font-weight: 600;
}}

.progress-track {{
    position: relative;
    width: 100%;
    height: 10px;
    background: #E5E7EB;
    border-radius: 999px;
    margin-top: 38px;
}}

.progress-fill {{
    height: 10px;

    background:
        linear-gradient(
            90deg,
            {RED_DARK},
            {RED_MAIN}
        );

    border-radius: 999px;
}}

.progress-dot {{
    position: absolute;
    top: -7px;
    width: 24px;
    height: 24px;
    background: {RED_MAIN};
    border: 4px solid white;
    border-radius: 50%;
    transform: translateX(-50%);

    box-shadow:
        0 6px 16px
        rgba(239, 68, 68, 0.22);
}}

.progress-label {{
    position: absolute;
    top: -34px;
    transform: translateX(-50%);
    font-size: 14px;
    font-weight: 800;
    color: {RED_MAIN};
    white-space: nowrap;
}}

.progress-scale {{
    display: flex;
    justify-content: space-between;
    font-size: 13px;
    font-weight: 700;
    color: {TEXT_MUTED};
    margin-top: 10px;
}}


/* =========================================================
   MINI KPI
   ========================================================= */

.mini-kpi {{
    background: {CARD_BG};
    border-radius: 18px;
    padding: 14px 18px;
    border: 1px solid {CARD_BORDER};

    box-shadow:
        0 8px 22px
        rgba(15, 23, 42, 0.05);

    margin-bottom: 10px;
}}

.mini-kpi-title {{
    font-size: 13px;
    font-weight: 800;
    color: {TEXT_MUTED};
    text-transform: uppercase;
    margin-bottom: 8px;
}}

.mini-kpi-value {{
    font-size: 30px;
    font-weight: 900;
    color: #0F172A;
    margin-bottom: 10px;
}}

.mini-kpi-badge {{
    display: inline-block;
    padding: 6px 10px;
    border-radius: 999px;
    background: #ECFEFF;
    color: #0F766E;
    font-size: 12px;
    font-weight: 700;
}}


/* =========================================================
   SECTION LABEL
   ========================================================= */

.section-label {{
    font-size: 17px;
    font-weight: 800;
    color: {TEXT_DARK};
    margin-bottom: 12px;
}}


/* =========================================================
   DATAFRAME
   ========================================================= */

div[data-testid="stDataFrame"] {{
    border-radius: 18px;
    overflow: hidden;
}}


/* =========================================================
   TRANG CHỦ MỚI - FULL YELLOW GRADIENT
   ========================================================= */

.homepage-stage {{
    position: relative;
    max-width: 1280px;
    margin: 0 auto;
    min-height: 680px;
    padding: 38px 28px 42px 28px;
    overflow: hidden;
    border-radius: 34px;

    background:
        linear-gradient(
            135deg,
            #FFF7CC 0%,
            #FFE98A 18%,
            #FFD94D 38%,
            #FFE17A 58%,
            #FFF0A8 78%,
            #FFF7D6 100%
        );

    box-shadow:
        inset 0 1px 0 rgba(255,255,255,0.35),
        0 18px 45px rgba(201, 152, 0, 0.14);
}}

.homepage-orb {{
    display: none;
}}

.orb-yellow {{
    display: none;
}}

.orb-blue {{
    display: none;
}}

.homepage-card {{
    position: relative;
    z-index: 2;
    max-width: 980px;
    margin: 0 auto;
    text-align: center;
    padding: 58px 56px 50px 56px;
    border-radius: 30px;

    background:
        linear-gradient(
            180deg,
            rgba(255,255,255,0.58) 0%,
            rgba(255,255,255,0.44) 100%
        );

    border: 1px solid rgba(255,255,255,0.55);

    backdrop-filter: blur(8px);
    -webkit-backdrop-filter: blur(8px);

    box-shadow:
        0 14px 30px rgba(120, 93, 0, 0.08);
}}

.homepage-title {{
    margin-top: 28px;
    font-size: 48px;
    line-height: 1.10;
    font-weight: 900;
    color: #1E2F6E;
    letter-spacing: 0.3px;
}}

.homepage-subtitle {{
    max-width: 820px;
    margin: 22px auto 0 auto;
    font-size: 20px;
    line-height: 1.82;
    color: #51627F;
    font-weight: 500;
}}

.homepage-guide {{
    max-width: 780px;
    margin: 30px auto 0 auto;
    font-size: 16px;
    line-height: 1.7;
    color: #3F4F68;
    font-weight: 650;
}}

/* =========================================================
   NÚT CHUNG NGOÀI SIDEBAR
   ========================================================= */

div.stButton > button {{
    min-height: 48px;
    border-radius: 14px;
    font-weight: 800;
}}

/* =========================================================
   NÚT THU GỌN SIDEBAR — MŨI TÊN TRẮNG SÁNG
   ========================================================= */

[data-testid="stSidebarCollapseButton"] {{
    opacity: 1 !important;
}}

[data-testid="stSidebarCollapseButton"] button {{
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    color: #FFFFFF !important;
    opacity: 1 !important;
}}

[data-testid="stSidebarCollapseButton"] button:hover {{
    background: rgba(255, 255, 255, 0.08) !important;
}}

[data-testid="stSidebarCollapseButton"] svg {{
    color: #FFFFFF !important;
    fill: #FFFFFF !important;
    stroke: #FFFFFF !important;
    opacity: 1 !important;
}}

[data-testid="stSidebarCollapseButton"] svg path {{
    color: #FFFFFF !important;
    fill: #FFFFFF !important;
    stroke: #FFFFFF !important;
    opacity: 1 !important;
}}

[data-testid="stSidebarCollapseButton"] * {{
    color: #FFFFFF !important;
    opacity: 1 !important;
}}


/* Dự phòng cho các phiên bản Streamlit khác */
button[data-testid="stSidebarCollapseButton"],
button[data-testid="stSidebarCollapseButton"] * {{
    color: #FFFFFF !important;
    fill: #FFFFFF !important;
    stroke: #FFFFFF !important;
    opacity: 1 !important;
}}

/* =========================================================
   CARD TARGET TƯƠNG TÁC — BẢN ỔN ĐỊNH
   ========================================================= */

.st-key-ro_target_card,
.st-key-revenue_target_card {{
    background: #FFFFFF !important;
    border-radius: 22px !important;
    padding: 22px 22px 18px 22px !important;
    border: 1px solid #DBE3EE !important;
    box-shadow: 0 8px 24px rgba(15, 23, 42, 0.05) !important;
    min-height: 190px !important;
    margin-bottom: 22px !important;
    overflow: visible !important;
}}

.st-key-ro_target_card .progress-title,
.st-key-revenue_target_card .progress-title {{
    font-size: 16px !important;
    font-weight: 800 !important;
    color: #1F2937 !important;
    margin-bottom: 14px !important;
}}

.st-key-ro_target_card .progress-sub,
.st-key-revenue_target_card .progress-sub {{
    font-size: 15px !important;
    color: #475569 !important;
    font-weight: 600 !important;
    margin-bottom: 30px !important;
}}

/* Slider thật, luôn kéo được */
.st-key-ro_target_card div[data-testid="stSlider"],
.st-key-revenue_target_card div[data-testid="stSlider"] {{
    position: relative !important;
    width: 100% !important;
    margin: 0 !important;
    padding: 0 !important;
    opacity: 1 !important;
    z-index: auto !important;
}}

/* Màu số phần trăm */
.st-key-ro_target_card [data-testid="stThumbValue"],
.st-key-revenue_target_card [data-testid="stThumbValue"] {{
    color: #E45858 !important;
    font-size: 14px !important;
    font-weight: 800 !important;
    white-space: nowrap !important;
}}

/* Nút slider */
.st-key-ro_target_card div[role="slider"],
.st-key-revenue_target_card div[role="slider"] {{
    background-color: #E45858 !important;
    border: 4px solid #FFFFFF !important;
    border-radius: 50% !important;
    box-shadow: 0 5px 14px rgba(228, 88, 88, 0.28) !important;
}}

/* Ẩn mốc mặc định vì có mốc cố định riêng */
.st-key-ro_target_card [data-testid="stTickBar"],
.st-key-revenue_target_card [data-testid="stTickBar"] {{
    display: none !important;
}}

/* 0% và 100% luôn hiển thị */
.slider-fixed-scale {{
    display: flex !important;
    justify-content: space-between !important;
    width: 100% !important;
    margin-top: 8px !important;
    color: #64748B !important;
    font-size: 13px !important;
    font-weight: 700 !important;
    line-height: 1 !important;
}}

.slider-fixed-scale span {{
    color: #64748B !important;
    opacity: 1 !important;
    visibility: visible !important;
}}

/* Thông báo bên dưới */
div[data-testid="stAlert"] {{
    border-radius: 14px !important;
}}

/* Nút reset bên dưới */
button[kind="secondary"] {{
    border-radius: 12px !important;
}}


/* =========================================================
   TOP HÃNG XE CHART
   Chỉ bo góc nền trắng, không đổi ngoại hình graph
   ========================================================= */

.st-key-brand_revenue_chart_card {{
    background: #FFFFFF;
    border-radius: 16px;
    overflow: hidden;
}}

.st-key-brand_revenue_chart_card
div[data-testid="stPlotlyChart"] {{
    background: #FFFFFF;
    border-radius: 16px;
    overflow: hidden;
}}

.st-key-brand_revenue_chart_card
.js-plotly-plot,
.st-key-brand_revenue_chart_card
.plot-container,
.st-key-brand_revenue_chart_card
.svg-container {{
    border-radius: 16px;
    overflow: hidden;
}}


/* =========================================================
   CƠ CẤU NGUỒN THANH TOÁN - DONUT CHART
   Chỉ bo 4 góc ô trắng, không đổi bố cục biểu đồ
   ========================================================= */

.st-key-payment_donut_card {{
    background: #FFFFFF !important;
    border-radius: 18px !important;
    overflow: hidden !important;
}}

.st-key-payment_donut_card > div {{
    border-radius: 18px !important;
    overflow: hidden !important;
}}

.st-key-payment_donut_card
div[data-testid="stPlotlyChart"] {{
    background: transparent !important;
    border-radius: 18px !important;
    overflow: hidden !important;
}}

.st-key-payment_donut_card
div[data-testid="stPlotlyChart"] > div {{
    background: transparent !important;
    border-radius: 18px !important;
    overflow: hidden !important;
}}

.st-key-payment_donut_card
.js-plotly-plot,
.st-key-payment_donut_card
.plot-container,
.st-key-payment_donut_card
.svg-container,
.st-key-payment_donut_card
.main-svg {{
    background: transparent !important;
    border-radius: 18px !important;
    overflow: hidden !important;
}}

/* =========================================================
   DAILY CHART CARDS - CARPLA SERVICE
   White cards, rounded corners, soft border and shadow
   ========================================================= */

.st-key-ro_daily_chart_card,
.st-key-revenue_daily_chart_card {{
    background: #FFFFFF !important;
    border: 1px solid #E9ECF3 !important;
    border-radius: 20px !important;
    overflow: hidden !important;
    box-shadow: 0 8px 24px rgba(30, 47, 110, 0.06) !important;
}}

.st-key-ro_daily_chart_card > div,
.st-key-revenue_daily_chart_card > div {{
    border-radius: 20px !important;
    overflow: hidden !important;
}}

.st-key-ro_daily_chart_card div[data-testid="stPlotlyChart"],
.st-key-revenue_daily_chart_card div[data-testid="stPlotlyChart"] {{
    background: transparent !important;
    border-radius: 20px !important;
    overflow: hidden !important;
}}

.st-key-ro_daily_chart_card .js-plotly-plot,
.st-key-ro_daily_chart_card .plot-container,
.st-key-ro_daily_chart_card .svg-container,
.st-key-ro_daily_chart_card .main-svg,
.st-key-revenue_daily_chart_card .js-plotly-plot,
.st-key-revenue_daily_chart_card .plot-container,
.st-key-revenue_daily_chart_card .svg-container,
.st-key-revenue_daily_chart_card .main-svg {{
    background: transparent !important;
    border-radius: 20px !important;
    overflow: hidden !important;
}}


</style>
""",
        unsafe_allow_html=True,
    )
