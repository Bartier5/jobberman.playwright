import asyncio
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeout

SEARCH_URL = "https://www.jobberman.com/jobs?q=developer"


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


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page(viewport={"width": 1280, "height": 900})

        def log_navigation(frame):
            if frame == page.main_frame:
                print("URL ->", frame.url)

        page.on("framenavigated", log_navigation)

        await page.goto(SEARCH_URL, wait_until="domcontentloaded")
        await accept_cookies(page)

        await asyncio.to_thread(
            input, "Apply filters by hand, then press Enter here to finish... "
        )
        await browser.close()


asyncio.run(main())