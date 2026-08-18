#!/usr/bin/env python3
"""Rebuild the web derivatives in assets/ from the originals in media/.

Why this exists: whatever produced the current assets/ decoded each photograph and threw
away its EXIF Orientation tag WITHOUT applying it. `sips` does not rotate on conversion —
verified — so fifteen portrait photographs are stored, and were published, on their side.

Usage
  python3 convert.py --check          list sources whose derivatives are wrong or missing
  python3 convert.py --fix            re-convert only those
  python3 convert.py --all            rebuild every derivative from scratch

Requires macOS `sips` (decode), `cwebp` and `avifenc` (encode). Videos and their poster
frames are not touched.
"""
import argparse, pathlib, re, struct, subprocess, sys, tempfile

ROOT = pathlib.Path(__file__).parent
MEDIA, ASSETS = ROOT / "media", ROOT / "assets"
SRC_EXT = {".jpg", ".jpeg", ".png", ".heic"}
EDGES = (800, 1600)                 # longest edge, matching the -800/-1600 filename suffix
WEBP_Q, AVIF_Q = "82", "62"         # calibrated against the existing derivatives

# EXIF orientation -> the sips operations that put the image the right way up. sips applies
# them in argument order and rotates clockwise.
FIX = {
    1: [], 2: [("--flip", "horizontal")], 3: [("--rotate", "180")],
    4: [("--flip", "vertical")],
    5: [("--flip", "horizontal"), ("--rotate", "90")],
    6: [("--rotate", "90")],
    7: [("--flip", "horizontal"), ("--rotate", "270")],
    8: [("--rotate", "270")],
}
SWAPS_AXES = {5, 6, 7, 8}


def exif_orientation(path):
    """Read tag 0x0112 out of the embedded TIFF header. Works for JPEG and HEIC alike, and
    needs no third-party library — the alternative was guessing 90 vs 270 and shipping a
    third of the photographs upside down."""
    data = path.read_bytes()
    for magic in (b"II*\x00", b"MM\x00*"):
        i = data.find(magic)
        if i < 0:
            continue
        e = "<" if magic[:2] == b"II" else ">"
        try:
            off = struct.unpack_from(e + "I", data, i + 4)[0]
            for k in range(struct.unpack_from(e + "H", data, i + off)[0]):
                b = i + off + 2 + k * 12
                if struct.unpack_from(e + "HHI", data, b)[0] == 0x0112:
                    v = struct.unpack_from(e + "H", data, b + 8)[0]
                    return v if v in FIX else 1
        except struct.error:
            pass
    return 1


def webp_size(path):
    b = path.read_bytes()
    if b[:4] != b"RIFF" or b[8:12] != b"WEBP":
        return None
    c = b[12:16]
    if c == b"VP8X":
        return (int.from_bytes(b[24:27], "little") + 1, int.from_bytes(b[27:30], "little") + 1)
    if c == b"VP8 ":
        return (int.from_bytes(b[26:28], "little") & 0x3FFF, int.from_bytes(b[28:30], "little") & 0x3FFF)
    if c == b"VP8L":
        n = int.from_bytes(b[21:25], "little")
        return ((n & 0x3FFF) + 1, ((n >> 14) & 0x3FFF) + 1)
    return None


def sips_size(path):
    out = subprocess.run(["sips", "-g", "pixelWidth", "-g", "pixelHeight", str(path)],
                         capture_output=True, text=True).stdout
    w = re.search(r"pixelWidth:\s*(\d+)", out)
    h = re.search(r"pixelHeight:\s*(\d+)", out)
    return (int(w.group(1)), int(h.group(1))) if w and h else None


def slug_of(folder):   return folder.lower().replace(" ", "-")
def base_of(stem):     return stem.lower().replace("_", "-")


def sources():
    for f in sorted(MEDIA.rglob("*")):
        if f.is_file() and f.suffix.lower() in SRC_EXT and not f.name.startswith("."):
            yield f


def targets(src):
    slug, base = slug_of(src.parent.name), base_of(src.stem)
    return ASSETS / slug, base


def true_size(src):
    """Source dimensions as they should DISPLAY, with orientation applied."""
    wh = sips_size(src)
    if not wh:
        return None
    w, h = wh
    return (h, w) if exif_orientation(src) in SWAPS_AXES else (w, h)


def wrong(src):
    """Reasons this source's derivatives need rebuilding, or []."""
    d, base = targets(src)
    ts = true_size(src)
    if not ts:
        return ["unreadable source"]
    bad = []
    for edge in EDGES:
        for ext in ("webp", "avif"):
            if not (d / f"{base}-{edge}.{ext}").exists():
                bad.append(f"missing {base}-{edge}.{ext}")
        f = d / f"{base}-{edge}.webp"
        if f.exists():
            got = webp_size(f)
            if got and (got[0] > got[1]) != (ts[0] > ts[1]):
                bad.append(f"{base}-{edge}: {got[0]}x{got[1]} but source displays {ts[0]}x{ts[1]}")
    return bad


def convert(src, verbose=True):
    d, base = targets(src)
    d.mkdir(parents=True, exist_ok=True)
    orient = exif_orientation(src)
    with tempfile.TemporaryDirectory() as tmp:
        flat = pathlib.Path(tmp) / "flat.png"
        run(["sips", "-s", "format", "png", str(src), "--out", str(flat)])
        if FIX[orient]:
            run(["sips"] + [a for op in FIX[orient] for a in op] + [str(flat)])
        src_w, src_h = sips_size(flat)
        for edge in EDGES:
            sized = pathlib.Path(tmp) / f"{edge}.png"
            # Never upscale: a 900px original must not be published as a 1600px file.
            cap = min(edge, max(src_w, src_h))
            run(["sips", "-Z", str(cap), str(flat), "--out", str(sized)])
            run(["cwebp", "-quiet", "-q", WEBP_Q, str(sized), "-o", str(d / f"{base}-{edge}.webp")])
            run(["avifenc", "--speed", "6", "-q", AVIF_Q, str(sized), str(d / f"{base}-{edge}.avif")],
                quiet=True)
    if verbose:
        w, h = webp_size(d / f"{base}-1600.webp")
        note = f"  (rotated, EXIF {orient})" if orient != 1 else ""
        print(f"  {base}: {w}x{h}{note}")


def run(cmd, quiet=False):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        sys.exit(f"FAILED: {' '.join(cmd[:3])}…\n{r.stderr.strip()[:400]}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--check", action="store_true", help="report what is wrong, change nothing")
    g.add_argument("--fix", action="store_true", help="re-convert only the wrong or missing")
    g.add_argument("--all", action="store_true", help="rebuild every derivative")
    a = ap.parse_args()

    srcs = list(sources())
    if a.all:
        print(f"Rebuilding all {len(srcs)} sources…")
        for s in srcs:
            convert(s)
        return

    broken = [(s, r) for s in srcs if (r := wrong(s))]
    if not broken:
        print(f"All {len(srcs)} sources have correct derivatives.")
        return
    print(f"{len(broken)} of {len(srcs)} sources need rebuilding:")
    for s, reasons in broken:
        print(f"  {s.relative_to(MEDIA)}")
        for r in reasons:
            print(f"      {r}")
    if a.check:
        print("\nRun with --fix to rebuild these.")
        return
    print()
    for s, _ in broken:
        convert(s)
    print(f"\nRebuilt {len(broken)}. Re-run gen.py so the markup picks up the new dimensions.")


if __name__ == "__main__":
    main()
