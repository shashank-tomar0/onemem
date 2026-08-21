"""Render the Excalidraw-style command-flow HTML to PNG using Playwright with better quality."""
import asyncio
from pathlib import Path

async def render():
    from playwright.async_api import async_playwright

    html_path = Path(__file__).parent / "command-flow.html"
    png_path = Path(__file__).parent / "command-flow.png"

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(
            viewport={"width": 1200, "height": 800},
            device_scale_factor=2  # 2x for crisp rendering
        )
        await page.goto(f"file:///{html_path.resolve()}")
        # Wait for Google Fonts to load
        await page.wait_for_timeout(4000)
        
        # Get actual content height
        height = await page.evaluate("document.body.scrollHeight")
        await page.set_viewport_size({"width": 1200, "height": height})
        await page.wait_for_timeout(500)
        
        # Screenshot the full page
        await page.screenshot(path=str(png_path), full_page=True)
        await browser.close()
        
        size = png_path.stat().st_size
        print(f"Wrote {png_path} ({size:,} bytes, {size/1024:.0f} KB)")

if __name__ == "__main__":
    asyncio.run(render())
