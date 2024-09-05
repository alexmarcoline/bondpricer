import streamlit as st
import numpy as np
from pathlib import Path

from datetime import datetime, timedelta



# Function to calculate bond price given yield
def calculate_price(maturity, coupon_rate, payment_frequency, par_amount, yield_rate):
    periods = maturity * payment_frequency
    semi_annual_coupon_payment = (coupon_rate / 100) * par_amount / payment_frequency
    periodic_interest_rate = yield_rate / payment_frequency
    
    annuity_factor = (1 - (1 / (1 + periodic_interest_rate) ** periods)) / periodic_interest_rate
    discounted_par_value = par_amount / (1 + periodic_interest_rate) ** periods
    
    price = semi_annual_coupon_payment * annuity_factor + discounted_par_value
    return price

# Function to calculate total return step-by-step with prints
def calculate_total_return(bond_price, coupon_rate, payment_frequency, reinvestment_rate, horizon_years, projected_yield, par_amount, maturity):
    h = horizon_years * payment_frequency
    semi_annual_coupon_payment = (coupon_rate / 100) * par_amount / payment_frequency
    r = reinvestment_rate / payment_frequency

    # Step 1: Total coupon payments + interest-on-interest
    total_coupon_interest = semi_annual_coupon_payment * ((1 + r) ** h - 1) / r
    

    # Step 2: Projected sale price at the end of the investment horizon (remaining years after horizon)
    remaining_years = maturity - horizon_years
    periods_remaining = remaining_years * payment_frequency
    periodic_projected_yield = projected_yield / payment_frequency
    
    # Calculate the projected sale price at the end of 3 years
    projected_sale_price = (
        semi_annual_coupon_payment * (1 - (1 / (1 + periodic_projected_yield) ** periods_remaining)) / periodic_projected_yield +
        par_amount / (1 + periodic_projected_yield) ** periods_remaining
    )
    
   

    # Step 3: Total future dollars
    total_future_dollars = total_coupon_interest + projected_sale_price

    # Step 4: Semiannual total return
    semiannual_total_return = (total_future_dollars / bond_price) ** (1 / h) - 1

    # Step 5: Bond-equivalent total return (annualized)
    bond_equivalent_total_return = 2 * semiannual_total_return

    # Step 6: Effective annual total return
    effective_annual_total_return = (1 + semiannual_total_return) ** 2 - 1

    return bond_equivalent_total_return * 100, effective_annual_total_return * 100

# Function to generate payment schedule
def generate_payment_schedule(maturity, coupon_rate, payment_frequency, par_amount, start_date):
    periods = maturity * payment_frequency
    coupon_payment = (coupon_rate / 100) * par_amount / payment_frequency
    schedule = []
    for i in range(1, periods + 1):
        payment_date = start_date + timedelta(days=(365 / payment_frequency) * i)
        payment_type = "Coupon"
        payment_amount = coupon_payment
        schedule.append((payment_date, payment_type, payment_amount))
    # Final principal payment
    schedule.append((start_date + timedelta(days=365 * maturity), "Principal", par_amount))
    return schedule

st.title("Bond Price and Total Return Calculator")

# Inputs
par_amount = st.number_input("Par Amount", value=1000)
maturity = st.number_input("Maturity (years)", value=20)
coupon_rate = st.number_input("Coupon Rate (%)", value=8.0)
payment_frequency = st.selectbox("Payment Frequency", options=[1, 2, 4, 12], index=1)

calculation_type = st.radio("Calculate", options=["Yield to Price", "Total Return"])

if calculation_type == "Yield to Price":
    required_yield = st.number_input("Required Yield (%)", value=7.0)
    if st.button("Convert to Price"):
        bond_price = calculate_price(maturity, coupon_rate, payment_frequency, par_amount, required_yield / 100)
        st.write(f"Bond Price at Required Yield {required_yield}%: ${bond_price:.2f}")
elif calculation_type == "Total Return":
    bond_price = st.number_input("Bond Price", value=828.40)
    reinvestment_rate = st.number_input("Reinvestment Rate (%)", value=6.0)
    horizon_years = st.number_input("Investment Horizon (years)", value=3)
    projected_yield = st.number_input("Projected Yield at Horizon (%)", value=7.0)
    
    if st.button("Calculate Total Return"):
        bond_equivalent_total_return, effective_annual_total_return = calculate_total_return(
            bond_price, coupon_rate, payment_frequency, reinvestment_rate / 100, horizon_years, projected_yield / 100, par_amount, maturity
        )
        st.write(f"Bond-Equivalent Total Return: {bond_equivalent_total_return:.2f}%")
        st.write(f"Effective Annual Total Return: {effective_annual_total_return:.2f}%")

# Generate and display payment schedule
start_date = datetime.today()
payment_schedule = generate_payment_schedule(maturity, coupon_rate, payment_frequency, par_amount, start_date)
st.write("### Payment Schedule")
st.write(f"{'Date':<15} {'Payment Type':<15} {'Payment Amount':<15}")
for payment in payment_schedule:
    st.write(f"{payment[0].strftime('%Y-%m-%d'):<15} {payment[1]:<15} ${payment[2]:<15.2f}")

if __name__ == "__main__":
    st.write()
