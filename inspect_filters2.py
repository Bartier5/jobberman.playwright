import asyncio
from playwright.async_api import async_playwright

SEARCH_URL = "https://www.jobberman.com/jobs?q=developer"
SIDEBAR_HEADINGS = ["Job Function", "Industry", "Location", "Work Type", "Experience Level"]


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        await page.goto(SEARCH_URL, wait_until="domcontentloaded")
        await page.wait_for_timeout(4000)

        # 1. Dismiss the cookie banner using the stable aria-label
        banner = page.locator('[aria-label="Cookie banner"]')
        accept = banner.get_by_role("button", name="Accept All Cookies")
        try:
            await accept.click(timeout=5000)
            print("Cookie banner dismissed")
        except Exception as error:
            print("Cookie step failed:", error)

        # 2. HTML around the hidden location <select> (the visible widget lives nearby)
        print("\n=== AROUND LOCATION SELECT ===")
        html = await page.locator("#location").first.evaluate("""
            el => {
                let node = el;
                for (let i = 0; i < 2 && node.parentElement; i++) node = node.parentElement;
                return node.outerHTML.slice(0, 3000);
            }
        """)
        print(html)

        # 3. Open every sidebar section so its checkboxes/radios exist on the page
        for heading in SIDEBAR_HEADINGS:
            try:
                await page.get_by_text(heading, exact=True).first.click(timeout=2000)
            except Exception:
                print(f"Could not open section: {heading}")
        await page.wait_for_timeout(1000)

        # 4. List every form on the page
        print("\n=== FORMS ===")
        forms = await page.evaluate("""
            () => [...document.querySelectorAll('form')]
                .map(f => `${f.method.toUpperCase()} ${f.action}`)
        """)
        for form in forms:
            print(form)

        # 5. List every field inside the sidebar filter form
        print("\n=== SIDEBAR FORM FIELDS ===")
        fields = await page.evaluate("""
            () => [...document.querySelectorAll(
                'form.sidebar-filter-form input, form.sidebar-filter-form select')]
                .map(el => {
                    const label = (el.labels && el.labels[0]) ? el.labels[0].innerText.trim() : '';
                    return `${el.tagName.toLowerCase()} | type=${el.type} | name=${el.name}`
                        + ` | id=${el.id} | value=${el.value}`
                        + ` | aria-label=${el.getAttribute('aria-label') || ''} | label=${label}`;
                })
        """)
        for field in fields:
            print(field)

        await browser.close()


asyncio.run(main())