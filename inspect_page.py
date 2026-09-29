import asyncio
from playwright.async_api import async_playwright

SEARCH_URL = "https://www.jobberman.com/jobs?q=Python+developer"


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        await page.goto(SEARCH_URL, wait_until="domcontentloaded")
        await page.wait_for_timeout(5000)

        # Part 1: every stable attribute on the page, with its tag name
        hooks = await page.evaluate("""
            () => [...document.querySelectorAll('*')].flatMap(el =>
                [...el.attributes]
                    .filter(a => ['data-cy', 'data-testid', 'aria-label'].includes(a.name) && a.value)
                    .map(a => `${el.tagName.toLowerCase()} [${a.name}="${a.value}"]`)
            )
        """)
        print("=== STABLE ATTRIBUTES ===")
        for hook in sorted(set(hooks)):
            print(hook)

        # Part 2: the HTML around the first job listing link
        card_html = await page.evaluate("""
            () => {
                const link = document.querySelector('a[href*="/listings/"]');
                if (!link) return 'NO LISTING LINK FOUND';
                let el = link;
                for (let i = 0; i < 4 && el.parentElement; i++) el = el.parentElement;
                return el.outerHTML.slice(0, 3000);
            }
        """)
        print("\n=== FIRST JOB CARD HTML ===")
        print(card_html)

        await browser.close()


asyncio.run(main())