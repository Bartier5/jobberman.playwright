import asyncio
from playwright.async_api import async_playwright

SEARCH_URL = "https://www.jobberman.com/jobs?q=developer"


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        await page.goto(SEARCH_URL, wait_until="domcontentloaded")
        await page.wait_for_timeout(4000)

        # 1. Dismiss the cookie banner (it covered the filters in your screenshot)
        accept = page.locator("#onetrust-accept-btn-handler")
        if await accept.count() > 0:
            await accept.click()
            print("Cookie banner dismissed")
        else:
            print("Cookie accept button not found by id")

        # 2. Print the options inside every <select> dropdown
        print("\n=== SELECT DROPDOWNS ===")
        selects = page.locator("select")
        for i in range(await selects.count()):
            sel = selects.nth(i)
            label = await sel.get_attribute("aria-label")
            options = await sel.locator("option").all_inner_texts()
            print(f"{label} -> {[o.strip() for o in options][:60]}")

        # 3. Open the Work Type section and print its HTML
        print("\n=== WORK TYPE SECTION ===")
        try:
            work_type = page.get_by_text("Work Type", exact=True).first
            await work_type.click(timeout=5000)
            await page.wait_for_timeout(1000)
            html = await work_type.evaluate("""
                el => {
                    let node = el;
                    for (let i = 0; i < 3 && node.parentElement; i++) node = node.parentElement;
                    return node.outerHTML.slice(0, 4000);
                }
            """)
            print(html)
        except Exception as error:
            print("Work Type step failed:", error)

        # 4. Try a location filter and see what the URL becomes
        print("\n=== URL AFTER LOCATION FILTER ===")
        try:
            await page.locator('select[aria-label="Select a location"]').select_option(
                label="Lagos", timeout=3000
            )
            await page.locator('button[aria-label="Search"]').first.click(timeout=3000)
            await page.wait_for_load_state("domcontentloaded")
            await page.wait_for_timeout(3000)
            print(page.url)
        except Exception as error:
            print("Location step failed:", error)

        await browser.close()


asyncio.run(main())