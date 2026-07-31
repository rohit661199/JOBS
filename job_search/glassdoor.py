"""Glassdoor job discovery engine implementation."""
import hashlib
import urllib.parse
from typing import List
from bs4 import BeautifulSoup
import httpx
from database.models import JobListing
from job_search.base_search import BaseSearchEngine
from utils.logger import logger


class GlassdoorSearchEngine(BaseSearchEngine):
    """Scraper adapter for Glassdoor Jobs."""

    @property
    def platform_name(self) -> str:
        return "Glassdoor"

    async def search(self, query: str, location: str, max_results: int = 20) -> List[JobListing]:
        logger.info(f"[Glassdoor] Searching for '{query}' in '{location}'...")
        encoded_query = urllib.parse.quote(query)
        encoded_loc = urllib.parse.quote(location)
        url = f"https://www.glassdoor.com/Job/jobs.htm?sc.keyword={encoded_query}&locT=&locId="

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        }

        jobs: List[JobListing] = []
        try:
            async with httpx.AsyncClient(headers=headers, timeout=20.0, follow_redirects=True) as client:
                response = await client.get(url)
                if response.status_code != 200:
                    logger.warning(f"[Glassdoor] Search request returned status {response.status_code}")
                    return jobs

                soup = BeautifulSoup(response.text, "html.parser")
                cards = soup.find_all("li", class_="JobsList_jobListItem__25261")

                for card in cards:
                    if len(jobs) >= max_results:
                        break

                    title_elem = card.find("a", class_="JobCard_jobTitle___7221")
                    company_elem = card.find("span", class_="EmployerProfile_employerName__9h3R5")

                    if not (title_elem and company_elem):
                        continue

                    title = title_elem.text.strip()
                    company = company_elem.text.strip()
                    link = title_elem.get("href", "")

                    fingerprint_str = f"glassdoor_{company.lower()}_{title.lower()}_{link}"
                    fingerprint = hashlib.sha256(fingerprint_str.encode("utf-8")).hexdigest()

                    job = JobListing(
                        title=title,
                        company=company,
                        location=location,
                        source_url=link,
                        source_platform="Glassdoor",
                        raw_description=f"Job Title: {title} at {company}. Glassdoor URL: {link}",
                        fingerprint=fingerprint,
                    )
                    jobs.append(job)

        except Exception as e:
            logger.error(f"[Glassdoor] Error during search execution: {e}")

        logger.info(f"[Glassdoor] Discovered {len(jobs)} jobs for query '{query}'.")
        return jobs
