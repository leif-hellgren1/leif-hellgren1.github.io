"""Render og-card.png, the 1200x630 image link previews use.

Built from the site's own palette and type so a shared link looks like the page it opens.
Regenerate after changing the name mark, headline, or palette:

    python tools/make-og.py
"""
from pathlib import Path
from playwright.sync_api import sync_playwright

OUT = Path(__file__).resolve().parent.parent / "og-card.png"

TEMPLATE = """
<!DOCTYPE html><html><head><meta charset="utf-8">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@300;500&family=Cabin:wght@500&display=swap" rel="stylesheet">
<link href="https://api.fontshare.com/v2/css?f[]=cabinet-grotesk@800&display=swap" rel="stylesheet">
<style>
  :root { --bg:#0a0b0f; --ink:#eef1f7; --ink-dim:#9aa3b2; --accent:#ff8a4c; }
  * { margin:0; padding:0; box-sizing:border-box; }
  body { width:1200px; height:630px; background:var(--bg); overflow:hidden;
         font-family:"IBM Plex Sans",sans-serif; -webkit-font-smoothing:antialiased; }
  .amb { position:absolute; inset:0;
    background:
      radial-gradient(55% 45% at 78% 12%, rgba(88,120,255,0.10), transparent 70%),
      radial-gradient(60% 55% at 15% 85%, rgba(150,80,220,0.08), transparent 70%),
      radial-gradient(45% 40% at 30% 20%, rgba(255,138,76,0.06), transparent 70%),
      linear-gradient(180deg,#0a0b0f 0%,#0b0d14 55%,#0a0b0f 100%); }
  .wrap { position:relative; padding:76px 84px; height:100%;
          display:flex; flex-direction:column; justify-content:space-between; }
  .name { font-family:"Gill Sans","Gill Sans MT","Cabin",sans-serif; font-weight:500;
          text-transform:uppercase; letter-spacing:0.22em; font-size:23px; color:var(--ink); }
  h1 { font-family:"Cabinet Grotesk","IBM Plex Sans",sans-serif; font-weight:800;
       font-size:76px; line-height:1.05; letter-spacing:-0.02em; color:var(--ink); }
  p  { margin-top:26px; font-size:25px; line-height:1.5; color:var(--ink-dim); max-width:44ch; font-weight:300; }
  .foot { display:flex; align-items:center; gap:12px; font-size:22px; color:var(--ink); font-weight:500; }
  .dot { width:10px; height:10px; border-radius:50%; background:var(--accent);
         box-shadow:0 0 12px rgba(255,138,76,0.7); }
</style></head><body>
  <div class="amb"></div>
  <div class="wrap">
    <div class="name">Leif Hellgren</div>
    <div>
      <h1>Physics. Rockets.<br>AI. GTM.</h1>
      <p>Flight-critical subsystem on Blue Origin's first lunar lander. Python and LLM systems built solo.</p>
    </div>
    <div class="foot"><span class="dot"></span>Looking for my next role in NYC</div>
  </div>
</body></html>
"""

def main():
    with sync_playwright() as p:
        b = p.chromium.launch(channel="chrome", headless=True)
        pg = b.new_page(viewport={"width": 1200, "height": 630}, device_scale_factor=1)
        pg.set_content(TEMPLATE, wait_until="networkidle")
        pg.evaluate("document.fonts.ready")
        pg.wait_for_timeout(700)
        pg.screenshot(path=str(OUT))
        b.close()
    print(f"wrote {OUT} ({OUT.stat().st_size // 1024} KB)")

if __name__ == "__main__":
    main()
