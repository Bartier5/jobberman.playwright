import asyncio
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeout

SEARCH_URL = "https://www.jobberman.com/jobs?q=Python+developer"

# Selectors confirmed against the live page
CARD_SELECTOR = '[data-cy="listing-cards-components"]'
TITLE_SELECTOR = '[data-cy="listing-title-link"]'
COMPANY_XPATH = "xpath=ancestor::div[1]/following-sibling::p[1]"


async def safe_text(locator):
    """Return the text of a locator, or 'N/A' if nothing matched."""
    if await locator.count() == 0:
        return "N/A"
    return (await locator.first.inner_text()).strip()


async def scrape_jobs():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()

        await page.goto(SEARCH_URL, wait_until="domcontentloaded")

        try:
            await page.wait_for_selector(CARD_SELECTOR, timeout=15000)
        except PlaywrightTimeout:
            await page.screenshot(path="debug_timeout.png")
            print("No job cards found. Check CARD_SELECTOR and debug_timeout.png")
            await browser.close()
            return []

        # Keep only cards that actually contain a job title link
        cards = page.locator(CARD_SELECTOR).filter(has=page.locator(TITLE_SELECTOR))
        total = await cards.count()
        print(f"Found {total} job cards")

        jobs = []
        for i in range(total):
            card = cards.nth(i)
            title_link = card.locator(TITLE_SELECTOR).first
            title = await safe_text(title_link)
            company = await safe_text(title_link.locator(COMPANY_XPATH))
            jobs.append({"title": title, "company": company})

        await browser.close()
        return jobs


async def main():
    jobs = await scrape_jobs()
    for number, job in enumerate(jobs, start=1):
        print(f"{number}. {job['title']} | {job['company']}")


if __name__ == "__main__":
    asyncio.run(main())