"""Streamlit visual component views, analytics charts, CV upload, and export helpers."""
from pathlib import Path
import pandas as pd
import streamlit as st
from config.settings import settings
from database.repository import JobRepository
from resume.analyzer import ResumeAnalyzer
from utils.logger import logger


def render_header():
    """Renders sleek top header for Streamlit dashboard."""
    st.markdown(
        """
        <div style="background-color:#1E1E2E;padding:20px;border-radius:12px;margin-bottom:25px;box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);">
            <h1 style="color:#C6A0F6;margin:0;font-family:sans-serif;">🤖 Autonomous AI Job Search & Application Agent</h1>
            <p style="color:#A6ADC8;margin:8px 0 0 0;font-size:15px;">Resume-driven dynamic career inference & multi-platform application tracking</p>
        </div>
        """,
        unsafe_allow_html=True
    )


def render_cv_upload_section(repo: JobRepository):
    """Renders dynamic CV / Resume upload and direct text input section."""
    st.subheader("📄 Dynamic CV / Master Resume Management")

    col_up1, col_up2 = st.columns(2)

    with col_up1:
        st.write("**Option A: Upload Master Resume File (PDF / DOCX)**")
        uploaded_file = st.file_uploader("Upload your updated Resume / CV", type=["pdf", "docx", "txt"])

        if uploaded_file is not None:
            resumes_dir = Path("resumes")
            resumes_dir.mkdir(exist_ok=True)
            saved_path = resumes_dir / uploaded_file.name

            with open(saved_path, "wb") as f:
                f.write(uploaded_file.getbuffer())

            st.success(f"Resume saved to `{saved_path}`!")

            if st.button("🚀 Analyze New Resume & Re-Infer Career Profile"):
                with st.spinner("Analyzing resume and generating search queries..."):
                    analyzer = ResumeAnalyzer(repo=repo)
                    profile = analyzer.analyze(str(saved_path), force_refresh=True)

                    st.session_state["current_profile"] = profile
                    st.success(f"Successfully analyzed profile for **{profile.full_name or 'Candidate'}**!")
                    st.write(f"**Inferred Careers**: {', '.join(profile.inferred_careers)}")
                    st.write(f"**Generated Search Queries**: {profile.inferred_search_queries}")

    with col_up2:
        st.write("**Option B: Paste Raw Resume / CV Text**")
        pasted_text = st.text_area("Paste Resume Text here:", height=150)

        if st.button("📝 Process Pasted Resume Text"):
            if pasted_text.strip():
                resumes_dir = Path("resumes")
                resumes_dir.mkdir(exist_ok=True)
                saved_path = resumes_dir / "pasted_resume.txt"

                with open(saved_path, "w", encoding="utf-8") as f:
                    f.write(pasted_text)

                with st.spinner("Analyzing pasted resume text..."):
                    analyzer = ResumeAnalyzer(repo=repo)
                    profile = analyzer.analyze(str(saved_path), force_refresh=True)
                    st.session_state["current_profile"] = profile
                    st.success(f"Profile updated for **{profile.full_name or 'Candidate'}**!")
                    st.write(f"**Inferred Careers**: {', '.join(profile.inferred_careers)}")
                    st.write(f"**Generated Search Queries**: {profile.inferred_search_queries}")
            else:
                st.warning("Please paste resume text before submitting.")


def render_kpi_cards(repo: JobRepository):
    """Renders top metric KPI summary cards."""
    analytics = repo.get_analytics_summary()

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Jobs Found", analytics.get("total_jobs_found", 0))
    with col2:
        st.metric("High Match (APPLY)", analytics.get("high_match_jobs", 0))
    with col3:
        st.metric("Applications Submitted", analytics.get("total_applied", 0))
    with col4:
        st.metric("HITL Safety Paused", analytics.get("pending_hitl", 0))


def render_analytics_charts(repo: JobRepository):
    """Renders visual analytical charts for match score distribution and job sources."""
    st.subheader("📊 Operational Analytics & Intelligence")
    col_chart1, col_chart2 = st.columns(2)

    with repo.db_manager.get_connection() as conn:
        df_scores = pd.read_sql_query(
            "SELECT overall_match_score, decision FROM job_evaluations",
            conn
        )
        df_platforms = pd.read_sql_query(
            "SELECT source_platform, COUNT(*) as job_count FROM jobs GROUP BY source_platform",
            conn
        )

    with col_chart1:
        st.write("**Match Score Distribution**")
        if not df_scores.empty:
            st.bar_chart(df_scores["overall_match_score"].value_counts(bins=10).sort_index())
        else:
            st.info("No score data available yet.")

    with col_chart2:
        st.write("**Discovered Jobs by Platform**")
        if not df_platforms.empty:
            st.bar_chart(df_platforms.set_index("source_platform"))
        else:
            st.info("No platform data available yet.")


def render_job_tables(repo: JobRepository):
    """Displays searchable job listings, evaluations, and reasoning."""
    st.subheader("📋 Application Pipeline & Discovered Opportunities")

    with repo.db_manager.get_connection() as conn:
        df = pd.read_sql_query(
            """
            SELECT j.id, j.title, j.company, j.location, j.source_platform,
                   e.overall_match_score, e.decision, a.status as app_status,
                   e.reasoning, j.source_url
            FROM jobs j
            LEFT JOIN job_evaluations e ON j.id = e.job_id
            LEFT JOIN applications a ON j.id = a.job_id
            ORDER BY j.created_at DESC
            """,
            conn
        )

    if not df.empty:
        st.dataframe(
            df[["id", "title", "company", "location", "source_platform", "overall_match_score", "decision", "app_status", "source_url"]],
            use_container_width=True,
            column_config={
                "source_url": st.column_config.LinkColumn("Listing Link"),
                "overall_match_score": st.column_config.ProgressColumn(
                    "Match Score",
                    format="%.1f",
                    min_value=0,
                    max_value=100
                )
            }
        )

        st.markdown("### 🔍 Evaluation Reasoning Explorer")
        selected_job_id = st.selectbox("Select Job ID to view LLM evaluation reasoning:", df["id"].tolist())
        if selected_job_id:
            row = df[df["id"] == selected_job_id].iloc[0]
            st.markdown(f"**Job Title**: {row['title']} at **{row['company']}**")
            st.markdown(f"**Match Decision**: `{row['decision']}` | **Overall Score**: `{row['overall_match_score']}`")
            st.info(f"**LLM Reasoning**: {row['reasoning'] or 'Not evaluated yet.'}")

        st.subheader("📥 Export Pipeline Data")
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("Download Full CSV Report", csv, "job_pipeline_report.csv", "text/csv")
    else:
        st.info("No job listings present in database yet. Run pipeline (`python main.py --mode run`) to discover opportunities.")
