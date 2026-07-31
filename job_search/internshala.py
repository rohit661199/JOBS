"""Internshala job discovery engine implementation."""
import hashlib
import urllib.parse
from typing import List
from bs4 import BeautifulSoup
import httpx
from database.models import JobListing
from job_search.base_search import BaseSearchEngine
from utils.logger import logger


class InternshalaSearchEngine(BaseSearchEngine):
    """Scraper adapter for Internshala jobs."""

    @property
    def platform_name(self) -> str:
        return "Internshala"

    async def search(self, query: str, location: str, max_results: int = 20) -> List[JobListing]:
        logger.info(f"[Internshala] Searching for '{query}'...")
        encoded_query = urllib.parse.quote(query)
        url = f"https://internshala.com/jobs/{encoded_query}-jobs"

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        }

        jobs: List[JobListing] = []
        try:
            async with httpx.AsyncClient(headers=headers, timeout=20.0, follow_redirects=True) as client:
                response = await client.get(url)
                if response.status_code != 200:
                    logger.warning(f"[Internshala] Search request returned status {response.status_code}")
                    return jobs

                soup = BeautifulSoup(response.text, "html.parser")
                cards = soup.find_all("div", class_="individual_internship")

                for card in cards:
                    if len(jobs) >= max_results:
                        break

                    title_elem = card.find("h3", class_="job-internship-name")
                    company_elem = card.find("p", class_="company-name")
                    loc_elem = card.find("a", class_="location_link")

                    if not (title_elem and company_elem):
                        continue

                    title = title_elem.text.strip()
                    company = company_elem.text.strip()
                    loc = loc_elem.text.strip() if loc_elem else location
                    link = f"https://internshala.com{card.get('data-href', '')}"

                    fingerprint_str = f"internshala_{company.lower()}_{title.lower()}_{link}"
                    fingerprint = hashlib.sha256(fingerprint_str.encode("utf-8")).hexdigest()

                    job = JobListing(
                        title=title,
                        company=company,
                        location=loc,
                        source_url=link,
                        source_platform="Internshala",
                        raw_description=f"Job Title: {title} at {company}. Location: {loc}. Internshala link: {link}",
                        fingerprint=fingerprint,
                    )
                    jobs.append(job)

        except Exception as e:
            logger.error(f"[Internshala] Error during search execution: {e}")

        logger.info(f"[Internshala] Discovered {len(jobs)} jobs for query '{query}'.")
        return jobs
