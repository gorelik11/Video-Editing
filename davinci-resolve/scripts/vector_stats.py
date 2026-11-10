"""Vectorscope proxy metrics for exported stills, optionally before -> after.

usage: vector_stats.py FRAME [FRAME_AFTER]
Prints: p99 chroma (CbCr radius x100), % pixels beyond radius 0.30,
mean saturation of blue/violet pixels (hue 200-290), of warm pixels
(hue <50 or >340) and the warm pixel share. 8-bit display-code proxy,
assumes Rec.709 display encoding; not IRE or legal-range measurement.
"""
import sys
import numpy as np
from PIL import Image


def stats(path):
    a = np.asarray(Image.open(path).convert("RGB"))[::4, ::4].astype(np.float32) / 255
    R, G, B = a[..., 0], a[..., 1], a[..., 2]
    Y = .2126 * R + .7152 * G + .0722 * B
    c = np.hypot((B - Y) / 1.8556, (R - Y) / 1.5748)
    mx, mn = a.max(2), a.min(2)
    d = mx - mn + 1e-6
    hue = np.where(mx == R, ((G - B) / d) % 6, np.where(mx == G, (B - R) / d + 2, (R - G) / d + 4)) * 60
    sat = d / (mx + 1e-6)
    vis = mx > 0.08
    blue = vis & (hue > 200) & (hue < 290)
    warm = vis & ((hue < 50) | (hue > 340))
    return {"p99": np.percentile(c, 99) * 100, "out": (c > 0.30).mean() * 100,
            "blue": sat[blue].mean() * 100 if blue.any() else 0.0,
            "warm": sat[warm].mean() * 100 if warm.any() else 0.0,
            "warm_share": warm.mean() * 100}


if __name__ == "__main__":
    b = stats(sys.argv[1])
    a = stats(sys.argv[2]) if len(sys.argv) > 2 else None
    for k, v in b.items():
        print(f"{k:10s} {v:6.1f}" + (f" -> {a[k]:6.1f}" if a else ""))
