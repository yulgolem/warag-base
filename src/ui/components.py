import streamlit as st


def log_expander():
    with st.expander("Logs"):
        st.text_area("Logs", "", height=200)


def json_expander():
    with st.expander("Debug JSON"):
        st.text_area("JSON", "", height=200)
