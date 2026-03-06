import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import datetime

st.set_page_config(layout="wide", page_title="BMD Sales Analytics")

# ── Custom CSS — green theme ──────────────────────────────
st.markdown("""
<style>
    .stApp { background-color: #F0F2F0; }
    .block-container { padding-top: 1rem; }

    /* Header */
    .bmd-header {
        background-color: #1B5E35;
        padding: 14px 20px 10px 20px;
        border-radius: 6px;
        margin-bottom: 6px;
    }
    .bmd-header h1 {
        color: white !important;
        font-size: 1.5rem !important;
        margin: 0 !important;
    }
    .bmd-subtitle {
        background-color: #81C995;
        padding: 5px 20px;
        border-radius: 4px;
        color: #0D1F14;
        font-style: italic;
        font-size: 0.85rem;
        margin-bottom: 10px;
    }

    /* KPI cards */
    .kpi-card {
        background-color: #2E7D4F;
        border-top: 4px solid #1B5E35;
        border-radius: 6px;
        padding: 14px 16px;
        color: white;
        min-height: 110px;
    }
    .kpi-label  { font-size: 0.75rem; color: #B2D8BE; margin-bottom: 4px; }
    .kpi-value  { font-size: 1.7rem; font-weight: 700; color: white; }
    .kpi-delta-pos { color: #81C995; font-size: 0.8rem; font-weight: 600; }
    .kpi-delta-neg { color: #FF8A80; font-size: 0.8rem; font-weight: 600; }

    /* Filter bar */
    .filter-bar {
        background-color: #E8EDE9;
        border: 1px solid #B2CEBF;
        border-radius: 6px;
        padding: 8px 12px;
        margin-bottom: 10px;
    }

    /* RLS banner */
    .rls-banner {
        background-color: #E8F5E9;
        border-left: 4px solid #2E7D4F;
        padding: 6px 14px;
        border-radius: 4px;
        color: #1B5E35;
        font-size: 0.82rem;
        margin-bottom: 10px;
    }
</style>
""", unsafe_allow_html=True)
st.title("Global Sales Analytics Dashboard")

st.markdown("""
**Better Medical Devices (BMD)**  
Interactive analytics dashboard for revenue performance, forecasting, and regional insights.
""")

# ── HEADER ────────────────────────────────────────────────
st.sidebar.header("Dashboard Filters")
st.markdown("""
<div class="bmd-header">
  <h1>Global Sales Analytics &nbsp;·&nbsp; Better Medical Devices (BMD)</h1>
  <div style="color:#B2D8BE;font-size:0.78rem;margin-top:2px;">
      Gold Layer &nbsp;·&nbsp; FactSales &nbsp;·&nbsp; Grain: one row per invoice line item
  </div>
</div>
<div class="bmd-subtitle">
  Same dashboard — RLS automatically limits view based on user identity
</div>
""", unsafe_allow_html=True)

# ── DATA ─────────────────────────────────────────────────
np.random.seed(42)   # fixed seed so numbers don't jump on every refresh

months_idx = pd.date_range("2024-01-01", periods=12, freq="MS")
channels   = ["Direct Sales", "Distributor", "Online", "Hospital Contracts"]

# ── Base actual data (12 months)
actual_revenue = [8_900_000, 9_400_000, 10_200_000, 9_800_000, 10_800_000,
                  11_500_000, 11_200_000, 11_900_000, 12_400_000,
                  11_000_000, 10_500_000, 12_000_000]

data = pd.DataFrame({
    "Date":     months_idx,
    "Month":    months_idx.strftime("%b"),        # "Jan", "Feb" …
    "Revenue":  actual_revenue,
    "Category": ["Cardiac","Ortho","Neuro","Other","Cardiac","Ortho",
                  "Neuro","Other","Cardiac","Ortho","Neuro","Other"],
    "Region":   ["US","EU","US","EU","US","EU","US","EU","US","EU","US","EU"],
    "Units":    [68000,72000,85000,79000,90000,95000,88000,92000,
                 98000,76000,71000,99000],
    "Channel":  np.random.choice(channels, 12),
    "Margin":   [0.41,0.37,0.44,0.35,0.42,0.38,0.43,0.36,
                 0.44,0.38,0.35,0.41],
})

# ── Last-year data (same months, ~10% lower)
last_year_rev = [int(r * 0.90) for r in actual_revenue]


# Convert lists to pandas series aligned with months
actual_series = pd.Series(actual_revenue, index=months_idx)
last_year_series = pd.Series(last_year_rev, index=months_idx)

today = datetime.datetime(2024, 9, 1)
# Actual data only until today
actual_series = actual_series[actual_series.index <= today]
last_year_series = last_year_series[last_year_series.index <= today]

# Forecast months after today
forecast_months = months_idx[months_idx > today]
forecast_rev = [12_500_000, 13_200_000, 14_400_000]

months_idx_actual = actual_series.index
actual_revenue_filtered = actual_series.values
last_year_filtered = last_year_series.values


# ── FILTERS ──────────────────────────────────────────────
st.markdown('<div class="filter-bar">', unsafe_allow_html=True)
col1, col2, col3, col4 = st.columns(4)

with col1:
    date_filter = st.sidebar.selectbox(
        "Date Range",
        ["All","Jan","Feb","Mar","Apr","May","Jun",
         "Jul","Aug","Sep","Oct","Nov","Dec"]
    )
with col2:
    region_filter = st.sidebar.selectbox("Region (US / EU / Global)", ["All","US","EU"])
with col3:
    category_filter = st.sidebar.selectbox(
        "Product Category",
        ["All","Cardiac","Ortho","Neuro","Other"]
    )
with col4:
    channel_filter = st.sidebar.selectbox(
        "Channel",
        ["All","Direct Sales","Distributor","Online","Hospital Contracts"]
    )
st.markdown('</div>', unsafe_allow_html=True)

# ── Apply filters ─────────────────────────────────────────
filtered = data.copy()

if date_filter != "All":
    filtered = filtered[filtered["Month"] == date_filter]
if region_filter != "All":
    filtered = filtered[filtered["Region"] == region_filter]
if category_filter != "All":
    filtered = filtered[filtered["Category"] == category_filter]
if channel_filter != "All":
    filtered = filtered[filtered["Channel"] == channel_filter]

# ── KPIs ─────────────────────────────────────────────────
total_revenue  = filtered["Revenue"].sum()
gross_margin   = filtered["Margin"].mean() * 100 if len(filtered) else 0
units_sold     = filtered["Units"].sum()
revenue_growth = 8.2   # fixed YoY for demo

k1, k2, k3, k4 = st.columns(4)

def kpi_card(col, label, value, delta, positive=True):
    dc = "kpi-delta-pos" if positive else "kpi-delta-neg"
    arrow = "▲" if positive else "▼"
    col.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">{label}</div>
        <div class="kpi-value">{value}</div>
        <div class="{dc}">{arrow} {delta}</div>
    </div>
    """, unsafe_allow_html=True)

kpi_card(k1, "Total Revenue (USD)",      f"${total_revenue/1e6:.1f}M", "8.2% YoY",   True)
kpi_card(k2, "Gross Margin %",           f"{gross_margin:.1f}%",        "1.1 pts",     True)
kpi_card(k3, "Revenue Growth (YOY)",     f"{revenue_growth:.1f}%",      "vs Last Year",True)
kpi_card(k4, "Units Sold (Invoice Units)",f"{units_sold/1000:.0f}K",    "2.1% YoY",   False)

st.markdown("<div style='margin-top:14px'></div>", unsafe_allow_html=True)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ROW 1 — Revenue Trend + YoY Growth
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

st.divider()
st.subheader("Revenue Trends")
left, right = st.columns([2, 1])

# ── Revenue Trend: Actual bars + Forecast line + LY line ─
with left:
    fig_trend = go.Figure()

    # Actual bars — dark green
    fig_trend.add_trace(go.Bar(
        x=months_idx_actual,
        y=actual_revenue_filtered,
        name="Actual",
        marker_color="#2E7D4F",
        opacity=0.9,
        hovertemplate="<b>%{x|%b %Y}</b><br>Actual: $%{y:,.0f}<extra></extra>"
    ))

    # Last Year — dotted grey line
    fig_trend.add_trace(go.Scatter(
        x=months_idx_actual,
        y=last_year_filtered,
        name="Last Year",
        mode="lines",
        line=dict(color="#9E9E9E", width=1.5, dash="dot"),
        hovertemplate="<b>%{x|%b %Y}</b><br>Last Year: $%{y:,.0f}<extra></extra>"
    ))

    # Forecast — dashed light green line (Oct–Dec only)
    fig_trend.add_trace(go.Scatter(
        x=forecast_months,
        y=forecast_rev,
        name="Forecast",
        mode="lines+markers",
        line=dict(color="#81C995", width=2.5, dash="dash"),
        marker=dict(size=7, color="#81C995", symbol="diamond"),
        hovertemplate="<b>%{x|%b %Y}</b><br>Forecast: $%{y:,.0f}<extra></extra>"
    ))

    # "Today" vertical line at Sep
   
    fig_trend.add_shape(
        type="line",
        x0=today,
        x1=today,
        y0=0,
        y1=1,
        xref="x",
        yref="paper",
        line=dict(color="#B2CEBF", width=1.5, dash="dot")
    )

    fig_trend.add_annotation(
        x=today,
        y=1,
        xref="x",
        yref="paper",
        text="Today",
        showarrow=False,
        font=dict(color="#6B8070"),
        xanchor="left",
        yanchor="bottom"
    )

    fig_trend.update_layout(
        title=dict(text="Revenue Trend + Forecast Overlay", font=dict(color="#0D1F14", size=13)),
        plot_bgcolor="#F0F2F0",
        paper_bgcolor="#F0F2F0",
        font=dict(color="#0D1F14"),
        legend=dict(bgcolor="#F0F2F0", bordercolor="#B2CEBF",
                    orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
        xaxis=dict(title="Date", gridcolor="#B2CEBF", tickformat="%b %Y"),
        yaxis=dict(title="Revenue ($)", gridcolor="#B2CEBF",
                   tickformat="$,.0f"),
        barmode="overlay",
        hovermode="x unified",
        height=320,
        margin=dict(t=50, b=40, l=60, r=20)
    )
    st.plotly_chart(fig_trend, use_container_width=True)

# ── YoY Growth  ───────────────

st.divider()
st.subheader("YOY growth")

with right:
    fig_yoy = go.Figure()

    fig_yoy.add_trace(go.Bar(
        x=["Q1 '24", "Q2 '24", "Q3 '24", "Q4 '24F"],
        y=[7.1, 8.4, 9.2, 10.1],
        name="US",
        marker_color="#1B5E35",
        text=["7.1%","8.4%","9.2%","10.1%"],
        textposition="outside",
        textfont=dict(color="#0D1F14", size=11)
    ))

    fig_yoy.add_trace(go.Bar(
        x=["Q1 '24", "Q2 '24", "Q3 '24", "Q4 '24F"],
        y=[5.2, 6.1, 6.8, 7.4],
        name="EU",
        marker_color="#81C995",
        text=["5.2%","6.1%","6.8%","7.4%"],
        textposition="outside",
        textfont=dict(color="#0D1F14", size=11)
    ))

    fig_yoy.update_layout(
        title=dict(text="YoY Growth Rate: US vs EU", font=dict(color="white", size=13)),
        barmode="group",
        bargap=0.25,
        bargroupgap=0.05,
        plot_bgcolor="#F0F2F0",
        paper_bgcolor="#DDE3E8",
        font=dict(color="white"),
        legend=dict(bgcolor="#0D1B2A", bordercolor="#1E3A5F",
                    font=dict(color="white")),
        xaxis=dict(gridcolor="#1E3A5F", tickfont=dict(color="white"), showgrid=False),
        yaxis=dict(gridcolor="#1E3A5F", tickfont=dict(color="white"),
                   ticksuffix="%", showgrid=True, range=[0, 13]),
        height=320,
        margin=dict(t=50, b=40, l=40, r=20)
    )
    st.plotly_chart(fig_yoy, use_container_width=True)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ROW 2 — Category Bar | Region Donut | Scatter
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
c1, c2, c3 = st.columns([1.3, 1, 1.3])

# ── Category horizontal bar ───────────────────────────────
with c1:
    cat = filtered.groupby("Category")["Revenue"].sum().reset_index().sort_values("Revenue", ascending=True)
    fig_cat = go.Figure(go.Bar(
        x=cat["Revenue"], y=cat["Category"],
        orientation="h",
        marker_color=["#1B5E35","#2E7D4F","#4CAF72","#00838F"],
        text=[f"${v/1e6:.1f}M" for v in cat["Revenue"]],
        textposition="outside"
    ))
    fig_cat.update_layout(
        title=dict(text="Revenue by Product Category", font=dict(color="#0D1F14", size=13)),
        plot_bgcolor="#F0F2F0", paper_bgcolor="#F0F2F0",
        font=dict(color="#0D1F14"),
        xaxis=dict(gridcolor="#B2CEBF", tickformat="$,.0f"),
        yaxis=dict(gridcolor="#B2CEBF"),
        height=300, margin=dict(t=45, b=30, l=10, r=60)
    )
    st.plotly_chart(fig_cat, use_container_width=True)

# ── Region donut ──────────────────────────────────────────
with c2:
    region_grp = filtered.groupby("Region")["Revenue"].sum().reset_index()
    fig_donut = go.Figure(go.Pie(
        labels=region_grp["Region"],
        values=region_grp["Revenue"],
        hole=0.55,
        marker_colors=["#1B5E35","#4CAF72"],
        textfont=dict(color="white", size=11),
        hovertemplate="<b>%{label}</b><br>$%{value:,.0f}<br>%{percent}<extra></extra>"
    ))
    fig_donut.update_layout(
        title=dict(text="Revenue by Region", font=dict(color="#0D1F14", size=13)),
        paper_bgcolor="#F0F2F0",
        legend=dict(font=dict(color="#0D1F14")),
        annotations=[dict(text=f"${filtered['Revenue'].sum()/1e6:.0f}M",
                          x=0.5, y=0.5, font_size=16,
                          font_color="#0D1F14", showarrow=False)],
        height=300, margin=dict(t=45, b=30, l=10, r=10)
    )
    st.plotly_chart(fig_donut, use_container_width=True)

# ── Revenue vs Margin scatter ─────────────────────────────
with c3:
    fig_scatter = px.scatter(
        filtered, x="Revenue", y="Margin",
        color="Category",
        size="Units",
        color_discrete_sequence=["#1B5E35","#2E7D4F","#4CAF72","#00838F"],
        title="Revenue vs Margin by Product",
        hover_data=["Category","Region"]
    )
    fig_scatter.add_hline(y=0.38, line_dash="dot", line_color="#B2CEBF", line_width=1)
    fig_scatter.add_vline(x=10_500_000, line_dash="dot", line_color="#B2CEBF", line_width=1)
    fig_scatter.update_layout(
        plot_bgcolor="#F0F2F0", paper_bgcolor="#F0F2F0",
        font=dict(color="#0D1F14"),
        xaxis=dict(gridcolor="#B2CEBF", tickformat="$,.0f"),
        yaxis=dict(gridcolor="#B2CEBF", tickformat=".0%"),
        height=300, margin=dict(t=45, b=30, l=50, r=20)
    )
    st.plotly_chart(fig_scatter, use_container_width=True)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ROW 3 — Discount/Margin | Forecast Accuracy | Top Customers
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
d1, d2, d3 = st.columns([1.2, 1.2, 1])

# ── Discount vs Margin dual-axis ──────────────────────────
with d1:
    disc_months_lbl = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep"]
    discount_vals   = [8.2, 9.1, 7.8, 10.2, 9.4, 8.6, 11.1, 8.9, 8.4]
    margin_vals     = [38.1,37.4,39.2,36.8,37.9,38.5,36.2,38.1,38.4]

    fig_disc = go.Figure()
    fig_disc.add_trace(go.Bar(
        x=disc_months_lbl, y=discount_vals,
        name="Discount %", marker_color="#F5A623", opacity=0.6,
        yaxis="y1"
    ))
    fig_disc.add_trace(go.Scatter(
        x=disc_months_lbl, y=margin_vals,
        name="Margin %", mode="lines+markers",
        line=dict(color="#1B5E35", width=2.2),
        marker=dict(size=5), yaxis="y2"
    ))
    fig_disc.update_layout(
    title=dict(text="Discount Rate vs Gross Margin", font=dict(color="#0D1F14", size=13)),
    plot_bgcolor="#F0F2F0",
    paper_bgcolor="#F0F2F0",
    font=dict(color="#0D1F14"),
    yaxis=dict(
        title=dict(text="Discount %", font=dict(color="#F5A623")),
        gridcolor="#B2CEBF",
        tickfont=dict(color="#F5A623")
    ),
    yaxis2=dict(
        title=dict(text="Margin %", font=dict(color="#1B5E35")),
        overlaying="y",
        side="right",
        range=[34, 42],
        showgrid=False,
        tickfont=dict(color="#1B5E35")
    ),
    legend=dict(bgcolor="#F0F2F0", bordercolor="#B2CEBF"),
    hovermode="x unified",
    height=280,
    margin=dict(t=45, b=40, l=50, r=50)
)
    st.plotly_chart(fig_disc, use_container_width=True)

# ── Forecast Accuracy area + target ──────────────────────
with d2:
    fc_acc = [87.2,88.9,86.1,90.3,89.7,91.2,92.4,91.8,91.2]
    fig_fc = go.Figure()
    fig_fc.add_trace(go.Scatter(
        x=disc_months_lbl, y=fc_acc,
        name="Accuracy %", mode="lines+markers",
        fill="tozeroy", fillcolor="rgba(46,125,79,0.15)",
        line=dict(color="#1B5E35", width=2.2),
        marker=dict(size=5, color="#2E7D4F")
    ))
    fig_fc.add_hline(
        y=90, line_dash="dash", line_color="#D32F2F", line_width=1.8,
        annotation_text="Target 90%",
        annotation_font_color="#D32F2F",
        annotation_position="top right"
    )
    fig_fc.update_layout(
        title=dict(text="Forecast Accuracy Over Time", font=dict(color="#0D1F14", size=13)),
        plot_bgcolor="#F0F2F0", paper_bgcolor="#F0F2F0",
        font=dict(color="#0D1F14"),
        xaxis=dict(gridcolor="#B2CEBF"),
        yaxis=dict(gridcolor="#B2CEBF", ticksuffix="%", range=[83,95]),
        height=280, margin=dict(t=45, b=40, l=50, r=20)
    )
    st.plotly_chart(fig_fc, use_container_width=True)

# ── Top Customers table ───────────────────────────────────
with d3:
    st.markdown("##### Top Customers &nbsp;·&nbsp; DimCustomer + CustomerXref")
    customers = pd.DataFrame({
        "Customer":  ["Medtech Corp","EuroHealth AG","ClinPath Ltd",
                      "BioTech Solutions","MedCore Inc","HealthAxis GmbH"],
        "Region":    ["US","EU","US","EU","US","EU"],
        "Revenue":   ["$18.2M","$14.7M","$11.3M","$9.8M","$8.4M","$7.1M"],
        "Margin":    ["41%","37%","39%","43%","31%","36%"],
        "YoY":       ["+12.1%","+7.3%","-2.1%","+15.4%","+4.2%","+8.9%"],
        "Risk":      ["LOW","LOW","HIGH","LOW","MED","LOW"],
    })
    # Colour risk column
    def colour_risk(val):
        c = {"LOW":"color:#2E7D4F;font-weight:700",
             "MED":"color:#E65100;font-weight:700",
             "HIGH":"color:#D32F2F;font-weight:700"}
        return c.get(val,"")

    st.dataframe(
        customers,
        use_container_width=True,
        height=260,
        hide_index=True
    )
    st.caption("🔒 RLS: EU users see EU rows only · US users see US rows only")

# ── Revenue by Channel ────────────────────────────────────
st.markdown("---")
channel_grp = filtered.groupby("Channel")["Revenue"].sum().reset_index()
fig_ch = go.Figure(go.Bar(
    x=channel_grp["Channel"],
    y=channel_grp["Revenue"],
    marker_color=["#1B5E35","#2E7D4F","#4CAF72","#00838F"],
    text=[f"${v/1e6:.1f}M" for v in channel_grp["Revenue"]],
    textposition="outside"
))
fig_ch.update_layout(
    title=dict(text="Revenue by Sales Channel", font=dict(color="#0D1F14", size=13)),
    plot_bgcolor="#F0F2F0", paper_bgcolor="#F0F2F0",
    font=dict(color="#0D1F14"),
    xaxis=dict(gridcolor="#B2CEBF"),
    yaxis=dict(gridcolor="#B2CEBF", tickformat="$,.0f"),
    height=280, margin=dict(t=45, b=40, l=60, r=20)
)
st.plotly_chart(fig_ch, use_container_width=True)

# ── Footer ────────────────────────────────────────────────
st.markdown("""
<div style='background:#1B5E35;padding:8px 16px;border-radius:4px;margin-top:10px;'>
    <span style='color:#B2D8BE;font-size:0.75rem;'>
    🔒 RLS Active &nbsp;·&nbsp; US users see US data only
    &nbsp;·&nbsp; EU users see EU data only &nbsp;·&nbsp; Exec: Global view
    &nbsp;·&nbsp; ERP_US + ERP_EU → Bronze → Silver → Gold
    </span>
</div>

""", unsafe_allow_html=True)
