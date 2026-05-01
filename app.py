import streamlit as st
import pandas as pd

st.set_page_config(page_title="FRA LogiPrice AI", layout="wide")

st.title("🚛 FRA LogiPrice AI")
st.subheader("Frankfurt AI Logistics Pricing Demo")

st.sidebar.header("实时环境")

fuel_price = st.sidebar.slider("柴油价格 €/L", 1.5, 2.5, 1.85)
cargo = st.sidebar.slider("货机数量", 50, 200, 120)
traffic = st.sidebar.slider("拥堵指数", 0, 100, 30)

def cargo_agent(x):
    if x < 80:
        return 0.8
    elif x < 140:
        return 1.0
    else:
        return 1.3

def traffic_agent(x):
    return 1 + x / 200

def price(dist):
    base = 1.25
    toll = 0.35
    fuel = (fuel_price - 1.7) * 0.4
    return dist * (base + toll + fuel) * cargo_agent(cargo) * traffic_agent(traffic)

destination = st.selectbox("目的地", ["Munich", "Hamburg", "Berlin", "Paris"])

dist_map = {
    "Munich": 390,
    "Hamburg": 490,
    "Berlin": 550,
    "Paris": 570
}

d = dist_map[destination]

st.metric("AI报价", f"€ {round(price(d),2)}")
st.line_chart(pd.DataFrame({
    "price": [price(d)*1.1, price(d), price(d)*0.9]
}))
