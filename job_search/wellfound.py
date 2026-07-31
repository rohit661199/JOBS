"""Wellfound (AngelList) startup job discovery engine implementation."""
import hashlib
import urllib.parse
from typing import List
from bs4 import BeautifulSoup
import httpx
from database.models import JobListing
from job_search.base_search import BaseSearchEngine
from utils.logger import logger


class WellfoundSearchEngine(BaseSearchEngine):
    """Scraper adapter for Wellfound (AngelList) startup job postings."""

    @property
    def platform_name(self) -> str:
        return "Wellfound"

    async def search(self, query: str, location: str, max_results: int = 20) -> List[JobListing]:
        logger.info(f"[Wellfound] Searching for '{query}' in '{location}'...")
        encoded_query = urllib.parse.quote(query)
        url = f"https://wellfound.com/jobs?q={encoded_query}"

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        }

        jobs: List[JobListing] = []
        try:
            async with httpx.AsyncClient(headers=headers, timeout=20.0, follow_redirects=True) as client:
                response = await client.get(url)
                if response.status_code != 200:
                    logger.warning(f"[Wellfound] Search request returned status {response.status_code}")
                    return jobs

                soup = BeautifulSoup(response.text, "html.parser")
                cards = soup.find_all("div", class_="styles_jobListing__")

                for card in cards:
                    if len(jobs) >= max_results:
                        break

                    title_elem = card.find("a", class_="styles_title__")
                    company_elem = card.find("span", class_="styles_startupName__")

                    if not (title_elem and company_elem):
                        continue

                    title = title_elem.text.strip()
                    company = company_elem.text.strip()
                    link = f"https://wellfound.com{title_elem.get('href', '')}"

                    fingerprint_str = f"wellfound_{company.lower()}_{title.lower()}_{link}"
                    fingerprint = hashlib.sha256(fingerprint_str.encode("utf-8")).hexdigest()

                    job = JobListing(
                        title=title,
                        company=company,
                        location=location,
                        source_url=link,
                        source_platform="Wellfound",
                        raw_description=f"Startup Position: {title} at {company}. Wellfound link: {link}",
                        fingerprint=fingerprint,
                    )
                    jobs.append(job)

        except Exception as e:
            logger.error(f"[Wellfound] Error during search execution: {e}")

        logger.info(f"[Wellfound] Discovered {len(jobs)} jobs for query '{query}'.")
        return jobs
