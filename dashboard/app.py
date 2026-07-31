"""Streamlit main dashboard web application."""
import sys
from pathlib import Path

# Add root project path to sys.path
root_dir = Path(__file__).parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

import streamlit as st
from config.settings import settings
from database.repository import JobRepository
from dashboard.views import (
    render_analytics_charts,
    render_cv_upload_section,
    render_header,
    render_job_tables,
    render_kpi_cards,
)

st.set_page_config(
    page_title="Autonomous AI Job Search & Application Agent",
    page_icon="🤖",
    layout="wide"
)

repo = JobRepository()

render_header()
render_kpi_cards(repo)

st.markdown("---")
render_cv_upload_section(repo)

st.markdown("---")
render_analytics_charts(repo)

st.markdown("---")
render_job_tables(repo)

with st.sidebar:
    st.header("⚙️ Agent Settings")
    st.write(f"**LLM Provider**: `{settings.llm_provider.upper()}`")
    st.write(f"**Match Threshold**: `{settings.match_threshold}%`")
    st.write(f"**Daily Limit**: `{settings.daily_application_limit}`")
    st.write(f"**Browser Headless**: `{settings.browser_headless}`")
    st.write(f"**Master Resume**: `{settings.resume_path}`")
