import streamlit as st
import pandas as pd
import plotly.express as px

def header_section():
    """Displays the header section of the dashboard."""
    st.title("My MoneyManage Dashboard")
    st.markdown("""
    Welcome to the **Credit & Debit Dashboard**. Here you can monitor your transactions, track balance trends, and categorize expenses. 
    Use the form below to add new entries and delete existing ones as needed.
    """)

def display_transactions(df):
    """Displays the transaction data table."""
   
    st.dataframe(df.style.set_properties(**{'text-align': 'center'}), height=300)

def transaction_form(last_transaction_id, last_balance):
    """Displays the transaction entry form and returns user input."""
    next_transaction_id = last_transaction_id + 1
    
    with st.form("add_entry_form"):
        st.write(f"**Auto-generated Transaction ID:** {next_transaction_id}")
        trans_date = st.date_input("Transaction Date")
        credit = st.number_input("Credit Amount", min_value=0.0, format="%.2f")
        credit_desc = st.text_input("Credit Description")  
        debit = st.number_input("Debit Amount", min_value=0.0, format="%.2f")
        debit_desc = st.text_input("Debit Description")  

        new_balance = last_balance + credit - debit
        st.write(f"**Updated Total Balance:** {new_balance:.2f}")

        submit = st.form_submit_button("Add Entry")

    if submit:
        return {
            'Transaction_ID': next_transaction_id,
            'Transaction_Date': trans_date,
            'Credit': credit,
            'Credit_Description': credit_desc,  
            'Debit': debit,
            'Debit_Description': debit_desc,  
            'Total_Balance': new_balance
        }
    
    return None

def visualize_data(df):
    """Displays visual analytics with color-coded indicators."""
    st.markdown("---")
    st.markdown("## Analytics & Insights 📊")

    if df.empty:
        st.info("No transactions available for analysis.")
        return

    total_credit = df['Credit'].sum()
    total_debit = df['Debit'].sum()

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Credit Overview")
        st.metric(label="Total Credit", value=f"${total_credit:,.2f}", delta=f"+${total_credit:,.2f}", delta_color="normal")
        st.write(df[['Transaction_Date', 'Credit', 'Credit_Description']].tail(10))

    with col2:
        st.subheader("Debit Overview")
        st.metric(label="Total Debit", value=f"${total_debit:,.2f}", delta=f"-${total_debit:,.2f}", delta_color="inverse")
        st.write(df[['Transaction_Date', 'Debit', 'Debit_Description']].tail(10))

    st.subheader("Debit Spending Breakdown")
    debit_spending = df.groupby('Debit_Description')['Debit'].sum().reset_index()
    fig_debit_pie = px.pie(debit_spending, names='Debit_Description', values='Debit', 
                            title="Where is Your Money Going?", hole=0.4)
    st.plotly_chart(fig_debit_pie, use_container_width=True)

    fig_trend = px.line(df, x='Transaction_Date', y=['Credit', 'Debit'], 
                        title="Credit & Debit Over Time", labels={'value': 'Amount', 'Transaction_Date': 'Date'})
    st.plotly_chart(fig_trend, use_container_width=True)

def delete_transaction_form():
    """Displays a form to delete a transaction and returns the entered ID."""
    
    delete_id = st.number_input("Enter Transaction ID to Delete", min_value=1, step=1)
    
    if st.button("Delete Entry"):
        return delete_id
    return None

def footer_section():
    """Displays a footer section."""
    st.markdown("---")
    st.markdown("© 2025 Credit & Debit Dashboard. All rights reserved.")


