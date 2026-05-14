"""
India Pulse — Interactive Digital Payments Dashboard
=====================================================
Run:  streamlit run app.py
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import mysql.connector
import requests, json

# ──────────────────────────────────────────────
# CONFIG
# ──────────────────────────────────────────────
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "",
    "database": "phonepe",
}
INDIA_GEOJSON_URL = (
    "https://gist.githubusercontent.com/jbrobst/56c13bbbf9d97d187fea01ca62ea5112"
    "/raw/e388c4cae20aa53cb5090210a42ebb9b765c0a36/india_states.geojson"
)

st.set_page_config(
    page_title="India Pulse — Digital Payments Dashboard",
    page_icon="🇮🇳",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ──────────────────────────────────────────────
# GLOBAL THEME / CSS
# ──────────────────────────────────────────────
st.markdown(
    """
    <style>
    /* ── Google Font ── */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    /* ── Main background ── */
    .main .block-container {
        padding: 2rem 2.5rem 3rem 2.5rem;
        max-width: 1400px;
    }

    /* ── Sidebar ── */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
        border-right: 1px solid rgba(255,255,255,0.08);
    }
    [data-testid="stSidebar"] * {
        color: #e8e8f0 !important;
    }
    [data-testid="stSidebar"] .stSelectbox label,
    [data-testid="stSidebar"] .stRadio label {
        font-size: 0.8rem;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        color: #a0a0c0 !important;
    }
    [data-testid="stSidebar"] hr {
        border-color: rgba(255,255,255,0.12);
    }

    /* ── Sidebar radio nav pills ── */
    [data-testid="stSidebar"] [data-testid="stRadio"] > div {
        gap: 0.25rem;
    }
    [data-testid="stSidebar"] [data-testid="stRadio"] label {
        background: rgba(255,255,255,0.05);
        border-radius: 8px;
        padding: 0.5rem 0.9rem;
        transition: background 0.2s;
        font-size: 0.88rem !important;
        text-transform: none !important;
        letter-spacing: 0 !important;
    }
    [data-testid="stSidebar"] [data-testid="stRadio"] label:hover {
        background: rgba(255,255,255,0.12);
    }

    /* ── Page title banner ── */
    .page-title {
        background: linear-gradient(135deg, #6a0dad 0%, #9b59b6 60%, #3498db 100%);
        border-radius: 16px;
        padding: 1.8rem 2rem 1.4rem 2rem;
        margin-bottom: 1.8rem;
        color: #fff;
        box-shadow: 0 8px 32px rgba(106,13,173,0.25);
    }
    .page-title h1 {
        margin: 0 0 0.3rem 0;
        font-size: 2rem;
        font-weight: 800;
        letter-spacing: -0.02em;
    }
    .page-title p {
        margin: 0;
        opacity: 0.85;
        font-size: 0.95rem;
    }

    /* ── KPI metric cards ── */
    .kpi-row {
        display: flex;
        gap: 1.2rem;
        margin-bottom: 1.8rem;
        flex-wrap: wrap;
    }
    .kpi-card {
        flex: 1;
        min-width: 180px;
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        border: 1px solid rgba(155,89,182,0.3);
        border-radius: 16px;
        padding: 1.3rem 1.5rem;
        box-shadow: 0 4px 24px rgba(0,0,0,0.18);
        transition: transform 0.2s, box-shadow 0.2s;
    }
    .kpi-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 32px rgba(106,13,173,0.22);
    }
    .kpi-icon {
        font-size: 1.6rem;
        margin-bottom: 0.5rem;
    }
    .kpi-label {
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: #a0a0c0;
        margin-bottom: 0.3rem;
    }
    .kpi-value {
        font-size: 1.7rem;
        font-weight: 800;
        color: #e8e8f0;
        line-height: 1.1;
    }
    .kpi-sub {
        font-size: 0.78rem;
        color: #7a7aa0;
        margin-top: 0.25rem;
    }

    /* ── Section headers ── */
    .section-header {
        display: flex;
        align-items: center;
        gap: 0.6rem;
        margin: 1.6rem 0 1rem 0;
        padding-bottom: 0.6rem;
        border-bottom: 2px solid rgba(155,89,182,0.25);
    }
    .section-header span {
        font-size: 1.1rem;
        font-weight: 700;
        color: #c39bd3;
        letter-spacing: -0.01em;
    }

    /* ── Chart containers ── */
    .chart-card {
        background: rgba(26,26,46,0.6);
        border: 1px solid rgba(155,89,182,0.18);
        border-radius: 16px;
        padding: 1rem;
        margin-bottom: 1rem;
    }

    /* ── Streamlit metric override ── */
    [data-testid="metric-container"] {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        border: 1px solid rgba(155,89,182,0.3);
        border-radius: 14px;
        padding: 1.1rem 1.3rem;
        box-shadow: 0 4px 18px rgba(0,0,0,0.18);
    }
    [data-testid="metric-container"] label {
        font-size: 0.72rem !important;
        font-weight: 600 !important;
        text-transform: uppercase;
        letter-spacing: 0.07em;
        color: #a0a0c0 !important;
    }
    [data-testid="metric-container"] [data-testid="stMetricValue"] {
        font-size: 1.5rem !important;
        font-weight: 800 !important;
        color: #e8e8f0 !important;
    }

    /* ── Tab styling ── */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0.5rem;
        border-bottom: 2px solid rgba(155,89,182,0.2);
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 10px 10px 0 0;
        padding: 0.55rem 1.2rem;
        font-weight: 600;
        font-size: 0.88rem;
        color: #a0a0c0 !important;
        background: transparent !important;
        border: none !important;
    }
    .stTabs [aria-selected="true"] {
        color: #c39bd3 !important;
        background: rgba(155,89,182,0.12) !important;
        border-bottom: 2px solid #9b59b6 !important;
    }

    /* ── Dataframe ── */
    .stDataFrame {
        border-radius: 12px;
        overflow: hidden;
        border: 1px solid rgba(155,89,182,0.2) !important;
    }

    /* ── Expander ── */
    details {
        background: rgba(26,26,46,0.5);
        border: 1px solid rgba(155,89,182,0.2) !important;
        border-radius: 12px !important;
    }

    /* ── Info/warning banners ── */
    .stAlert {
        border-radius: 12px;
        border-left: 4px solid #9b59b6;
    }

    /* ── Footer ── */
    .footer-text {
        text-align: center;
        font-size: 0.75rem;
        color: #7a7aa0;
        margin-top: 3rem;
        padding-top: 1rem;
        border-top: 1px solid rgba(155,89,182,0.15);
    }

    /* ── Scrollbar ── */
    ::-webkit-scrollbar { width: 6px; height: 6px; }
    ::-webkit-scrollbar-track { background: #0f0c29; }
    ::-webkit-scrollbar-thumb { background: #5b2c8d; border-radius: 3px; }

    /* Dark background for the full app */
    .stApp {
        background: #0d0d1a;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ──────────────────────────────────────────────
# PLOTLY THEME DEFAULTS
# ──────────────────────────────────────────────
PLOTLY_LAYOUT = dict(
    paper_bgcolor="rgba(13,13,26,0)",
    plot_bgcolor="rgba(13,13,26,0)",
    font=dict(family="Inter", color="#c8c8e0"),
    title_font=dict(size=16, color="#e8e8f0", family="Inter"),
    legend=dict(
        bgcolor="rgba(26,26,46,0.8)",
        bordercolor="rgba(155,89,182,0.3)",
        borderwidth=1,
    ),
    xaxis=dict(gridcolor="rgba(155,89,182,0.15)", zerolinecolor="rgba(155,89,182,0.2)"),
    yaxis=dict(gridcolor="rgba(155,89,182,0.15)", zerolinecolor="rgba(155,89,182,0.2)"),
    coloraxis_colorbar=dict(
        tickfont=dict(color="#c8c8e0"),
        title_font=dict(color="#c8c8e0"),
    ),
)
PURPLE_SEQ = px.colors.sequential.Purples_r
PURPLE_DIV = px.colors.diverging.Tealrose


def apply_theme(fig):
    fig.update_layout(**PLOTLY_LAYOUT)
    return fig


# ──────────────────────────────────────────────
# DATABASE HELPER
# ──────────────────────────────────────────────
@st.cache_resource
def get_connection():
    return mysql.connector.connect(**DB_CONFIG)


def run_query(sql: str, params=None) -> pd.DataFrame:
    conn = get_connection()
    return pd.read_sql(sql, conn, params=params)


@st.cache_data(ttl=600)
def load_geojson():
    return requests.get(INDIA_GEOJSON_URL).json()


# ──────────────────────────────────────────────
# SIDEBAR — BRANDING + GLOBAL FILTERS
# ──────────────────────────────────────────────
st.sidebar.markdown(
    """
    <div style="text-align:center; padding: 1.2rem 0 0.8rem 0;">
        <div style="font-size:2.8rem; line-height:1;">🇮🇳</div>
        <div style="font-size:1.25rem; font-weight:800; color:#c39bd3;
                    letter-spacing:-0.02em; margin-top:0.5rem;">India Pulse</div>
        <div style="font-size:0.72rem; color:#7a7aa0; margin-top:0.2rem;
                    letter-spacing:0.06em; text-transform:uppercase;">
            Digital Payments Analytics
        </div>
    </div>
    <hr style="margin:0.8rem 0;"/>
    """,
    unsafe_allow_html=True,
)

years = run_query("SELECT DISTINCT year FROM aggregated_transaction ORDER BY year")["year"].tolist()
states_list = run_query("SELECT DISTINCT state FROM aggregated_transaction ORDER BY state")["state"].tolist()

st.sidebar.markdown(
    "<div style='font-size:0.72rem;font-weight:600;text-transform:uppercase;"
    "letter-spacing:0.08em;color:#7a7aa0;margin-bottom:0.4rem;'>Filters</div>",
    unsafe_allow_html=True,
)
selected_year = st.sidebar.selectbox("📅 Year", years, index=len(years) - 1)
selected_quarter = st.sidebar.selectbox("🗓️ Quarter", [1, 2, 3, 4])
selected_state = st.sidebar.selectbox("📍 State (drill-down)", ["All India"] + states_list)

st.sidebar.markdown("<hr/>", unsafe_allow_html=True)
st.sidebar.markdown(
    "<div style='font-size:0.72rem;font-weight:600;text-transform:uppercase;"
    "letter-spacing:0.08em;color:#7a7aa0;margin-bottom:0.4rem;'>Navigation</div>",
    unsafe_allow_html=True,
)

PAGES = [
    "🏠  Home",
    "📊  Aggregated Analysis",
    "🗺️  Geo Visualization",
    "🏆  Top Charts",
    "📈  Trend Analysis",
    "🛡️  Insurance Insights",
    "💡  Business Queries",
]
page = st.sidebar.radio("", PAGES, label_visibility="collapsed")

st.sidebar.markdown("<hr/>", unsafe_allow_html=True)
st.sidebar.markdown(
    f"<div style='font-size:0.72rem;color:#7a7aa0;text-align:center;'>"
    f"Viewing <b style='color:#c39bd3;'>Q{selected_quarter} {selected_year}</b><br/>"
    f"{'All India' if selected_state=='All India' else selected_state}</div>",
    unsafe_allow_html=True,
)


# ──────────────────────────────────────────────
# HELPERS
# ──────────────────────────────────────────────
def fmt_num(n):
    if n >= 1e9:  return f"₹{n/1e9:.2f} B"
    if n >= 1e7:  return f"₹{n/1e7:.2f} Cr"
    if n >= 1e5:  return f"₹{n/1e5:.2f} L"
    return f"₹{n:,.0f}"


def fmt_count(n):
    if n >= 1e7: return f"{n/1e7:.2f} Cr"
    if n >= 1e5: return f"{n/1e5:.2f} L"
    if n >= 1e3: return f"{n/1e3:.1f} K"
    return f"{n:,.0f}"


def page_banner(icon: str, title: str, subtitle: str = ""):
    st.markdown(
        f"""<div class="page-title">
            <h1>{icon} {title}</h1>
            {"<p>" + subtitle + "</p>" if subtitle else ""}
        </div>""",
        unsafe_allow_html=True,
    )


def section_header(icon: str, label: str):
    st.markdown(
        f'<div class="section-header"><span>{icon} {label}</span></div>',
        unsafe_allow_html=True,
    )


# ──────────────────────────────────────────────
# PAGE: HOME
# ──────────────────────────────────────────────
def page_home():
    page_banner(
        "🇮🇳", "India Pulse",
        "India's digital payment revolution — visualised & explored"
    )

    # KPI cards
    kpi_sql = """
        SELECT SUM(transaction_count) AS total_txns,
               SUM(transaction_amount) AS total_amount,
               COUNT(DISTINCT state) AS states
        FROM aggregated_transaction
        WHERE year = %s AND quarter = %s
    """
    kpi = run_query(kpi_sql, (selected_year, selected_quarter)).iloc[0]

    user_sql = """
        SELECT SUM(registered_users) AS reg_users, SUM(app_opens) AS opens
        FROM (
            SELECT state, year, quarter,
                   MAX(registered_users) AS registered_users,
                   MAX(app_opens) AS app_opens
            FROM aggregated_user
            WHERE year = %s AND quarter = %s
            GROUP BY state, year, quarter
        ) sub
    """
    user_kpi = run_query(user_sql, (selected_year, selected_quarter)).iloc[0]

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("💳 Total Transactions", fmt_count(kpi["total_txns"] or 0))
    c2.metric("💰 Total Amount", fmt_num(kpi["total_amount"] or 0))
    c3.metric("👤 Registered Users", fmt_count(user_kpi["reg_users"] or 0))
    c4.metric("📱 App Opens", fmt_count(user_kpi["opens"] or 0))

    st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)

    # Mini trend sparkline
    section_header("📈", "Transaction Trend — All Quarters")
    df_spark = run_query(
        """
        SELECT year, quarter,
               SUM(transaction_count) AS total_count,
               SUM(transaction_amount) AS total_amount
        FROM aggregated_transaction
        GROUP BY year, quarter
        ORDER BY year, quarter
        """
    )
    if not df_spark.empty:
        df_spark["period"] = df_spark["year"].astype(str) + "-Q" + df_spark["quarter"].astype(str)
        col_a, col_b = st.columns(2)
        with col_a:
            fig = px.area(
                df_spark, x="period", y="total_amount",
                title="Total Transaction Amount Over Time",
                color_discrete_sequence=["#9b59b6"],
            )
            fig.update_traces(fill="tozeroy", line_width=2.5)
            apply_theme(fig)
            fig.update_layout(xaxis_tickangle=-40, height=280, margin=dict(t=40, b=40))
            st.plotly_chart(fig, use_container_width=True)
        with col_b:
            fig2 = px.area(
                df_spark, x="period", y="total_count",
                title="Total Transaction Count Over Time",
                color_discrete_sequence=["#3498db"],
            )
            fig2.update_traces(fill="tozeroy", line_width=2.5)
            apply_theme(fig2)
            fig2.update_layout(xaxis_tickangle=-40, height=280, margin=dict(t=40, b=40))
            st.plotly_chart(fig2, use_container_width=True)

    # About cards
    section_header("📋", "Dashboard Coverage")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(
            """<div class="kpi-card">
            <div class="kpi-icon">💳</div>
            <div class="kpi-label">Transactions</div>
            <div style="font-size:0.88rem;color:#c8c8e0;margin-top:0.4rem;">
                Aggregated by type, state, district & pincode across all years.
            </div></div>""",
            unsafe_allow_html=True,
        )
    with col2:
        st.markdown(
            """<div class="kpi-card">
            <div class="kpi-icon">👤</div>
            <div class="kpi-label">Users</div>
            <div style="font-size:0.88rem;color:#c8c8e0;margin-top:0.4rem;">
                Registrations, app opens, and device brand analytics.
            </div></div>""",
            unsafe_allow_html=True,
        )
    with col3:
        st.markdown(
            """<div class="kpi-card">
            <div class="kpi-icon">🛡️</div>
            <div class="kpi-label">Insurance</div>
            <div style="font-size:0.88rem;color:#c8c8e0;margin-top:0.4rem;">
                Policy counts, premium amounts, and penetration maps.
            </div></div>""",
            unsafe_allow_html=True,
        )

    st.markdown(
        f"<div class='footer-text'>Showing data for <b>Q{selected_quarter} {selected_year}</b> "
        f"— use the sidebar to change filters and explore pages.</div>",
        unsafe_allow_html=True,
    )


# ──────────────────────────────────────────────
# PAGE: AGGREGATED ANALYSIS
# ──────────────────────────────────────────────
def page_aggregated():
    page_banner("📊", "Aggregated Analysis",
                "Transaction types and user device breakdown")

    tab1, tab2 = st.tabs(["💳  Transactions", "👤  Users"])

    # ── Transactions ──
    with tab1:
        section_header("🔍", "Transaction Type Breakdown")
        where = "WHERE year = %s AND quarter = %s"
        params = [selected_year, selected_quarter]
        if selected_state != "All India":
            where += " AND state = %s"
            params.append(selected_state)

        df = run_query(
            f"""
            SELECT transaction_type,
                   SUM(transaction_count)  AS count,
                   SUM(transaction_amount) AS amount
            FROM aggregated_transaction
            {where}
            GROUP BY transaction_type
            ORDER BY amount DESC
            """,
            tuple(params),
        )

        if df.empty:
            st.warning("No data available for this selection.")
            return

        col1, col2 = st.columns(2)
        with col1:
            fig = px.pie(
                df, names="transaction_type", values="count",
                title="Transaction Count Share",
                hole=0.5,
                color_discrete_sequence=PURPLE_SEQ,
            )
            fig.update_traces(textposition="outside", textinfo="percent+label")
            apply_theme(fig)
            fig.update_layout(height=380, margin=dict(t=40))
            st.plotly_chart(fig, use_container_width=True)
        with col2:
            fig = px.bar(
                df, x="transaction_type", y="amount",
                title="Transaction Amount by Type",
                color="amount",
                color_continuous_scale="Purples",
            )
            fig.update_layout(showlegend=False, xaxis_title="", yaxis_title="Amount (₹)",
                               height=380, margin=dict(t=40))
            apply_theme(fig)
            st.plotly_chart(fig, use_container_width=True)

        section_header("📋", "Detailed Table")
        st.dataframe(
            df.style.format({"count": "{:,.0f}", "amount": "₹{:,.2f}"}),
            use_container_width=True,
        )

    # ── Users ──
    with tab2:
        section_header("📱", "Device Brand Distribution")
        where = "WHERE year = %s AND quarter = %s AND brand IS NOT NULL"
        params = [selected_year, selected_quarter]
        if selected_state != "All India":
            where += " AND state = %s"
            params.append(selected_state)

        df_dev = run_query(
            f"""
            SELECT brand, SUM(user_count) AS count
            FROM aggregated_user
            {where}
            GROUP BY brand
            ORDER BY count DESC
            LIMIT 15
            """,
            tuple(params),
        )

        if not df_dev.empty:
            fig = px.bar(
                df_dev, x="brand", y="count",
                title="Top 15 Device Brands by User Count",
                color="count",
                color_continuous_scale="Purples",
            )
            apply_theme(fig)
            fig.update_layout(xaxis_title="Brand", yaxis_title="Users", height=380)
            st.plotly_chart(fig, use_container_width=True)

        section_header("🗺️", "Registered Users by State")
        df_users = run_query(
            """
            SELECT state,
                   MAX(registered_users) AS registered_users,
                   MAX(app_opens) AS app_opens
            FROM aggregated_user
            WHERE year = %s AND quarter = %s
            GROUP BY state
            ORDER BY registered_users DESC
            """,
            (selected_year, selected_quarter),
        )
        col1, col2 = st.columns(2)
        with col1:
            fig = px.bar(
                df_users.head(15), x="state", y="registered_users",
                title="Top 15 States — Registered Users",
                color="registered_users",
                color_continuous_scale="Purples",
            )
            apply_theme(fig)
            fig.update_layout(xaxis_tickangle=-45, height=380)
            st.plotly_chart(fig, use_container_width=True)
        with col2:
            fig2 = px.bar(
                df_users.head(15), x="state", y="app_opens",
                title="Top 15 States — App Opens",
                color="app_opens",
                color_continuous_scale="Blues",
            )
            apply_theme(fig2)
            fig2.update_layout(xaxis_tickangle=-45, height=380)
            st.plotly_chart(fig2, use_container_width=True)


# ──────────────────────────────────────────────
# PAGE: GEO VISUALIZATION
# ──────────────────────────────────────────────
def page_geo():
    page_banner("🗺️", "Geo Visualization",
                "State-level choropleth maps across key metrics")

    geo_type = st.radio(
        "Select Metric",
        ["Transaction Amount", "Transaction Count", "Registered Users", "Insurance Amount"],
        horizontal=True,
    )

    geojson = load_geojson()

    if geo_type in ["Transaction Amount", "Transaction Count"]:
        df = run_query(
            """
            SELECT state,
                   SUM(transaction_count)  AS transaction_count,
                   SUM(transaction_amount) AS transaction_amount
            FROM aggregated_transaction
            WHERE year = %s AND quarter = %s
            GROUP BY state
            """,
            (selected_year, selected_quarter),
        )
        color_col = "transaction_amount" if "Amount" in geo_type else "transaction_count"
    elif geo_type == "Registered Users":
        df = run_query(
            """
            SELECT state, SUM(registered_users) AS registered_users
            FROM map_user
            WHERE year = %s AND quarter = %s
            GROUP BY state
            """,
            (selected_year, selected_quarter),
        )
        color_col = "registered_users"
    else:
        df = run_query(
            """
            SELECT state,
                   SUM(transaction_count) AS transaction_count,
                   SUM(transaction_amount) AS transaction_amount
            FROM aggregated_insurance
            WHERE year = %s AND quarter = %s
            GROUP BY state
            """,
            (selected_year, selected_quarter),
        )
        color_col = "transaction_amount"

    if df.empty:
        st.warning("No data for this selection.")
        return

    fig = px.choropleth(
        df,
        geojson=geojson,
        featureidkey="properties.ST_NM",
        locations="state",
        color=color_col,
        color_continuous_scale="Purples",
        title=f"{geo_type} — Q{selected_quarter} {selected_year}",
        hover_data=df.columns.tolist(),
    )
    fig.update_geos(fitbounds="locations", visible=False)
    fig.update_layout(height=700, margin={"r": 0, "t": 40, "l": 0, "b": 0})
    apply_theme(fig)
    st.plotly_chart(fig, use_container_width=True)

    # District breakdown
    if selected_state != "All India":
        section_header("📊", f"District Breakdown — {selected_state}")
        df_dist = run_query(
            """
            SELECT district,
                   SUM(transaction_count) AS txn_count,
                   SUM(transaction_amount) AS txn_amount
            FROM map_transaction
            WHERE year = %s AND quarter = %s AND state = %s
            GROUP BY district
            ORDER BY txn_amount DESC
            LIMIT 20
            """,
            (selected_year, selected_quarter, selected_state),
        )
        if not df_dist.empty:
            fig2 = px.bar(
                df_dist, x="district", y="txn_amount",
                color="txn_count",
                color_continuous_scale="Purples",
                title=f"Top 20 Districts in {selected_state}",
            )
            apply_theme(fig2)
            fig2.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig2, use_container_width=True)


# ──────────────────────────────────────────────
# PAGE: TOP CHARTS
# ──────────────────────────────────────────────
def page_top():
    page_banner("🏆", "Top Performers",
                "Rankings across states, districts, and pin codes")

    tab1, tab2, tab3 = st.tabs(["🗺️  States", "🏙️  Districts", "📮  Pin Codes"])

    with tab1:
        section_header("🏅", "Top 10 States by Transaction Amount")
        df = run_query(
            """
            SELECT state,
                   SUM(transaction_count)  AS total_count,
                   SUM(transaction_amount) AS total_amount
            FROM aggregated_transaction
            WHERE year = %s AND quarter = %s
            GROUP BY state
            ORDER BY total_amount DESC
            LIMIT 10
            """,
            (selected_year, selected_quarter),
        )
        if not df.empty:
            fig = px.bar(
                df, x="total_amount", y="state", orientation="h",
                color="total_amount", color_continuous_scale="Purples",
                title="Top 10 States by Transaction Amount",
                text=df["total_amount"].apply(fmt_num),
            )
            apply_theme(fig)
            fig.update_traces(textposition="outside")
            fig.update_layout(yaxis={"categoryorder": "total ascending"}, height=440)
            st.plotly_chart(fig, use_container_width=True)
            st.dataframe(
                df.style.format({"total_count": "{:,.0f}", "total_amount": "₹{:,.2f}"}),
                use_container_width=True,
            )

    with tab2:
        section_header("🏙️", "Top 10 Districts by Transaction Amount")
        df = run_query(
            """
            SELECT entity_name AS district, state,
                   SUM(transaction_count)  AS total_count,
                   SUM(transaction_amount) AS total_amount
            FROM top_transaction
            WHERE year = %s AND quarter = %s AND entity_type = 'district'
            GROUP BY entity_name, state
            ORDER BY total_amount DESC
            LIMIT 10
            """,
            (selected_year, selected_quarter),
        )
        if not df.empty:
            fig = px.bar(
                df, x="total_amount", y="district", orientation="h",
                color="state", title="Top 10 Districts",
            )
            apply_theme(fig)
            fig.update_layout(yaxis={"categoryorder": "total ascending"}, height=440)
            st.plotly_chart(fig, use_container_width=True)
            st.dataframe(df, use_container_width=True)

    with tab3:
        section_header("📮", "Top 10 Pin Codes by Transaction Amount")
        df = run_query(
            """
            SELECT entity_name AS pincode, state,
                   SUM(transaction_count)  AS total_count,
                   SUM(transaction_amount) AS total_amount
            FROM top_transaction
            WHERE year = %s AND quarter = %s AND entity_type = 'pincode'
            GROUP BY entity_name, state
            ORDER BY total_amount DESC
            LIMIT 10
            """,
            (selected_year, selected_quarter),
        )
        if not df.empty:
            fig = px.bar(
                df, x="total_amount", y="pincode", orientation="h",
                color="state", title="Top 10 Pin Codes",
            )
            apply_theme(fig)
            fig.update_layout(yaxis={"categoryorder": "total ascending"}, height=440)
            st.plotly_chart(fig, use_container_width=True)
            st.dataframe(df, use_container_width=True)


# ──────────────────────────────────────────────
# PAGE: TREND ANALYSIS
# ──────────────────────────────────────────────
def page_trends():
    page_banner("📈", "Trend Analysis",
                "Quarterly and year-over-year transaction & user growth")

    where = ""
    params: list = []
    if selected_state != "All India":
        where = "WHERE state = %s"
        params = [selected_state]

    section_header("📉", "Quarterly Transaction Trend")
    df = run_query(
        f"""
        SELECT year, quarter,
               SUM(transaction_count)  AS total_count,
               SUM(transaction_amount) AS total_amount
        FROM aggregated_transaction
        {where}
        GROUP BY year, quarter
        ORDER BY year, quarter
        """,
        tuple(params) if params else None,
    )

    if not df.empty:
        df["period"] = df["year"].astype(str) + "-Q" + df["quarter"].astype(str)
        col1, col2 = st.columns(2)
        with col1:
            fig = px.line(
                df, x="period", y="total_amount", markers=True,
                title="Transaction Amount Over Time",
                color_discrete_sequence=["#9b59b6"],
            )
            apply_theme(fig)
            fig.update_layout(xaxis_tickangle=-40, height=320)
            st.plotly_chart(fig, use_container_width=True)
        with col2:
            fig = px.line(
                df, x="period", y="total_count", markers=True,
                title="Transaction Count Over Time",
                color_discrete_sequence=["#3498db"],
            )
            apply_theme(fig)
            fig.update_layout(xaxis_tickangle=-40, height=320)
            st.plotly_chart(fig, use_container_width=True)

    section_header("📊", "Year-over-Year Growth")
    df_yoy = run_query(
        f"""
        SELECT year,
               SUM(transaction_count)  AS total_count,
               SUM(transaction_amount) AS total_amount
        FROM aggregated_transaction
        {where}
        GROUP BY year
        ORDER BY year
        """,
        tuple(params) if params else None,
    )
    if not df_yoy.empty:
        df_yoy["amount_growth_%"] = df_yoy["total_amount"].pct_change() * 100
        df_yoy["count_growth_%"] = df_yoy["total_count"].pct_change() * 100

        col1, col2 = st.columns(2)
        with col1:
            fig = px.bar(
                df_yoy, x="year", y="total_amount",
                title="Yearly Transaction Amount",
                color="total_amount",
                color_continuous_scale="Purples",
                text=df_yoy["total_amount"].apply(fmt_num),
            )
            apply_theme(fig)
            fig.update_traces(textposition="outside")
            st.plotly_chart(fig, use_container_width=True)
        with col2:
            fig2 = px.bar(
                df_yoy.dropna(subset=["amount_growth_%"]),
                x="year", y="amount_growth_%",
                title="YoY Growth (%)",
                color="amount_growth_%",
                color_continuous_scale="RdYlGn",
                text=df_yoy.dropna(subset=["amount_growth_%"])["amount_growth_%"].apply(
                    lambda v: f"{v:+.1f}%"
                ),
            )
            apply_theme(fig2)
            fig2.update_traces(textposition="outside")
            st.plotly_chart(fig2, use_container_width=True)

        st.dataframe(
            df_yoy.style.format({
                "total_count": "{:,.0f}",
                "total_amount": "₹{:,.2f}",
                "amount_growth_%": "{:+.2f}%",
                "count_growth_%": "{:+.2f}%",
            }),
            use_container_width=True,
        )

    section_header("👤", "User Registration Trend")
    df_reg = run_query(
        f"""
        SELECT year, quarter, SUM(reg) AS registered_users
        FROM (
            SELECT state, year, quarter, MAX(registered_users) AS reg
            FROM aggregated_user
            {"WHERE state = %s" if selected_state != "All India" else ""}
            GROUP BY state, year, quarter
        ) sub
        GROUP BY year, quarter
        ORDER BY year, quarter
        """,
        (selected_state,) if selected_state != "All India" else None,
    )
    if not df_reg.empty:
        df_reg["period"] = df_reg["year"].astype(str) + "-Q" + df_reg["quarter"].astype(str)
        fig = px.area(
            df_reg, x="period", y="registered_users",
            title="Cumulative Registered Users Growth",
            color_discrete_sequence=["#8e44ad"],
        )
        fig.update_traces(fill="tozeroy", line_width=2.5)
        apply_theme(fig)
        fig.update_layout(xaxis_tickangle=-40, height=320)
        st.plotly_chart(fig, use_container_width=True)


# ──────────────────────────────────────────────
# PAGE: INSURANCE INSIGHTS
# ──────────────────────────────────────────────
def page_insurance():
    page_banner("🛡️", "Insurance Insights",
                "Policy counts, premium collection, and penetration maps")

    col1, col2 = st.columns(2)
    with col1:
        section_header("🏅", "Top 10 States — Insurance Premium")
        df = run_query(
            """
            SELECT state,
                   SUM(transaction_count)  AS policy_count,
                   SUM(transaction_amount) AS premium_amount
            FROM aggregated_insurance
            WHERE year = %s AND quarter = %s
            GROUP BY state
            ORDER BY premium_amount DESC
            LIMIT 10
            """,
            (selected_year, selected_quarter),
        )
        if not df.empty:
            fig = px.bar(
                df, x="premium_amount", y="state", orientation="h",
                color="premium_amount", color_continuous_scale="Purples",
                text=df["premium_amount"].apply(fmt_num),
            )
            apply_theme(fig)
            fig.update_layout(yaxis={"categoryorder": "total ascending"}, height=400)
            st.plotly_chart(fig, use_container_width=True)

    with col2:
        section_header("🏙️", "Top 10 Districts — Insurance")
        df = run_query(
            """
            SELECT district, state,
                   SUM(transaction_count)  AS policy_count,
                   SUM(transaction_amount) AS premium_amount
            FROM map_insurance
            WHERE year = %s AND quarter = %s
            GROUP BY district, state
            ORDER BY premium_amount DESC
            LIMIT 10
            """,
            (selected_year, selected_quarter),
        )
        if not df.empty:
            fig = px.bar(
                df, x="premium_amount", y="district", orientation="h",
                color="state",
            )
            apply_theme(fig)
            fig.update_layout(yaxis={"categoryorder": "total ascending"}, height=400)
            st.plotly_chart(fig, use_container_width=True)

    section_header("📈", "Insurance Premium — Quarterly Trend")
    df_trend = run_query(
        """
        SELECT year, quarter,
               SUM(transaction_count)  AS policy_count,
               SUM(transaction_amount) AS premium_amount
        FROM aggregated_insurance
        GROUP BY year, quarter
        ORDER BY year, quarter
        """
    )
    if not df_trend.empty:
        df_trend["period"] = (
            df_trend["year"].astype(str) + "-Q" + df_trend["quarter"].astype(str)
        )
        col_a, col_b = st.columns(2)
        with col_a:
            fig = px.line(
                df_trend, x="period", y="premium_amount", markers=True,
                title="Insurance Premium Over Time",
                color_discrete_sequence=["#6c3483"],
            )
            apply_theme(fig)
            fig.update_layout(xaxis_tickangle=-45, height=320)
            st.plotly_chart(fig, use_container_width=True)
        with col_b:
            fig2 = px.line(
                df_trend, x="period", y="policy_count", markers=True,
                title="Policy Count Over Time",
                color_discrete_sequence=["#117a65"],
            )
            apply_theme(fig2)
            fig2.update_layout(xaxis_tickangle=-45, height=320)
            st.plotly_chart(fig2, use_container_width=True)

    section_header("🗺️", "Insurance Penetration Map")
    geojson = load_geojson()
    df_map = run_query(
        """
        SELECT state,
               SUM(transaction_count) AS policy_count,
               SUM(transaction_amount) AS premium_amount
        FROM aggregated_insurance
        WHERE year = %s AND quarter = %s
        GROUP BY state
        """,
        (selected_year, selected_quarter),
    )
    if not df_map.empty:
        fig = px.choropleth(
            df_map, geojson=geojson,
            featureidkey="properties.ST_NM",
            locations="state",
            color="premium_amount",
            color_continuous_scale="Purples",
            title="Insurance Premium by State",
        )
        fig.update_geos(fitbounds="locations", visible=False)
        fig.update_layout(height=620, margin={"r": 0, "t": 40, "l": 0, "b": 0})
        apply_theme(fig)
        st.plotly_chart(fig, use_container_width=True)


# ──────────────────────────────────────────────
# PAGE: BUSINESS QUERIES
# ──────────────────────────────────────────────
BUSINESS_QUERIES = {
    "1. Top 10 States by Transaction Amount": """
        SELECT state,
               SUM(transaction_amount) AS total_amount,
               SUM(transaction_count) AS total_count
        FROM aggregated_transaction
        WHERE year = {year} AND quarter = {quarter}
        GROUP BY state
        ORDER BY total_amount DESC
        LIMIT 10;
    """,
    "2. Transaction Type Market Share (%)": """
        SELECT transaction_type,
               SUM(transaction_count) AS count,
               ROUND(SUM(transaction_count) * 100.0 /
                     (SELECT SUM(transaction_count)
                      FROM aggregated_transaction
                      WHERE year = {year} AND quarter = {quarter}), 2) AS market_share_pct
        FROM aggregated_transaction
        WHERE year = {year} AND quarter = {quarter}
        GROUP BY transaction_type
        ORDER BY count DESC;
    """,
    "3. Average Transaction Value by State": """
        SELECT state,
               ROUND(SUM(transaction_amount) / SUM(transaction_count), 2) AS avg_txn_value
        FROM aggregated_transaction
        WHERE year = {year} AND quarter = {quarter}
        GROUP BY state
        ORDER BY avg_txn_value DESC
        LIMIT 10;
    """,
    "4. Year-over-Year Growth by State": """
        SELECT curr.state,
               prev.total_amount AS prev_year_amount,
               curr.total_amount AS curr_year_amount,
               ROUND((curr.total_amount - prev.total_amount) * 100.0
                      / prev.total_amount, 2) AS growth_pct
        FROM (SELECT state, SUM(transaction_amount) AS total_amount
              FROM aggregated_transaction
              WHERE year = {year}
              GROUP BY state) curr
        JOIN (SELECT state, SUM(transaction_amount) AS total_amount
              FROM aggregated_transaction
              WHERE year = {year} - 1
              GROUP BY state) prev
        ON curr.state = prev.state
        ORDER BY growth_pct DESC
        LIMIT 10;
    """,
    "5. Top 10 Districts by Transaction Volume": """
        SELECT district, state,
               SUM(transaction_count) AS total_count,
               SUM(transaction_amount) AS total_amount
        FROM map_transaction
        WHERE year = {year} AND quarter = {quarter}
        GROUP BY district, state
        ORDER BY total_count DESC
        LIMIT 10;
    """,
    "6. Device Brand Popularity Ranking": """
        SELECT brand,
               SUM(user_count) AS total_users
        FROM aggregated_user
        WHERE year = {year} AND quarter = {quarter}
          AND brand IS NOT NULL
        GROUP BY brand
        ORDER BY total_users DESC
        LIMIT 10;
    """,
    "7. Top 10 Pin Codes by Registered Users": """
        SELECT entity_name AS pincode, state,
               SUM(registered_users) AS total_users
        FROM top_user
        WHERE year = {year} AND quarter = {quarter}
          AND entity_type = 'pincode'
        GROUP BY entity_name, state
        ORDER BY total_users DESC
        LIMIT 10;
    """,
    "8. States With Highest Insurance Penetration": """
        SELECT i.state,
               SUM(i.transaction_count)  AS insurance_policies,
               SUM(i.transaction_amount) AS premium_collected,
               SUM(t.transaction_count)  AS total_transactions,
               ROUND(SUM(i.transaction_count) * 100.0
                     / SUM(t.transaction_count), 4) AS insurance_pct
        FROM aggregated_insurance i
        JOIN (SELECT state, year, quarter,
                     SUM(transaction_count) AS transaction_count
              FROM aggregated_transaction
              GROUP BY state, year, quarter) t
          ON i.state = t.state AND i.year = t.year AND i.quarter = t.quarter
        WHERE i.year = {year} AND i.quarter = {quarter}
        GROUP BY i.state
        ORDER BY insurance_pct DESC
        LIMIT 10;
    """,
    "9. Quarterly Transaction Trend (All Years)": """
        SELECT year, quarter,
               SUM(transaction_count)  AS total_count,
               SUM(transaction_amount) AS total_amount,
               ROUND(SUM(transaction_amount) / SUM(transaction_count), 2) AS avg_value
        FROM aggregated_transaction
        GROUP BY year, quarter
        ORDER BY year, quarter;
    """,
    "10. Low-Activity States (Potential Growth Markets)": """
        SELECT state,
               SUM(transaction_count)  AS total_count,
               SUM(transaction_amount) AS total_amount
        FROM aggregated_transaction
        WHERE year = {year} AND quarter = {quarter}
        GROUP BY state
        ORDER BY total_amount ASC
        LIMIT 10;
    """,
}


def page_business_queries():
    page_banner("💡", "Business Case SQL Queries",
                "Pre-built analytical queries with auto-visualisation")

    query_name = st.selectbox("📋 Select a Business Query", list(BUSINESS_QUERIES.keys()))
    raw_sql = BUSINESS_QUERIES[query_name]
    sql = raw_sql.format(year=selected_year, quarter=selected_quarter)

    col_info, col_btn = st.columns([4, 1])
    with col_info:
        st.info(
            f"Running **{query_name}** for **Q{selected_quarter} {selected_year}**"
        )

    with st.expander("🔍 View SQL Query"):
        st.code(sql, language="sql")

    try:
        df = run_query(sql)

        if df.empty:
            st.warning("No results returned for this query and filter combination.")
            return

        section_header("📋", "Query Results")
        st.dataframe(df, use_container_width=True)

        # Auto visualisation
        if len(df.columns) >= 2:
            num_cols = df.select_dtypes("number").columns.tolist()
            cat_cols = df.select_dtypes(exclude="number").columns.tolist()
            if cat_cols and num_cols:
                section_header("📊", "Auto Visualisation")
                col_sel1, col_sel2 = st.columns(2)
                with col_sel1:
                    chosen_x = st.selectbox("X axis (categorical)", cat_cols, key="bq_x")
                with col_sel2:
                    chosen_y = st.selectbox("Y axis (numeric)", num_cols, key="bq_y")

                chart_type = st.radio("Chart type", ["Bar", "Horizontal Bar", "Scatter", "Line"],
                                       horizontal=True)

                plot_df = df.head(15)
                if chart_type == "Bar":
                    fig = px.bar(plot_df, x=chosen_x, y=chosen_y, color=chosen_y,
                                  color_continuous_scale="Purples", title=query_name,
                                  text=chosen_y)
                    fig.update_traces(textposition="outside")
                elif chart_type == "Horizontal Bar":
                    fig = px.bar(plot_df, x=chosen_y, y=chosen_x, orientation="h",
                                  color=chosen_y, color_continuous_scale="Purples",
                                  title=query_name)
                    fig.update_layout(yaxis={"categoryorder": "total ascending"})
                elif chart_type == "Scatter":
                    fig = px.scatter(plot_df, x=chosen_x, y=chosen_y, color=chosen_y,
                                      size=chosen_y, color_continuous_scale="Purples",
                                      title=query_name)
                else:
                    fig = px.line(plot_df, x=chosen_x, y=chosen_y, markers=True,
                                   color_discrete_sequence=["#9b59b6"], title=query_name)

                apply_theme(fig)
                fig.update_layout(xaxis_tickangle=-45)
                st.plotly_chart(fig, use_container_width=True)

    except Exception as e:
        st.error(f"Query error: {e}")


# ──────────────────────────────────────────────
# ROUTER
# ──────────────────────────────────────────────
PAGE_MAP = {
    "🏠  Home": page_home,
    "📊  Aggregated Analysis": page_aggregated,
    "🗺️  Geo Visualization": page_geo,
    "🏆  Top Charts": page_top,
    "📈  Trend Analysis": page_trends,
    "🛡️  Insurance Insights": page_insurance,
    "💡  Business Queries": page_business_queries,
}

PAGE_MAP[page]()

# Footer
st.sidebar.markdown(
    "<div style='font-size:0.68rem;color:#4a4a6a;text-align:center;"
    "margin-top:1.5rem;'>India Pulse · Built with Streamlit</div>",
    unsafe_allow_html=True,
)