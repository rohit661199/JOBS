"""Naukri.com job discovery engine implementation."""
import hashlib
import urllib.parse
from typing import List
from bs4 import BeautifulSoup
import httpx
from database.models import JobListing
from job_search.base_search import BaseSearchEngine
from utils.logger import logger


class NaukriSearchEngine(BaseSearchEngine):
    """Scraper adapter implementation for Naukri.com job portal."""

    @property
    def platform_name(self) -> str:
        return "Naukri"

    async def search(self, query: str, location: str, max_results: int = 20) -> List[JobListing]:
        logger.info(f"[Naukri] Searching for '{query}' in '{location}'...")
        clean_q = query.lower().replace(" ", "-")
        clean_loc = location.lower().replace(" ", "-")
        url = f"https://www.naukri.com/{clean_q}-jobs-in-{clean_loc}"

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        }

        jobs: List[JobListing] = []
        try:
            async with httpx.AsyncClient(headers=headers, timeout=20.0, follow_redirects=True) as client:
                response = await client.get(url)
                if response.status_code != 200:
                    logger.warning(f"[Naukri] Search request returned status {response.status_code}")
                    return jobs

                soup = BeautifulSoup(response.text, "html.parser")
                articles = soup.find_all("article", class_="jobTuple")

                for article in articles:
                    if len(jobs) >= max_results:
                        break

                    title_elem = article.find("a", class_="title")
                    company_elem = article.find("a", class_="subTitle")
                    loc_elem = article.find("li", class_="location")

                    if not (title_elem and company_elem):
                        continue

                    title = title_elem.text.strip()
                    company = company_elem.text.strip()
                    loc = loc_elem.text.strip() if loc_elem else location
                    link = title_elem.get("href", "")

                    fingerprint_str = f"naukri_{company.lower()}_{title.lower()}_{link}"
                    fingerprint = hashlib.sha256(fingerprint_str.encode("utf-8")).hexdigest()

                    job = JobListing(
                        title=title,
                        company=company,
                        location=loc,
                        source_url=link,
                        source_platform="Naukri",
                        raw_description=f"Job Title: {title} at {company}. Location: {loc}. Listing Link: {link}",
                        fingerprint=fingerprint,
                    )
                    jobs.append(job)

        except Exception as e:
            logger.error(f"[Naukri] Error during search execution: {e}")

        logger.info(f"[Naukri] Discovered {len(jobs)} jobs for query '{query}'.")
        return jobs
