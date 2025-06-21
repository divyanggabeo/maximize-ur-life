import streamlit as st
import numpy as np
import pandas as pd

st.set_page_config(page_title="Maximize UR Life", layout="wide")
st.title("💡 Maximize UR Life")

# --- User Inputs ---
st.markdown("### 🔧 Financial Inputs")
row1_col1, row1_col2, row1_col3 = st.columns([1, 1, 1])
with row1_col1:
    age = st.number_input("👤 Current Age", min_value=0, max_value=120, value=48)
    household_size = st.radio("🏠 Household Type", ["Individual", "Couple"])
    retirement_age = st.number_input("🎉 Retirement Age", min_value=age + 1, max_value=130, value=66)

with row1_col2:
    liquid_assets = st.number_input("💵 Liquid Assets", min_value=0, step=1000, value=2_000_000)
    growth_liquid = st.slider("📈 Liquid Growth Rate (%)", 0.0, 15.0, 5.0) / 100
    income = st.number_input("🏦 Annual Income (pre-retirement)", min_value=0, step=1000, value=550_000)

with row1_col3:
    illiquid_assets = st.number_input("🏡 Illiquid Assets", min_value=0, step=1000, value=10_000_000)
    growth_illiquid = st.slider("🏘️ Illiquid Growth Rate (%)", 0.0, 10.0, 2.0) / 100
    tax_rate = st.slider("🧾 Tax Rate (%)", 0.0, 50.0, 33.0) / 100

row2_col1, row2_col2, row2_col3 = st.columns([1, 1, 1])
with row2_col1:
    household_expense = st.number_input("🏠 Annual Household Expense", min_value=0, step=1000, value=150_000)
with row2_col2:
    fun_expense = st.number_input("🎉 Annual Fun Expense", min_value=0, step=1000, value=50_000)
with row2_col3:
    travel_expense = st.number_input("✈️ Annual Travel Expense", min_value=0, step=1000, value=25_000)

with st.container():
    lifespan = st.number_input("⚰️ Expected Lifespan", min_value=age + 1, max_value=130, value=85)
    inflation = st.slider("📉 Inflation Rate (%)", 0.0, 10.0, 2.0) / 100

social_security = 4018 * 12 * (2 if household_size == "Couple" else 1)
years = lifespan - age

# --- Flexible Spending Simulation ---
def simulate_spending(liquid_assets, illiquid_assets, income, years, growth_liquid, growth_illiquid, inflation, tax_rate, multiplier, household_expense, fun_expense, travel_expense):
    l_assets = liquid_assets
    i_assets = illiquid_assets
    year_data = []

    annual_expenses = household_expense + fun_expense + travel_expense
    sustainable_spend = (liquid_assets + illiquid_assets) / years
    spend = sustainable_spend * multiplier

    for i in range(years):
        current_age = age + i
        business_income = income if current_age < retirement_age else 0
        ss_income = social_security if current_age >= 66 else 0
        investment_income = l_assets * growth_liquid
        other_income = ss_income + investment_income
        total_income = business_income + other_income
        tax = total_income * tax_rate
        total_expenses = annual_expenses + tax
        net_income = total_income - total_expenses
        # Update assets accordingly
        l_assets += investment_income + net_income - spend
        i_assets *= (1 + growth_illiquid)
        total_nw = l_assets + i_assets

        year_data.append({
            'Age': current_age,
            'Business Income': int(business_income),
            'Other Income': int(other_income),
            'Total Income': int(total_income),
            'Tax': int(tax),
            'Annual Expenses (Household + Fun + Travel)': int(annual_expenses),
            'Total Expenses (Including Tax)': int(total_expenses),
            'Spending Multiplier Spend': int(spend),
            'Net Income After Expenses': int(net_income),
            'Added to NW': int(net_income - spend + investment_income),
            'Liquid Assets': int(l_assets),
            'Illiquid Assets': int(i_assets),
            'Total Net Worth': int(total_nw)
        })

    return pd.DataFrame(year_data), int(spend)

# --- Find Max Spending Multiplier ---
def find_max_spending_multiplier(liquid_assets, illiquid_assets, income, years, growth_liquid, growth_illiquid, inflation, tax_rate, household_expense, fun_expense, travel_expense):
    low, high = 0, 10
    for _ in range(50):
        mid = (low + high) / 2
        df, _ = simulate_spending(liquid_assets, illiquid_assets, income, years, growth_liquid, growth_illiquid, inflation, tax_rate, mid, household_expense, fun_expense, travel_expense)
        if df.iloc[-1]['Total Net Worth'] > 100_000:
            low = mid
        else:
            high = mid
    return round((low + high) / 2, 2)

# --- Run Calculation ---
if st.button("Calculate"):
    best_multiplier = find_max_spending_multiplier(liquid_assets, illiquid_assets, income, years,
                                                   growth_liquid, growth_illiquid, inflation, tax_rate,
                                                   household_expense, fun_expense, travel_expense)
    
    # Define step size relative to best_multiplier, but with a floor to avoid negative multipliers
    step = max(0.1, best_multiplier * 0.1)  # at least 0.1 or 10% of best_multiplier
    
    # Create multipliers: two below and two above the best multiplier
    multipliers = sorted([
        max(0.01, best_multiplier - 2*step),
        max(0.01, best_multiplier - step),
        best_multiplier + step,
        best_multiplier + 2*step,
    ])

    results = {}
    for m in multipliers:
        df, spend = simulate_spending(liquid_assets, illiquid_assets, income, years,
                                      growth_liquid, growth_illiquid, inflation, tax_rate, m,
                                      household_expense, fun_expense, travel_expense)
        results[m] = (df, spend)

    df_best, best_spend = simulate_spending(liquid_assets, illiquid_assets, income, years,
                                            growth_liquid, growth_illiquid, inflation, tax_rate, best_multiplier,
                                            household_expense, fun_expense, travel_expense)

    st.subheader("📈 Spend vs Net Worth Change (Scenarios)")
    for m, (df, spend) in results.items():
        with st.expander(f"Scenario: {m:.2f}x Spending  |  ${spend:,.0f} / year"):
            st.line_chart(df.set_index('Age')[[
                'Spending Multiplier Spend', 
                'Added to NW', 
                'Total Net Worth',
                'Illiquid Assets'  # Added illiquid assets here
            ]], use_container_width=True)
            st.dataframe(df.style.format("${:,.0f}"), use_container_width=True)

    st.subheader("🏁 Optimal Quality-of-Life Spending")
    st.success(f"Most aggressive sustainable multiplier: {best_multiplier:.2f}x  |  ${best_spend:,.0f} / year")
    st.line_chart(df_best.set_index('Age')[[
        'Spending Multiplier Spend', 
        'Total Net Worth',
        'Illiquid Assets'   # Added illiquid assets here as well
    ]])
    st.dataframe(df_best.style.format("${:,.0f}"), use_container_width=True)
