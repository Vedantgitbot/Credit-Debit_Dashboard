import streamlit as st
import pandas as pd
import plotly.express as px
from UI import (
    header_section, display_transactions, transaction_form, 
    visualize_data, delete_transaction_form, footer_section
)


FILE_PATH = ""

st.set_page_config(page_title="My MoneyManage Dashboard", layout="wide")


@st.cache_data
def load_data(file_path):
    try:
        df = pd.read_excel(file_path)
        df.columns = df.columns.str.strip()
        required_cols = ['Transaction_ID', 'Transaction_Date', 'Credit', 'Credit_Description', 'Debit', 'Debit_Description', 'Total_Balance']
        
        if set(required_cols).issubset(df.columns):
            df['Transaction_Date'] = pd.to_datetime(df['Transaction_Date'])
            return df
        else:
            st.error("Invalid file format. Ensure required columns are present.")
            return pd.DataFrame()
    except FileNotFoundError:
        st.error("File not found. Ensure the file path is correct.")
        return pd.DataFrame()

df = load_data(FILE_PATH)

if 'transactions' not in st.session_state:
    st.session_state['transactions'] = df

header_section()

df = st.session_state['transactions']

st.markdown("### 📌 Add Transaction & View Data")
col1, col2 = st.columns([1, 2]) 

with col1:
    st.subheader("➕ Add New Transaction")
    last_transaction_id = int(df['Transaction_ID'].max()) if not df.empty else 0
    last_balance = df['Total_Balance'].iloc[-1] if not df.empty else 0
    
    new_transaction = transaction_form(last_transaction_id, last_balance)
    if new_transaction:
        new_entry = pd.DataFrame([new_transaction])
        df = pd.concat([df, new_entry], ignore_index=True)
        df.to_excel(FILE_PATH, index=False)
        st.session_state['transactions'] = df
        st.success(f"Entry with Transaction ID {new_transaction['Transaction_ID']} added successfully!")

with col2:
    st.subheader("📋 Transaction Records")
    if not df.empty:
        display_transactions(df)
    else:
        st.info("No transactions recorded yet.")

st.markdown("---")
st.markdown("##  Analytics & Insights 📊")

if not df.empty:
    total_credit = df['Credit'].sum()
    total_debit = df['Debit'].sum()

    col3, col4 = st.columns(2)
    
    with col3:
        st.subheader(" Credit Overview")
        st.metric(label="Total Credit", value=f"${total_credit:,.2f}")
        st.write(df[['Transaction_Date', 'Credit', 'Credit_Description']].tail(10))  

    with col4:
        st.subheader("Debit Overview")
        st.metric(label="Total Debit", value=f"${total_debit:,.2f}")
        st.write(df[['Transaction_Date', 'Debit', 'Debit_Description']].tail(10))  

    df['Debit_Description'] = df['Debit_Description'].str.strip().str.lower()
    debit_spending = df.groupby('Debit_Description')['Debit'].sum().reset_index()
    debit_spending = debit_spending.drop_duplicates()

    st.subheader(" Debit Spending Breakdown ")
    fig_debit_pie = px.pie(debit_spending, names='Debit_Description', values='Debit', title="Where is Your Money Going?", hole=0.4)
    st.plotly_chart(fig_debit_pie, use_container_width=True)

    fig_trend = px.line(df, x='Transaction_Date', y=['Credit', 'Debit'], title="Credit & Debit Over Time", labels={'value': 'Amount', 'Transaction_Date': 'Date'})
    st.plotly_chart(fig_trend, use_container_width=True)

    st.subheader("Delete Transaction 🗑️ ")
    delete_id = delete_transaction_form()
    if delete_id:
        if delete_id in df['Transaction_ID'].values:
            df = df[df['Transaction_ID'] != delete_id]
            df['Total_Balance'] = df['Credit'].cumsum() - df['Debit'].cumsum()
            df.to_excel(FILE_PATH, index=False)
            st.session_state['transactions'] = df
            st.success(f"Entry with Transaction ID {delete_id} deleted successfully!")
        else:
            st.error(f"No entry found with Transaction ID {delete_id}.")
else:
    st.info("No transactions available for analysis.")

def set_target_goal():
    """Allow users to set a target spending limit and track progress."""
    st.subheader("🎯 Set Target Goal")
    if 'target_goal' not in st.session_state:
        st.session_state['target_goal'] = 0.0
    target = st.number_input("Enter your spending limit ($)", 
                             min_value=0.0, 
                             value=float(st.session_state['target_goal']),  # Ensure float
                             step=100.0)
    if st.button("Set Goal"):
        st.session_state['target_goal'] = target
        st.success(f"Target spending limit set to ${target:,.2f}")

def spending_stop_recommender(df):
    """Check spending against the target goal and display warnings accordingly."""
    if 'target_goal' in st.session_state and st.session_state['target_goal'] > 0:
        total_debit = df['Debit'].sum()
        target = st.session_state['target_goal']
        
        st.subheader("📊 Spending Progress")
        progress = min(total_debit / target, 1.0)  # Cap at 100%
        st.progress(progress)
        
        if total_debit >= target:
            st.error("🚨 You have exceeded your spending limit! Consider reducing expenses.")
        elif total_debit >= 0.9 * target:
            st.warning("⚠️ You are close to exceeding your spending limit!")
        else:
            st.success(f"✅ You have spent ${total_debit:,.2f} out of your target ${target:,.2f}.")

set_target_goal()
spending_stop_recommender(df)

footer_section()
