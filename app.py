import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="Maximize UR Life", layout="wide")
st.title("💡 Maximize UR Life")

# --- User Inputs ---
age = st.number_input("Your current age", min_value=0, max_value=120, value=30)
lifespan = st.number_input("Expected lifespan", min_value=age+1, max_value=130, value=85)
net_worth = st.number_input("Current net worth ($)", min_value=0, step=1000)
income = st.number_input("Annual income ($)", min_value=0, step=1000)
expenses = st.number_input("Annual expenses ($)", min_value=0, step=1000)
growth = st.slider("Expected investment growth rate (%)", 0.0, 15.0, 5.0) / 100
inflation = st.slider("Expected inflation rate (%)", 0.0, 10.0, 2.0) / 100

years = lifespan - age

# --- Core Logic ---
def calculate_sustainable_spending(net_worth, income, expenses, years, growth, inflation):
    real_growth = (1 + growth) / (1 + inflation) - 1
    pv_factor = sum([1 / ((1 + real_growth) ** t) for t in range(1, years + 1)])
    sustainable_spend = (net_worth + (income - expenses) * years) / pv_factor

    year_data = []
    for year in range(years):
        year_net = net_worth * (1 + growth) + income - expenses - sustainable_spend
        year_data.append({
            'Year': age + year,
            'Income': income,
            'Expenses': expenses,
            'Suggested Spending': sustainable_spend,
            'End Net Worth': year_net
        })
        net_worth = year_net
    return sustainable_spend, pd.DataFrame(year_data)

def calculate_targeted_spending_fixed(net_worth, income, expenses, years, growth, inflation, target_pct=0.1):
    target_end = net_worth * target_pct

    def simulate(spend):
        nw = net_worth
        for _ in range(years):
            nw = nw * (1 + growth) + income - expenses - spend
        return nw

    # Use binary search to find spend that ends close to target_end
    low = 0
    high = (net_worth + income * years)  # overshoot range
    for _ in range(100):
        mid = (low + high) / 2
        final_nw = simulate(mid)
        if final_nw > target_end:
            low = mid  # spend more
        else:
            high = mid  # spend less

    # Now simulate again to get year-by-year
    spend_final = (low + high) / 2
    nw = net_worth
    net_worth_track = []
    for _ in range(years):
        nw = nw * (1 + growth) + income - expenses - spend_final
        net_worth_track.append(nw)

    return spend_final, net_worth_track

# --- Run Calculation ---
if st.button("Calculate"):

    # Normal sustainable spending plan
    sustainable_spend, df = calculate_sustainable_spending(net_worth, income, expenses, years, growth, inflation)
    final_net = df['End Net Worth'].iloc[-1]

    # Optimized spending to near zero
    spend_to_zero, zero_track = calculate_targeted_spending(net_worth, income, expenses, years, growth, inflation, 0.1)

    # --- Output Summary ---
    st.success(f"✅ Sustainable Spending: ${sustainable_spend:,.2f} / year")
    st.info(f"🏁 Final Net Worth at age {lifespan}: ${final_net:,.2f}")
    st.warning(f"💸 Want to spend it all? You could spend ${spend_to_zero:,.2f} / year and end with <10% net worth.")

    # --- Chart 1: Income vs Expenses vs Spending ---
    st.subheader("📊 Yearly Financial Flow")
    chart_data = df[['Year', 'Income', 'Expenses', 'Suggested Spending']].set_index('Year')
    st.bar_chart(chart_data)

    # --- Chart 2: Net Worth Over Time (Sustainable Spending) ---
    st.subheader("📈 Net Worth Projection (Sustainable Spending)")
    st.line_chart(df.set_index('Year')['End Net Worth'])

    # --- Chart 3: Optimized Depletion Curve ---
    st.subheader("💀 Spend It All (Ending with <10% of Net Worth)")
    zero_df = pd.DataFrame({
        'Year': [age + i for i in range(years)],
        'Net Worth': zero_track
    }).set_index('Year')
    st.line_chart(zero_df)
