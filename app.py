import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(page_title="Maximize UR Life", layout="centered")
st.title("💡 Maximize UR Life")

# User inputs
age = st.number_input("Your current age", min_value=0, max_value=120, value=30)
lifespan = st.number_input("Expected lifespan", min_value=0, max_value=120, value=85)
net_worth = st.number_input("Current net worth ($)", min_value=0, step=1000)
income = st.number_input("Annual income ($)", min_value=0, step=1000)
expenses = st.number_input("Annual expenses ($)", min_value=0, step=1000)
growth = st.slider("Expected investment growth rate (%)", 0.0, 15.0, 5.0) / 100
inflation = st.slider("Expected inflation rate (%)", 0.0, 10.0, 2.0) / 100

years = lifespan - age

def calculate_spending(net_worth, income, expenses, years, growth, inflation):
    real_growth = (1 + growth) / (1 + inflation) - 1
    pv_factor = sum([1 / ((1 + real_growth) ** t) for t in range(1, years + 1)])
    sustainable_spend = (net_worth + (income - expenses) * years) / pv_factor

    net_worth_track = [net_worth]
    for year in range(1, years + 1):
        net_worth = net_worth * (1 + growth) + income - expenses - sustainable_spend
        net_worth_track.append(net_worth)
    return sustainable_spend, net_worth_track

if st.button("Calculate"):
    spend, track = calculate_spending(net_worth, income, expenses, years, growth, inflation)
    st.success(f"✅ You can safely spend: ${spend:,.2f} per year")
    st.info(f"💼 Final net worth at age {lifespan}: ${track[-1]:,.2f}")

    st.subheader("📈 Net Worth Projection")
    st.line_chart(track)
