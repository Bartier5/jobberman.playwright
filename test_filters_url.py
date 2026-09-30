import asyncio
from playwright.async_api import async_playwright

BASE = "https://www.jobberman.com"
TITLE_SELECTOR = '[data-cy="listing-title-link"]'

TEST_PATHS = [
    "/jobs/lagos?q=developer",
    "/jobs/abuja?q=developer",
    "/jobs/remote?q=developer",
    "/jobs/full-time?q=developer",
    "/jobs/lagos/full-time?q=developer",
    "/jobs/full-time/lagos?q=developer",
    "/jobs/abuja/full-time?q=developer",
    "/jobs/remote/full-time?q=developer",
]


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page(viewport={"width": 1280, "height": 900})

        for path in TEST_PATHS:
            response = await page.goto(BASE + path, wait_until="domcontentloaded")
            await page.wait_for_timeout(2500)

            status = response.status if response else "none"
            title = await page.title()
            job_count = await page.locator(TITLE_SELECTOR).count()

            print(path)
            print(f"   status={status} | job links on page={job_count}")
            print(f"   final url={page.url}")
            print(f"   title={title}")

        await browser.close()


asyncio.run(main())