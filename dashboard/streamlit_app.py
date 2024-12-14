import streamlit as st

st.title("E-commerce BI Dashboard")

st.sidebar.title("Navigation")
page = st.sidebar.selectbox("Select Page", ["Home", "Reports", "KPIs"])

if page == "Home":
    st.header("Welcome to the E-commerce BI Dashboard")
    st.write("Overview of key metrics and insights.")

elif page == "Reports":
    st.header("Reports")
    st.write("Detailed reports will be displayed here.")

elif page == "KPIs":
    st.header("Key Performance Indicators (KPIs)")
    st.write("KPI metrics will be displayed here.")
