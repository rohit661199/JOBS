"""Dynamic Playwright form filler mapping candidate fields to web inputs across common Applicant Tracking Systems (ATS)."""
from pathlib import Path
from playwright.async_api import Page
from database.models import CandidateProfile
from utils.logger import logger


class DynamicFormFiller:
    """Automates standard job application form fields, multi-step inputs, file uploads, radios, and text inputs."""

    @staticmethod
    async def fill_application_form(page: Page, profile: CandidateProfile, resume_path: str) -> bool:
        """Fills standard input controls and multi-step ATS application forms.

        Args:
            page: Playwright page instance.
            profile: CandidateProfile model instance.
            resume_path: Path to master resume file.

        Returns:
            True if form filling completed successfully.
        """
        logger.info(f"Attempting dynamic form completion for candidate: {profile.full_name or 'Applicant'}")

        try:
            # 1. First & Last Name or Full Name
            if profile.full_name:
                name_parts = profile.full_name.strip().split(" ", 1)
                first_name = name_parts[0]
                last_name = name_parts[1] if len(name_parts) > 1 else ""

                # First Name
                fn_input = await page.query_selector("input[name*='first_name'], input[id*='first_name'], input[autocomplete='given-name']")
                if fn_input and await fn_input.is_visible():
                    await fn_input.fill(first_name)

                # Last Name
                ln_input = await page.query_selector("input[name*='last_name'], input[id*='last_name'], input[autocomplete='family-name']")
                if ln_input and await ln_input.is_visible():
                    await ln_input.fill(last_name)

                # Full Name fallback
                fn_full = await page.query_selector("input[name*='name']:not([name*='first']):not([name*='last']), input[id='name']")
                if fn_full and await fn_full.is_visible():
                    await fn_full.fill(profile.full_name)

            # 2. Email Address
            if profile.email:
                email_input = await page.query_selector("input[type='email'], input[name*='email'], input[id*='email']")
                if email_input and await email_input.is_visible():
                    await email_input.fill(profile.email)

            # 3. Phone Number
            if profile.phone:
                phone_input = await page.query_selector("input[type='tel'], input[name*='phone'], input[id*='phone']")
                if phone_input and await phone_input.is_visible():
                    await phone_input.fill(profile.phone)

            # 4. Years of Experience (if present)
            exp_input = await page.query_selector("input[name*='experience'], input[id*='experience']")
            if exp_input and await exp_input.is_visible():
                await exp_input.fill("3")

            # 5. Work Authorization Radios (Select 'Yes' for legal work authorization)
            auth_radios = await page.query_selector_all("input[type='radio'][value='1'], input[type='radio'][value='yes'], input[type='radio'][id*='authorized']")
            for radio in auth_radios[:1]:
                if await radio.is_visible():
                    await radio.check()

            # 6. Resume File Upload
            file_input = await page.query_selector("input[type='file']")
            if file_input:
                r_path = Path(resume_path)
                if r_path.exists():
                    await file_input.set_input_files(str(r_path.resolve()))
                    logger.info(f"Uploaded master resume: {r_path.name}")

            logger.info("Dynamic multi-step form filling finished.")
            return True
        except Exception as e:
            logger.error(f"Error during dynamic form filling: {e}")
            return False
