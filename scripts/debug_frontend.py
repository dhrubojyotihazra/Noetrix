import asyncio
from playwright.async_api import async_playwright

async def check():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        
        errors = []
        page.on('console', lambda msg: errors.append(f"CONSOLE {msg.type}: {msg.text}"))
        page.on('pageerror', lambda err: errors.append(f"PAGEERROR: {err}"))
        page.on('requestfailed', lambda req: errors.append(f"FAILED REQ: {req.url} - {req.failure}"))
        
        resp = await page.goto('http://localhost:3000', wait_until='networkidle')
        print(f"Status: {resp.status}")
        
        css_links = await page.evaluate("Array.from(document.querySelectorAll('link[rel=stylesheet]')).map(l => l.href)")
        print("CSS links:", css_links)
        
        computed = await page.evaluate("window.getComputedStyle(document.body).backgroundColor")
        print("Body bg:", computed)

        img_style = await page.evaluate("(() => { const img = document.querySelector('img[alt=\"Noetrix Logo\"]'); return img ? {w: img.clientWidth, h: img.clientHeight, naturalW: img.naturalWidth, class: img.className} : null; })()")
        print("Logo img style:", img_style)
        
        print(f"Errors count: {len(errors)}")
        for e in errors[:20]:
            print("  ", e)
            
        await browser.close()

if __name__ == '__main__':
    asyncio.run(check())
