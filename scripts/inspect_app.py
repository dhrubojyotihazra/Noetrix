#!/usr/bin/env python3
"""Inspect actual app state to determine correct selectors for screenshots."""
import asyncio
from playwright.async_api import async_playwright

async def inspect():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(viewport={"width": 1440, "height": 860})
        await page.goto("http://localhost:3000", wait_until="networkidle", timeout=30000)
        await page.wait_for_timeout(6000)
        
        title = await page.title()
        url = page.url
        body_text = await page.evaluate("document.body.innerText")
        headings = await page.evaluate("[...document.querySelectorAll('h1,h2,h3')].map(e=>e.innerText)")
        
        print("Title:", title)
        print("URL:", url)
        print("Body text (first 1000 chars):")
        print(body_text[:1000])
        print("\nHeadings:", headings[:15])
        
        # Check what routes are available
        links = await page.evaluate("[...document.querySelectorAll('a[href]')].map(e=>e.href)")
        print("\nLinks found:", links[:20])
        
        # Take a screenshot to see what's rendered
        await page.screenshot(path="inspect_landing.png")
        print("\nSaved inspect_landing.png")
        
        # Check candidate route
        await page.goto("http://localhost:3000/candidate", wait_until="networkidle", timeout=20000)
        await page.wait_for_timeout(5000)
        cand_text = await page.evaluate("document.body.innerText")
        print("\n=== CANDIDATE PAGE ===")
        print(cand_text[:500])
        await page.screenshot(path="inspect_candidate.png")
        
        await browser.close()

asyncio.run(inspect())
