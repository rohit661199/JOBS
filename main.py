"""Autonomous AI Job Search & Application Agent CLI entry point."""
import argparse
import asyncio
import sys
from pathlib import Path
from application.orchestrator import ApplicationOrchestrator
from config.settings import settings
from resume.analyzer import ResumeAnalyzer
from utils.logger import logger


def parse_args():
    parser = argparse.ArgumentParser(description="Autonomous AI Job Search & Application Agent")
    parser.add_argument(
        "--mode",
        choices=["run", "parse", "search"],
        default="run",
        help="Mode of operation: 'run' (full pipeline), 'parse' (extract resume only), 'search' (discover jobs only)."
    )
    parser.add_argument(
        "--resume",
        type=str,
        default=settings.resume_path,
        help="Path to candidate master resume file."
    )
    return parser.parse_args()


async def main_async():
    args = parse_args()
    logger.info("Initializing Autonomous AI Job Search Agent...")

    if args.mode == "parse":
        logger.info(f"Executing resume analysis on: {args.resume}")
        analyzer = ResumeAnalyzer()
        profile = analyzer.analyze(args.resume, force_refresh=True)
        print("\n" + "=" * 50)
        print(f"Candidate: {profile.full_name or 'N/A'}")
        print(f"Email: {profile.email or 'N/A'}")
        print(f"Inferred Careers: {', '.join(profile.inferred_careers)}")
        print(f"Generated Search Queries: {profile.inferred_search_queries}")
        print("=" * 50 + "\n")

    elif args.mode == "run":
        orchestrator = ApplicationOrchestrator(resume_path=args.resume)
        results = await orchestrator.run_full_pipeline()
        print("\n" + "=" * 50)
        print("PIPELINE CYCLE COMPLETE")
        print(f"Discovered Jobs: {results['jobs_discovered']}")
        print(f"Evaluated Jobs: {results['jobs_evaluated']}")
        print(f"Applications Queued: {results['applications_queued']}")
        print("Launch dashboard using: streamlit run dashboard/app.py")
        print("=" * 50 + "\n")


def main():
    asyncio.run(main_async())


if __name__ == "__main__":
    main()
