import asyncio
from urllib.parse import quote_plus
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeout

BASE_URL = "https://www.jobberman.com/jobs"
KEYWORD = "developer"

LOCATIONS = ["lagos", "abuja", "remote"]
JOB_TYPES = ["full-time"]

CARD_SELECTOR = '[data-cy="listing-cards-components"]'
TITLE_SELECTOR = '[data-cy="listing-title-link"]'
COMPANY_XPATH = "xpath=ancestor::div[1]/following-sibling::p[1]"


def build_url(location, job_type, keyword):
    return f"{BASE_URL}/{location}/{job_type}?q={quote_plus(keyword)}"


async def accept_cookies(page):
    button = page.locator('[aria-label="Cookie banner"]').get_by_role(
        "button", name="Accept All Cookies"
    )
    try:
        await button.wait_for(state="visible", timeout=10000)
        await button.click()
        await button.wait_for(state="hidden", timeout=5000)
        print("Cookie banner accepted")
    except PlaywrightTimeout:
        print("No cookie banner appeared (or it was already gone)")


async def safe_text(locator):
    if await locator.count() == 0:
        return "N/A"
    return (await locator.first.inner_text()).strip()


async def scrape_current_page(page):
    try:
        await page.wait_for_selector(CARD_SELECTOR, timeout=15000)
    except PlaywrightTimeout:
        return []

    cards = page.locator(CARD_SELECTOR).filter(has=page.locator(TITLE_SELECTOR))
    total = await cards.count()

    jobs = []
    for i in range(total):
        card = cards.nth(i)
        title_link = card.locator(TITLE_SELECTOR).first
        title = await safe_text(title_link)
        company = await safe_text(title_link.locator(COMPANY_XPATH))
        url = await title_link.get_attribute("href")
        jobs.append({"title": title, "company": company, "url": url})
    return jobs


async def scrape_filtered(page, location, job_type):
    url = build_url(location, job_type, KEYWORD)
    await page.goto(url, wait_until="domcontentloaded")

    if page.url.split("?")[0] != url.split("?")[0]:
        print(f"Warning: {url} redirected to {page.url}")

    jobs = await scrape_current_page(page)
    for job in jobs:
        job["location"] = location
        job["job_type"] = job_type
    return jobs


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page(viewport={"width": 1280, "height": 900})

        await page.goto("https://www.jobberman.com", wait_until="domcontentloaded")
        await accept_cookies(page)

        all_jobs = []
        for location in LOCATIONS:
            for job_type in JOB_TYPES:
                jobs = await scrape_filtered(page, location, job_type)
                print(f"{location} + {job_type}: {len(jobs)} jobs")
                all_jobs.extend(jobs)

        await browser.close()

    print(f"\nTotal: {len(all_jobs)} jobs")
    for number, job in enumerate(all_jobs, start=1):
        print(f"{number}. [{job['location']} | {job['job_type']}] "
              f"{job['title']} | {job['company']}")


if __name__ == "__main__":
    asyncio.run(main())