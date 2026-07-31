"""RemoteOK and remote job board discovery engine implementation."""
import hashlib
from typing import List
import httpx
from database.models import JobListing
from job_search.base_search import BaseSearchEngine
from utils.logger import logger


class RemoteOKSearchEngine(BaseSearchEngine):
    """API scraper adapter for RemoteOK public API."""

    @property
    def platform_name(self) -> str:
        return "RemoteOK"

    async def search(self, query: str, location: str, max_results: int = 20) -> List[JobListing]:
        logger.info(f"[RemoteOK] Fetching remote opportunities matching query '{query}'...")
        url = "https://remoteok.com/api"

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        }

        jobs: List[JobListing] = []
        try:
            async with httpx.AsyncClient(headers=headers, timeout=20.0, follow_redirects=True) as client:
                response = await client.get(url)
                if response.status_code != 200:
                    logger.warning(f"[RemoteOK] Search request returned status {response.status_code}")
                    return jobs

                data = response.json()
                if isinstance(data, list) and len(data) > 1:
                    raw_items = data[1:]  # First element is API legal notice metadata
                    q_lower = query.lower()

                    for item in raw_items:
                        if len(jobs) >= max_results:
                            break

                        position = item.get("position", "")
                        company = item.get("company", "")
                        tags = [t.lower() for t in item.get("tags", [])]
                        description = item.get("description", "")

                        # Filter by query keyword overlap in title or tags
                        if not (q_lower in position.lower() or any(q_lower in t for t in tags)):
                            continue

                        link = item.get("url", f"https://remoteok.com/remote-jobs/{item.get('id', '')}")

                        fingerprint_str = f"remoteok_{company.lower()}_{position.lower()}_{link}"
                        fingerprint = hashlib.sha256(fingerprint_str.encode("utf-8")).hexdigest()

                        job = JobListing(
                            title=position,
                            company=company,
                            location="Remote",
                            source_url=link,
                            source_platform="RemoteOK",
                            raw_description=f"Position: {position} at {company}.\nTags: {', '.join(tags)}.\nDescription: {description[:1000]}",
                            fingerprint=fingerprint,
                        )
                        jobs.append(job)

        except Exception as e:
            logger.error(f"[RemoteOK] Error during search execution: {e}")

        logger.info(f"[RemoteOK] Discovered {len(jobs)} jobs for query '{query}'.")
        return jobs
