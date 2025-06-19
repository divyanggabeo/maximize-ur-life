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

def highlight_net_worth(val):
    color = 'green' if val > 0 else 'red'
    return f'color: {color}'

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

    # Binary search to find optimal annual spend
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

    # Build detailed yearly breakdown
    nw = net_worth
    rows = []
    for i in range(years):
        nw = nw * (1 + growth) + income - expenses - final_spend
        rows.append({
            'Year': i,
            'Age': i + (lifespan - years),
            'Income': income,
            'Expenses': expenses,
            'Optimized Spending': final_spend,
            'End Net Worth (Optimized)': nw
        })
    df = pd.DataFrame(rows)
    return final_spend, df


# --- Run Calculation ---
if st.button("Calculate"):

    # Normal sustainable spending plan
    sustainable_spend, df = calculate_sustainable_spending(net_worth, income, expenses, years, growth, inflation)
    final_net = df['End Net Worth'].iloc[-1]

    # Optimized spending to near zero
    spend_to_zero, df_zero = calculate_targeted_spending_fixed(net_worth, income, expenses, years, growth, inflation, 0.1)



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

    # Merge both plans into one table
    combined_df = df.copy()
    combined_df = combined_df.rename(columns={
        'Suggested Spending': 'Sustainable Spending',
        'End Net Worth': 'End Net Worth (Sustainable)'
    })
    combined_df = combined_df.merge(
        df_zero[['Age', 'Optimized Spending', 'End Net Worth (Optimized)']],
        on='Age'
    )

    st.subheader("📋 Year-by-Year Financial Amortization")
    styled = combined_df.style.format("${:,.0f}", subset=['Income', 'Expenses', 'Sustainable Spending', 'Optimized Spending', 'End Net Worth (Sustainable)', 'End Net Worth (Optimized)'])
    styled = styled.applymap(highlight_net_worth, subset=['End Net Worth (Sustainable)', 'End Net Worth (Optimized)'])

    st.dataframe(styled, use_container_width=True)
