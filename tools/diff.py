"""Compare two screenshot runs pixel-by-pixel.

Usage: python tools/diff.py <run-a> <run-b> [--threshold 8]
Prints, per image pair: count of pixels whose max channel delta exceeds the
threshold, as a percentage, plus the bounding box of the changed region.
"""
import sys
from pathlib import Path
from PIL import Image, ImageChops

def main():
    a_name, b_name = sys.argv[1], sys.argv[2]
    thr = int(sys.argv[sys.argv.index("--threshold") + 1]) if "--threshold" in sys.argv else 8
    root = Path(__file__).resolve().parent.parent / "screenshots"
    a_dir, b_dir = root / a_name, root / b_name
    names = sorted(p.name for p in a_dir.glob("*.png"))
    clean = 0
    for n in names:
        pb = b_dir / n
        if not pb.exists():
            print(f"{n:34s} MISSING in {b_name}")
            continue
        ia, ib = Image.open(a_dir / n).convert("RGB"), Image.open(pb).convert("RGB")
        if ia.size != ib.size:
            print(f"{n:34s} SIZE {ia.size} vs {ib.size}")
            continue
        diff = ImageChops.difference(ia, ib).convert("L")
        mask = diff.point(lambda v: 255 if v > thr else 0)
        bbox = mask.getbbox()
        changed = sum(1 for v in mask.getdata() if v)
        pct = 100.0 * changed / (ia.size[0] * ia.size[1])
        if bbox is None:
            clean += 1
        else:
            print(f"{n:34s} {pct:6.2f}% changed  bbox={bbox}")
    print(f"-- {clean}/{len(names)} identical (threshold {thr})")

if __name__ == "__main__":
    main()
