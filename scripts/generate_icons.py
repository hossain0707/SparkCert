"""Generate consistent PNG, ICO and ICNS app icons from a vector-like draw.

Build-only Pillow dependency. No external images/fonts or network needed.
"""
from __future__ import annotations

from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / "assets"
DEST.mkdir(exist_ok=True)
SIZE = 1024
SCALE = 4

base = Image.new("RGBA", (SIZE * SCALE, SIZE * SCALE), (0, 0, 0, 0))
d = ImageDraw.Draw(base)
m = SIZE * SCALE
margin = 75 * SCALE
radius = 220 * SCALE
# Rounded slate canvas and subtle layered frame.
d.rounded_rectangle((margin, margin, m-margin, m-margin), radius=radius,
                    fill="#0B1C2B", outline="#416477", width=12*SCALE)
d.rounded_rectangle((124*SCALE, 124*SCALE, 900*SCALE, 900*SCALE), radius=155*SCALE,
                    fill="#133449")
# Spark / verifiable pulse: thick, rounded neon path.
path = [(247, 565), (379, 565), (474, 323), (550, 716), (657, 473), (778, 473)]
p=[(x*SCALE,y*SCALE) for x,y in path]
d.line(p, fill="#55EBC0", width=60*SCALE, joint="curve")
r=29*SCALE
for x,y in [p[0], p[-1]]:
    d.ellipse((x-r,y-r,x+r,y+r),fill="#55EBC0")
# Top-right small star suggests verification rather than NVIDIA branding.
star=[(755,235),(777,287),(829,309),(777,331),(755,383),(733,331),(681,309),(733,287)]
d.polygon([(x*SCALE,y*SCALE) for x,y in star], fill="#ACEDFA")
img=base.resize((SIZE,SIZE), Image.Resampling.LANCZOS)
img.save(DEST / "sparkcert-icon.png", optimize=True)
img.save(DEST / "sparkcert-icon.ico", format="ICO", sizes=[(16,16),(24,24),(32,32),(48,48),(64,64),(128,128),(256,256)])
img.save(DEST / "sparkcert-icon.icns", format="ICNS")
print("Generated branded SparkCert application icons.")
