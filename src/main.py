from __future__ import annotations

import time
from pathlib import Path
from typing import List, Optional

import streamlit as st

from src.ui.components import (
    file_uploader_component,
    settings_sidebar_component,
    progress_component,
    human_logs_component,
    json_logs_component,
    stats_component,
)


def main() -> None:
    st.set_page_config(page_title="Worldbuilding Assistant", page_icon="🌍", layout="wide")

    _initialize_session_state()

    _render_sidebar()
    _render_main_content()
    _render_logging_section()


def _initialize_session_state() -> None:
    if "uploaded_files" not in st.session_state:
        st.session_state.uploaded_files: List = []
    if "processing_status" not in st.session_state:
        st.session_state.processing_status = "idle"
    if "settings" not in st.session_state:
        st.session_state.settings = {
            "chunk_size": 500,
            "chunk_overlap": 100,
            "entity_types": ["person", "location", "organization", "concept", "object"],
            "confidence_threshold": 0.7,
        }
    if "logs_buffer" not in st.session_state:
        st.session_state.logs_buffer: List[str] = []
    if "processing_results" not in st.session_state:
        st.session_state.processing_results = None


def _render_sidebar() -> None:
    st.session_state.settings = settings_sidebar_component()
    if st.sidebar.button("Reset All"):
        st.session_state.uploaded_files = []
        st.session_state.processing_status = "idle"
        st.session_state.logs_buffer = []
        st.session_state.processing_results = None


def _render_main_content() -> None:
    st.title("🌍 Worldbuilding Assistant")
    uploaded = file_uploader_component()
    if uploaded is not None:
        st.session_state.uploaded_files = uploaded

    if st.button("Process Files"):
        _process_files()

    if st.session_state.processing_status == "processing":
        progress_component(1, 3, "Processing...")
    elif st.session_state.processing_status == "completed":
        stats_component({"Files": len(st.session_state.uploaded_files)})


def _render_logging_section() -> None:
    logs = _load_logs_from_file()
    human_logs_component(logs)
    json_logs_component([{"log": log} for log in logs])


def _process_files() -> None:
    """Placeholder for file processing."""
    st.session_state.processing_status = "processing"
    st.info("🚧 File processing will be implemented in next tasks")
    with st.spinner("Processing files..."):
        time.sleep(2)
    st.success("✅ Mock processing completed!")
    st.session_state.processing_status = "completed"


def _load_logs_from_file() -> List[str]:
    """Placeholder for log loading."""
    return [
        "14:30:15 | agents | INFO | Mock: Starting entity extraction",
        "14:30:16 | agents | INFO | Mock: Found 5 entities in chunk_0",
        "14:30:17 | database | INFO | Mock: Stored entities in Neo4j",
    ]


if __name__ == "__main__":
    main()
