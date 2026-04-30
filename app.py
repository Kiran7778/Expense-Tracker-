import streamlit as st
import requests
from datetime import date

API = "http://127.0.0.1:8000"

st.set_page_config(page_title="Daily Expense Tracker", layout="centered")

st.title("💰 Daily Expense Tracker")


# ───────────────────────── ADD EXPENSE ─────────────────────────
st.header("➕ Add Today's Expense")

today = str(date.today())

title = st.text_input("Title")
amount = st.number_input("Amount", min_value=0.0)
category = st.selectbox("Category", ["Food", "Travel", "Shopping", "Other"])
expense_date = st.text_input("Date", today)
description = st.text_area("Description")

if st.button("Save Expense"):
    try:
        res = requests.post(
            f"{API}/expenses",
            json={
                "title": title,
                "amount": amount,
                "category": category,
                "date": expense_date,
                "description": description
            },
            timeout=10
        )
        st.success("Expense saved successfully!")

    except Exception as e:
        st.error(f"API Error: {e}")


# ───────────────────────── VIEW RECORDS ─────────────────────────
st.header("📋 Expense Records")

try:
    res = requests.get(f"{API}/expenses", timeout=10)
    expenses = res.json().get("expenses", [])

    if not expenses:
        st.warning("No expenses found")
    else:
        for e in expenses:
            st.write(
                f"📅 {e['date']} | "
                f"💰 ₹{e['amount']} | "
                f"🏷️ {e['category']} | "
                f"📝 {e['title']}"
            )

except Exception as e:
    st.error(f"API Error: {e}")