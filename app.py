import streamlit as st
import pandas as pd
import numpy as np

# =========================
# Page Config
# =========================
st.set_page_config(
    page_title="FRA Smart Pricing Engine",
    page_icon="🚛",
    layout="wide"
)

# =========================
# Header
# =========================
st.markdown("# 🚛 FRA Smart Pricing Engine")
st.caption("AI-powered logistics decision system | Frankfurt Airport 2026")
st.divider()

# =========================
# Sidebar: Market Parameters
# =========================
st.sidebar.header("⚙️ 市场参数模拟")

fuel_price = st.sidebar.slider(
    "德国柴油价格 Diesel Price (€/L)",
    1.50, 2.50, 1.85, 0.01
)

incoming_cargo_planes = st.sidebar.slider(
    "FRA 今日进港货机数量",
    50, 200, 120
)

traffic_index = st.sidebar.slider(
    "A3/A5 高速拥堵指数",
    0, 100, 30
)

last_week_acceptance = st.sidebar.slider(
    "上周司机接单率 (%)",
    0, 100, 70
)

# =========================
# AI Agent Logic
# =========================
def airport_scraper_agent(cargo_planes):
    if cargo_planes < 80:
        return 0.75, "低货运压力"
    elif cargo_planes < 120:
        return 1.00, "正常货运压力"
    elif cargo_planes < 160:
        return 1.20, "高货运压力"
    else:
        return 1.45, "爆仓状态"


def traffic_agent(traffic):
    if traffic < 30:
        return 1.00, "道路顺畅"
    elif traffic < 60:
        return 1.12, "中度拥堵"
    elif traffic < 80:
        return 1.25, "严重拥堵"
    else:
        return 1.40, "事故 / 极端拥堵"


def subsidy_agent(cargo_pressure, traffic):
    if cargo_pressure >= 1.2 and traffic >= 60:
        return 0.20
    elif cargo_pressure >= 1.2:
        return 0.12
    elif traffic >= 60:
        return 0.10
    else:
        return 0.05


def pricing_strategy_agent(acceptance_rate):
    if acceptance_rate < 40:
        return 1.10, "接单率过低，系统加入高溢价"
    elif acceptance_rate < 60:
        return 1.05, "接单率偏低，系统加入中等溢价"
    elif acceptance_rate < 80:
        return 1.02, "接单率正常，系统加入轻微溢价"
    else:
        return 1.00, "接单率良好，无需额外溢价"


def calculate_price(distance, fuel, cargo_pressure, traffic_multiplier, subsidy, driver_premium):
    base_price = 1.25
    toll = 0.35
    fuel_extra = max((fuel - 1.70) * 0.40, 0)

    unit_cost = base_price + toll + fuel_extra - subsidy
    final_price = distance * unit_cost * cargo_pressure * traffic_multiplier * driver_premium

    return round(final_price, 2), round(unit_cost, 2), round(fuel_extra, 2)


# =========================
# Route Selection
# =========================
st.subheader("📍 运输线路设置")

route_col1, route_col2 = st.columns([2, 1])

with route_col1:
    destination = st.selectbox(
        "目的地 Destination",
        ["Munich (MUC)", "Hamburg (HAM)", "Berlin (BER)", "Paris (CDG)", "Amsterdam (AMS)", "Zurich (ZRH)"]
    )

dist_map = {
    "Munich (MUC)": 390,
    "Hamburg (HAM)": 490,
    "Berlin (BER)": 550,
    "Paris (CDG)": 570,
    "Amsterdam (AMS)": 440,
    "Zurich (ZRH)": 410
}

distance = dist_map[destination]

with route_col2:
    st.metric("预估距离", f"{distance} km")

# =========================
# Agent Outputs
# =========================
cargo_pressure, cargo_status = airport_scraper_agent(incoming_cargo_planes)
traffic_multiplier, traffic_status = traffic_agent(traffic_index)
subsidy = subsidy_agent(cargo_pressure, traffic_index)
driver_premium, premium_reason = pricing_strategy_agent(last_week_acceptance)

final_quote, unit_cost, fuel_extra = calculate_price(
    distance,
    fuel_price,
    cargo_pressure,
    traffic_multiplier,
    subsidy,
    driver_premium
)

estimated_driver_cost = distance * 1.05
estimated_profit = final_quote - estimated_driver_cost
profit_margin = estimated_profit / final_quote * 100 if final_quote > 0 else 0

acceptance_probability = max(25, min(95, 100 - (final_quote / 18) + last_week_acceptance * 0.25))
risk_score = min(100, int((traffic_index * 0.45) + (cargo_pressure * 25) + ((100 - last_week_acceptance) * 0.25)))

# =========================
# Executive Dashboard
# =========================
st.divider()
st.subheader("📊 AI 定价决策结果")

kpi1, kpi2, kpi3, kpi4 = st.columns(4)

kpi1.metric(
    "AI 建议报价",
    f"€ {final_quote}",
    f"€ {round(final_quote / distance, 2)} / km"
)

kpi2.metric(
    "预计利润",
    f"€ {round(estimated_profit, 2)}",
    f"{round(profit_margin, 1)}%"
)

kpi3.metric(
    "司机接单概率",
    f"{round(acceptance_probability)}%",
    "AI estimate"
)

kpi4.metric(
    "运输风险指数",
    f"{risk_score}/100",
    "Risk score"
)

# =========================
# AI Decision Explanation
# =========================
st.divider()
st.subheader("🤖 AI 决策解释")

decision_col1, decision_col2 = st.columns(2)

with decision_col1:
    st.markdown("### 当前市场判断")
    st.write(f"""
**FRA 货运状态：** {cargo_status}  
**高速路况：** {traffic_status}  
**柴油价格：** €{fuel_price}/L  
**德国路税 Toll：** €0.35/km  
**系统补贴：** €{subsidy}/km  
**司机策略：** {premium_reason}
""")

with decision_col2:
    if risk_score >= 70:
        st.error("高风险：建议提高报价，或延后发车。")
    elif risk_score >= 45:
        st.warning("中等风险：建议保留动态溢价，并持续观察路况。")
    else:
        st.success("低风险：当前条件适合正常发单。")

    if acceptance_probability < 45:
        st.warning("司机接单概率偏低，建议增加运力溢价。")
    else:
        st.info("司机接单概率处于可接受区间。")

# =========================
# Agent Table
# =========================
st.divider()
st.subheader("🧠 AI Agent 输出")

agent_data = pd.DataFrame({
    "AI Agent": [
        "AirportScraperAgent",
        "TrafficAgent",
        "SubsidyAgent",
        "PricingStrategyAgent"
    ],
    "输入 Input": [
        f"{incoming_cargo_planes} 架进港货机",
        f"Traffic Index = {traffic_index}",
        f"Cargo Pressure = {cargo_pressure}, Traffic = {traffic_index}",
        f"Last Week Acceptance = {last_week_acceptance}%"
    ],
    "输出 Output": [
        f"{cargo_status} / x{cargo_pressure}",
        f"{traffic_status} / x{traffic_multiplier}",
        f"€{subsidy}/km",
        f"x{driver_premium}"
    ]
})

st.dataframe(agent_data, use_container_width=True)

# =========================
# Price vs Acceptance Chart
# =========================
st.divider()
st.subheader("📈 报价与接单概率模拟")

price_range = np.linspace(final_quote * 0.80, final_quote * 1.20, 12)

acceptance_curve = [
    max(20, min(95, 100 - (p / 18) + last_week_acceptance * 0.25))
    for p in price_range
]

chart_df = pd.DataFrame({
    "报价 €": price_range,
    "接单概率 %": acceptance_curve
})

st.line_chart(chart_df.set_index("报价 €"))

# =========================
# 24h Forecast
# =========================
st.divider()
st.subheader("⏱ 24小时运价预测")

forecast_df = pd.DataFrame({
    "时间": ["08:00", "12:00", "16:00", "20:00", "00:00"],
    "预测报价 €": [
        final_quote * 1.08,
        final_quote,
        final_quote * 1.15,
        final_quote * 0.95,
        final_quote * 0.88
    ]
})

st.line_chart(forecast_df.set_index("时间"))

# =========================
# Formula
# =========================
st.divider()
st.subheader("🧮 定价模型")

st.code("""
Final Price =
Distance
× (Base Price + German Toll + Fuel Extra - Subsidy)
× Cargo Pressure Multiplier
× Traffic Multiplier
× Driver Acceptance Premium
""")

st.caption("Demo model only. Real deployment would require live airport data, traffic API, historical transaction data and driver capacity data.")
