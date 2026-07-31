"""Streamlit visual component views, analytics charts, CV upload, and pipeline execution controls."""
import asyncio
from pathlib import Path
import pandas as pd
import streamlit as st
from application.orchestrator import ApplicationOrchestrator
from config.settings import settings
from database.repository import JobRepository
from resume.analyzer import ResumeAnalyzer
from utils.async_utils import run_async
from utils.logger import logger
from utils.salary_estimator import SalaryEstimator


def render_header():
    """Renders sleek top header for Streamlit dashboard."""
    st.markdown(
        """
        <div style="background-color:#1E1E2E;padding:20px;border-radius:12px;margin-bottom:25px;box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);">
            <h1 style="color:#C6A0F6;margin:0;font-family:sans-serif;">🤖 Autonomous AI Job Search & Application Agent</h1>
            <p style="color:#A6ADC8;margin:8px 0 0 0;font-size:15px;">Strict 0-Experience Fresher Job Search & Multi-Platform Application Tracking</p>
        </div>
        """,
        unsafe_allow_html=True
    )


def render_pipeline_controls(repo: JobRepository):
    """Renders one-click execution button for triggering the job search and application pipeline."""
    st.subheader("⚡ Autonomous Agent Pipeline Controls")

    col_btn1, col_btn2 = st.columns([2, 1])

    with col_btn1:
        if st.button("🚀 Run Autonomous Fresher (0 Exp) Job Search & Application Pipeline", use_container_width=True, type="primary"):
            target_resume = st.session_state.get("active_resume_path", settings.resume_path)
            with st.spinner(f"Initiating autonomous fresher job search & evaluation pipeline using `{target_resume}`..."):
                try:
                    orchestrator = ApplicationOrchestrator(resume_path=target_resume)
                    results = run_async(orchestrator.run_full_pipeline())
                    st.success(
                        f"Pipeline Executed Successfully! "
                        f"Discovered **{results['jobs_discovered']}** jobs, "
                        f"Evaluated **{results['jobs_evaluated']}**, "
                        f"Queued **{results['applications_queued']}** 0-experience fresher opportunities."
                    )
                    st.rerun()
                except Exception as e:
                    logger.error(f"Pipeline execution error in UI: {e}")
                    st.error(f"Pipeline execution encountered an error: {e}")

    with col_btn2:
        st.info("Searches LinkedIn, Indeed, Glassdoor, Naukri, Wellfound, RemoteOK, Internshala, Company Portals, Unstop, Freshersworld, and Cutshort.")


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

            st.session_state["active_resume_path"] = str(saved_path)
            st.success(f"Resume saved to `{saved_path}`!")

            col_sub1, col_sub2 = st.columns(2)
            with col_sub1:
                if st.button("🔍 Analyze Resume & Infer Careers"):
                    with st.spinner("Analyzing resume and generating search queries..."):
                        analyzer = ResumeAnalyzer(repo=repo)
                        profile = analyzer.analyze(str(saved_path), force_refresh=True)

                        st.session_state["current_profile"] = profile
                        st.success(f"Successfully analyzed profile for **{profile.full_name or 'Candidate'}**!")
                        st.write(f"**Inferred Careers**: {', '.join(profile.inferred_careers)}")
                        st.write(f"**Generated Search Queries**: {profile.inferred_search_queries}")
            with col_sub2:
                if st.button("🚀 Auto-Search Fresher Jobs"):
                    with st.spinner("Running fresher job search & match evaluation..."):
                        orchestrator = ApplicationOrchestrator(resume_path=str(saved_path))
                        results = run_async(orchestrator.run_full_pipeline())
                        st.success(f"Discovered {results['jobs_discovered']} 0-experience jobs!")
                        st.rerun()

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

                st.session_state["active_resume_path"] = str(saved_path)

                with st.spinner("Analyzing pasted resume text..."):
                    analyzer = ResumeAnalyzer(repo=repo)
                    profile = analyzer.analyze(str(saved_path), force_refresh=True)
                    st.session_state["current_profile"] = profile
                    st.success(f"Profile updated for **{profile.full_name or 'Candidate'}**!")
                    st.write(f"**Inferred Careers**: {', '.join(profile.inferred_careers)}")
                    st.write(f"**Generated Search Queries**: {profile.inferred_search_queries}")

                    # Automatically run discovery
                    orchestrator = ApplicationOrchestrator(resume_path=str(saved_path))
                    results = run_async(orchestrator.run_full_pipeline())
                    st.success(f"Discovered {results['jobs_discovered']} jobs!")
                    st.rerun()
            else:
                st.warning("Please paste resume text before submitting.")


def render_kpi_cards(repo: JobRepository):
    """Renders top metric KPI summary cards."""
    analytics = repo.get_analytics_summary()

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Jobs Found", analytics.get("total_jobs_found", 0))
    with col2:
        st.metric("Fresher Match (APPLY)", analytics.get("high_match_jobs", 0))
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
        st.write("**Discovered Jobs by Platform & Career Portals**")
        if not df_platforms.empty:
            st.bar_chart(df_platforms.set_index("source_platform"))
        else:
            st.info("No platform data available yet.")


def render_job_tables(repo: JobRepository):
    """Displays searchable job listings, evaluations, estimated salaries, and reasoning."""
    st.subheader("📋 Application Pipeline & Discovered Fresher Opportunities")

    with repo.db_manager.get_connection() as conn:
        df = pd.read_sql_query(
            """
            SELECT j.id, j.title, j.company, j.location, j.source_platform, j.salary_range,
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
        # Populate estimated salary if raw salary is empty
        df["Estimated Salary / CTC"] = df.apply(
            lambda r: SalaryEstimator.get_salary_estimate(
                title=str(r["title"]),
                company=str(r["company"]),
                location=str(r["location"]),
                raw_salary=r["salary_range"]
            ),
            axis=1
        )

        st.dataframe(
            df[["id", "title", "company", "location", "source_platform", "Estimated Salary / CTC", "overall_match_score", "decision", "app_status", "source_url"]],
            use_container_width=True,
            column_config={
                "source_url": st.column_config.LinkColumn("Apply Link"),
                "overall_match_score": st.column_config.ProgressColumn(
                    "Match Score",
                    format="%.1f",
                    min_value=0,
                    max_value=100
                )
            }
        )

        st.markdown("### 🔍 Fresher Evaluation Reasoning Explorer")
        selected_job_id = st.selectbox("Select Job ID to view 0-experience fit analysis:", df["id"].tolist())
        if selected_job_id:
            row = df[df["id"] == selected_job_id].iloc[0]
            st.markdown(f"**Job Title**: {row['title']} at **{row['company']}**")
            st.markdown(f"**Estimated Salary / CTC**: `{row['Estimated Salary / CTC']}`")
            st.markdown(f"**Match Decision**: `{row['decision']}` | **Overall Score**: `{row['overall_match_score']}`")
            st.info(f"**LLM / Gatekeeper Reasoning**: {row['reasoning'] or 'Not evaluated yet.'}")

        st.subheader("📥 Export Pipeline Data")
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("Download Full CSV Report", csv, "fresher_jobs_report.csv", "text/csv")
    else:
        st.info("No fresher job listings present in database yet. Click '🚀 Run Autonomous Fresher Job Search' above to discover opportunities.")
