import streamlit as st
import numpy as np
import pandas as pd

st.set_page_config(page_title="Maximize UR Life", layout="wide")
st.title("💡 Maximize UR Life")

# --- User Inputs ---
col1, col2 = st.columns(2)
with col1:
    age = st.number_input("👤 Your current age", min_value=0, max_value=120, value=30)
with col2:
    lifespan = st.number_input("⚰️ Expected lifespan", min_value=age + 1, max_value=130, value=85)

col1, col2 = st.columns(2)
with col1:
    net_worth = st.number_input("💰 Current Net Worth", min_value=0, step=1000, value=1_000_000)
    st.markdown(f"**You entered:** ${net_worth:,.0f}")
with col2:
    income = st.number_input("🏦 Annual Income", min_value=0, step=1000, value=200_000)
    st.markdown(f"**You entered:** ${income:,.0f}")

col1, col2 = st.columns(2)
with col1:
    expenses = st.number_input("🧾 Annual Expenses", min_value=0, step=1000, value=150_000)
    st.markdown(f"**You entered:** ${expenses:,.0f}")
with col2:
    growth = st.slider("📈 Expected investment growth rate (%)", 0.0, 15.0, 5.0) / 100
    inflation = st.slider("📉 Expected inflation rate (%)", 0.0, 10.0, 2.0) / 100

years = lifespan - age

# --- Sustainable Spending Calculation ---
def calculate_sustainable_spending(net_worth, income, expenses, years, growth, inflation):
    real_growth = (1 + growth) / (1 + inflation) - 1
    pv_factor = sum([1 / ((1 + real_growth) ** t) for t in range(1, years + 1)])
    sustainable_spend = (net_worth + (income - expenses) * years) / pv_factor

    year_data = []
    for i in range(years):
        current_age = age + i
        net_worth = net_worth * (1 + growth) + income - expenses - sustainable_spend
        year_data.append({
            'Age': current_age,
            'Income': income,
            'Expenses': expenses,
            'Sustainable Spending': sustainable_spend,
            'End Net Worth (Sustainable)': net_worth
        })
    return sustainable_spend, pd.DataFrame(year_data)

# --- Optimized Spending to Deplete Net Worth ---
def calculate_targeted_spending_fixed(net_worth, income, expenses, years, growth, inflation, target_pct=0.1):
    target_end = net_worth * target_pct

    def simulate(spend):
        nw = net_worth
        for _ in range(years):
            nw = nw * (1 + growth) + income - expenses - spend
        return nw

    low = 0
    high = net_worth + income * years
    for _ in range(100):
        mid = (low + high) / 2
        final_nw = simulate(mid)
        if final_nw > target_end:
            low = mid
        else:
            high = mid

    final_spend = (low + high) / 2

    # Year-by-year tracking
    nw = net_worth
    rows = []
    for i in range(years):
        current_age = age + i
        nw = nw * (1 + growth) + income - expenses - final_spend
        rows.append({
            'Age': current_age,
            'Income': income,
            'Expenses': expenses,
            'Optimized Spending': final_spend,
            'End Net Worth (Optimized)': nw
        })
    return final_spend, pd.DataFrame(rows)

# --- Run Calculation ---
if st.button("Calculate"):

    # 1. Sustainable Spending Plan
    spend_sustainable, df_sustainable = calculate_sustainable_spending(
        net_worth, income, expenses, years, growth, inflation
    )

    # 2. Optimized Spending Plan
    spend_optimized, df_optimized = calculate_targeted_spending_fixed(
        net_worth, income, expenses, years, growth, inflation, 0.1
    )

    # 3. Summary
    col1, col2 = st.columns(2)
    col1.metric("💵 Sustainable Spending / year", f"${spend_sustainable:,.0f}")
    col2.metric("🔥 Optimized Spending / year", f"${spend_optimized:,.0f}")

    st.warning(f"💼 Ending NW (sustainable): ${df_sustainable.iloc[-1]['End Net Worth (Sustainable)']:,.0f}")
    st.warning(f"🏁 Ending NW (optimized): ${df_optimized.iloc[-1]['End Net Worth (Optimized)']:,.0f}")
    st.info(f"🧾 Optimized to die nearly broke (10% left): ${spend_optimized:,.0f}/year")
    st.warning(f"💼 Ending NW (sustainable): ${df_sustainable.iloc[-1]['End Net Worth (Sustainable)']:,.0f}")
    st.warning(f"🏁 Ending NW (optimized): ${df_optimized.iloc[-1]['End Net Worth (Optimized)']:,.0f}")

    # --- Chart: Sustainable Spending
    st.subheader("📈 Net Worth Projection – Sustainable Spending")
    st.line_chart(df_sustainable.set_index('Age')[['End Net Worth (Sustainable)']])

    # --- Chart: Optimized Spend-It-All
    st.subheader("💀 Spend It All Strategy")
    st.line_chart(df_optimized.set_index('Age')[['End Net Worth (Optimized)']])

    # --- Combined Table
    st.subheader("📋 Year-by-Year Financial Table")

    df_combined = pd.merge(
        df_sustainable,
        df_optimized[['Age', 'Optimized Spending', 'End Net Worth (Optimized)']],
        on='Age'
    )

    def highlight(val):
        color = 'green' if val > 0 else 'red'
        return f'color: {color}'

    styled = df_combined.style.format("${:,.0f}", subset=[
        'Income', 'Expenses', 'Sustainable Spending',
        'Optimized Spending', 'End Net Worth (Sustainable)', 'End Net Worth (Optimized)'
    ])
    styled = styled.applymap(highlight, subset=[
        'End Net Worth (Sustainable)', 'End Net Worth (Optimized)'
    ])

    st.dataframe(styled, use_container_width=True)
