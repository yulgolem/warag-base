from __future__ import annotations

import json
from typing import List, Optional, Dict, Any

import streamlit as st


def file_uploader_component() -> Optional[List]:
    """Multiple file uploader for Markdown files."""
    uploaded_files = st.file_uploader(
        "Upload Markdown Files",
        type=["md"],
        accept_multiple_files=True,
    )
    return uploaded_files


def settings_sidebar_component() -> Dict[str, Any]:
    """Render settings controls in the sidebar and return config."""
    st.sidebar.header("⚙️ Settings")
    chunk_size = st.sidebar.number_input("Chunk Size", min_value=100, max_value=2000, value=500, step=50)
    chunk_overlap = st.sidebar.number_input("Chunk Overlap", min_value=0, max_value=500, value=100, step=10)
    confidence = st.sidebar.slider("Confidence Threshold", 0.0, 1.0, 0.7, 0.05)

    entity_types = [
        "person",
        "location",
        "organization",
        "concept",
        "object",
    ]
    selected_types = [
        et
        for et in entity_types
        if st.sidebar.checkbox(et.capitalize(), True, key=f"ent_{et}")
    ]

    return {
        "chunk_size": chunk_size,
        "chunk_overlap": chunk_overlap,
        "entity_types": selected_types,
        "confidence_threshold": confidence,
    }


def progress_component(current: int, total: int, message: str = "") -> None:
    """Display a progress bar with optional message."""
    if total <= 0:
        progress = 0.0
    else:
        progress = current / total
    st.progress(progress, text=message)


def human_logs_component(logs: List[str]) -> None:
    """Display human-readable logs inside an expander."""
    with st.expander("Processing Logs", expanded=False):
        st.text_area(
            "Logs",
            value="\n".join(logs),
            height=200,
        )


def json_logs_component(json_logs: List[Dict[str, Any]]) -> None:
    """Display JSON logs inside an expander."""
    with st.expander("Debug Output (JSON)", expanded=False):
        formatted = json.dumps(json_logs, ensure_ascii=False, indent=2)
        st.code(formatted, language="json")


def stats_component(stats: Dict[str, Any]) -> None:
    """Show processing statistics using Streamlit metrics."""
    cols = st.columns(len(stats))
    for col, (name, value) in zip(cols, stats.items()):
        col.metric(label=name, value=value)

