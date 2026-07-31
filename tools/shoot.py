"""Deterministic screenshot harness for the restyle pass.

Captures every scroll stop (7) and hash route (4) at 375 / 820 / 1440 px wide
into screenshots/<name>/. Determinism measures, applied identically to every run
so baseline-vs-after diffs isolate real styling changes:
  - all CSS animations/transitions forced off (ship tumble, pulse dot, cue drop,
    halo ease all land in their final resting state)
  - the starfield canvas is hidden: its stars are Math.random() per page load,
    so it can never diff cleanly run-to-run
The Z-dolly JS keeps running (it is what positions the scene per scroll stop).

Usage: python tools/shoot.py <run-name>   e.g. baseline, after-1
"""
import sys, time
from pathlib import Path
from playwright.sync_api import sync_playwright

BASE = "http://localhost:8788/"
SPACING = 1600  # must match SPACING in index.html's dolly
STOPS = ["top", "now", "blue-origin", "clubs", "education", "trading", "contact"]
ROUTES = ["now", "blue-origin", "clubs", "trading"]
VIEWPORTS = {"375": (375, 812), "820": (820, 1024), "1440": (1440, 900)}
SETTLE_S = 2.2  # dolly cam lerp (0.1/frame) needs ~90 frames to converge

FREEZE_CSS = """
*, *::before, *::after { animation: none !important; transition: none !important; }
#space { visibility: hidden !important; }
"""

def wait_deep_images(page):
    try:
        page.wait_for_function(
            "Array.from(document.querySelectorAll('#deepPanel img')).every(i => i.complete)",
            timeout=8000)
    except Exception:
        pass  # capture whatever state we have; identical logic on every run

def main():
    name = sys.argv[1] if len(sys.argv) > 1 else "run"
    out = Path(__file__).resolve().parent.parent / "screenshots" / name
    out.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        browser = p.chromium.launch(channel="chrome", headless=True,
                                    args=["--hide-scrollbars"])
        for label, (w, h) in VIEWPORTS.items():
            ctx = browser.new_context(viewport={"width": w, "height": h},
                                      device_scale_factor=1)
            page = ctx.new_page()
            page.goto(BASE, wait_until="networkidle")
            page.add_style_tag(content=FREEZE_CSS)
            page.evaluate("document.fonts.ready")
            time.sleep(0.4)
            for i, loc in enumerate(STOPS):
                page.evaluate(f"scrollTo({{top: {i * SPACING}, behavior: 'auto'}})")
                time.sleep(SETTLE_S)
                page.screenshot(path=str(out / f"{label}-stop{i}-{loc}.png"))
            page.evaluate("scrollTo({top: 0, behavior: 'auto'})")
            time.sleep(SETTLE_S)
            for r in ROUTES:
                page.evaluate(f"location.hash = '#/{r}'")
                wait_deep_images(page)
                time.sleep(0.6)
                page.screenshot(path=str(out / f"{label}-route-{r}.png"))
            ctx.close()
        browser.close()
    print(f"captured {len(VIEWPORTS) * (len(STOPS) + len(ROUTES))} shots -> {out}")

if __name__ == "__main__":
    main()
