import streamlit as st
from src.utils.logging_utils import get_logger

logger = get_logger(__name__)

st.set_page_config(page_title="Worldbuilding Assistant")

st.sidebar.title("Settings")

st.write("Upload markdown files to begin processing.")
