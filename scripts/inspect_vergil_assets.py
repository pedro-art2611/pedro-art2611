from __future__ import annotations

import hashlib
import math
import re
import shutil
import zipfile
from collections import Counter, deque
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
ZIP_PATH = ROOT / "vergil-assets.zip"
OUT = ROOT / "assets" / "v2" / "vergil"
RAW = OUT / "source_raw"
REPORT = OUT / "INVENTORY.md"

IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".webp", ".gif", ".bmp"}


def safe_name(name: str, index: int) -> str:
    base = Path(name).name
    stem = re.sub(r"[^A-Za-z0-9._-]+", "-", Path(base).stem).strip("-._") or f"asset-{index:02d}"
    ext = Path(base).suffix.lower() or ".bin"
    return f"{index:02d}-{stem}{ext}"


def pct(v: float) -> str:
    return f"{v * 100:.1f}%"


def is_magenta(c: tuple[int, int, int]) -> bool:
    r, g, b = c
    return r >= 180 and b >= 175 and g <= 105 and abs(r - b) <= 75


def is_gray_bg(c: tuple[int, int, int]) -> bool:
    r, g, b = c
    return max(c) - min(c) <= 28 and 115 <= (r + g + b) / 3 <= 245


def flood_background(rgb: Image.Image, bg_kind: str) -> list[list[bool]]:
    w, h = rgb.size
    bg = [[False] * w for _ in range(h)]
    q: deque[tuple[int, int]] = deque()

    def candidate(x: int, y: int) -> bool:
        c = rgb.getpixel((x, y))
        if bg_kind == "magenta":
            return is_magenta(c)
        if bg_kind == "checker":
            return is_gray_bg(c)
        return False

    for x in range(w):
        for y in (0, h - 1):
            if candidate(x, y) and not bg[y][x]:
                bg[y][x] = True
                q.append((x, y))
    for y in range(h):
        for x in (0, w - 1):
            if candidate(x, y) and not bg[y][x]:
                bg[y][x] = True
                q.append((x, y))

    while q:
        x, y = q.popleft()
        for nx, ny in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)):
            if 0 <= nx < w and 0 <= ny < h and not bg[ny][nx] and candidate(nx, ny):
                bg[ny][nx] = True
                q.append((nx, ny))
    return bg


def analyze(path: Path) -> dict:
    with Image.open(path) as im:
        im.seek(0)
        rgba = im.convert("RGBA")
        rgb = rgba.convert("RGB")
        w, h = rgba.size
        pixels = list(rgba.getdata())
        total = max(1, len(pixels))
        alpha_pixels = sum(1 for r, g, b, a in pixels if a < 255)
        magenta_exact = sum(1 for r, g, b, a in pixels if r >= 245 and g <= 15 and b >= 245)

        sample = []
        step = max(1, int((total / 6000) ** 0.5))
        for y in range(0, h, step):
            for x in range(0, w, step):
                sample.append(rgb.getpixel((x, y)))
        common = Counter(sample).most_common(8)

        corner_pts = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]
        corners = [rgb.getpixel(p) for p in corner_pts]
        magenta_corners = sum(is_magenta(c) for c in corners)
        gray_corners = sum(is_gray_bg(c) for c in corners)
        if magenta_corners >= 2:
            bg_kind = "magenta"
        elif gray_corners >= 2:
            bg_kind = "checker"
        else:
            bg_kind = "unknown"

        checker_candidates = 0
        grayish = []
        for color, count in common:
            if is_gray_bg(color):
                grayish.append((color, count))
        if len(grayish) >= 2:
            checker_candidates = sum(c for _, c in grayish[:4])

        if bg_kind in {"magenta", "checker"}:
            bg = flood_background(rgb, bg_kind)
            fg_coords = []
            dark = cyan = bright = 0
            for y in range(h):
                for x in range(w):
                    if bg[y][x]:
                        continue
                    r, g, b = rgb.getpixel((x, y))
                    fg_coords.append((x, y))
                    mean = (r + g + b) / 3
                    if mean < 95:
                        dark += 1
                    if b >= 145 and g >= 105 and b > r * 1.25 and g > r * 1.15:
                        cyan += 1
                    if mean > 185:
                        bright += 1
        else:
            fg_coords = [(x, y) for y in range(h) for x in range(w)]
            dark = cyan = bright = 0

        fg_n = max(1, len(fg_coords))
        if fg_coords:
            xs = [p[0] for p in fg_coords]
            ys = [p[1] for p in fg_coords]
            x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
            bbox = (x0, y0, x1 + 1, y1 + 1)
            bbox_w = (x1 - x0 + 1) / w
            bbox_h = (y1 - y0 + 1) / h
        else:
            bbox = None
            bbox_w = bbox_h = 0.0

        fg_ratio = len(fg_coords) / total if bg_kind in {"magenta", "checker"} else 1.0
        dark_ratio = dark / fg_n
        cyan_ratio = cyan / fg_n
        bright_ratio = bright / fg_n

        if bg_kind == "unknown":
            candidate = "unknown/background-rich"
        elif bbox_w >= 0.88 and bbox_h <= 0.42 and dark_ratio >= 0.25:
            candidate = "environment/floor"
        elif cyan_ratio >= 0.16 and dark_ratio <= 0.28:
            candidate = "vfx-only"
        elif cyan_ratio >= 0.035 and dark_ratio >= 0.28:
            candidate = "character+vfx"
        elif dark_ratio >= 0.30:
            candidate = "character-sheet"
        else:
            candidate = "other"

        return {
            "size": f"{w}x{h}",
            "mode": im.mode,
            "frames": getattr(im, "n_frames", 1),
            "alpha": alpha_pixels / total,
            "magenta": magenta_exact / total,
            "checker": checker_candidates / max(1, len(sample)),
            "corners": corners,
            "common": common,
            "bg_kind": bg_kind,
            "candidate": candidate,
            "bbox": bbox,
            "bbox_w": bbox_w,
            "bbox_h": bbox_h,
            "fg_ratio": fg_ratio,
            "dark_ratio": dark_ratio,
            "cyan_ratio": cyan_ratio,
            "bright_ratio": bright_ratio,
        }


def main() -> None:
    if not ZIP_PATH.exists():
        raise SystemExit(f"Arquivo não encontrado: {ZIP_PATH}")

    if RAW.exists():
        shutil.rmtree(RAW)
    RAW.mkdir(parents=True, exist_ok=True)

    rows = []
    with zipfile.ZipFile(ZIP_PATH) as zf:
        members = [m for m in zf.infolist() if not m.is_dir()]
        img_members = [m for m in members if Path(m.filename).suffix.lower() in IMAGE_EXTS]
        for i, member in enumerate(img_members, 1):
            out_name = safe_name(member.filename, i)
            out_path = RAW / out_name
            with zf.open(member) as src, out_path.open("wb") as dst:
                shutil.copyfileobj(src, dst)
            digest = hashlib.sha1(out_path.read_bytes()).hexdigest()[:10]
            info = analyze(out_path)
            rows.append((i, member.filename, out_name, out_path.stat().st_size, digest, info))

    lines = [
        "# Inventário dos assets do Vergil",
        "",
        f"Total de imagens encontradas no ZIP: **{len(rows)}**.",
        "",
        "Este relatório é gerado automaticamente para orientar o recorte e a montagem frame a frame.",
        "",
        "| # | Origem no ZIP | Dimensões | Fundo | Candidato | Foreground | Dark | Cyan | BBox |",
        "|---:|---|---:|---|---|---:|---:|---:|---|",
    ]

    for i, original, out_name, size_bytes, digest, info in rows:
        lines.append(
            f"| {i} | [`{out_name}`](./source_raw/{out_name}) | {info['size']} | {info['bg_kind']} | **{info['candidate']}** | {pct(info['fg_ratio'])} | {pct(info['dark_ratio'])} | {pct(info['cyan_ratio'])} | `{info['bbox']}` |"
        )

    lines += [
        "",
        "## Fundo e integridade",
        "",
        "| # | Alpha real | Magenta exato | Checker provável | SHA1 |",
        "|---:|---:|---:|---:|---|",
    ]
    for i, original, out_name, size_bytes, digest, info in rows:
        lines.append(
            f"| {i} | {pct(info['alpha'])} | {pct(info['magenta'])} | {pct(info['checker'])} | `{digest}` |"
        )

    lines += ["", "## Diagnóstico de fundo", ""]
    for i, original, out_name, size_bytes, digest, info in rows:
        common = ", ".join(f"rgb{c}:{n}" for c, n in info["common"][:4])
        lines.append(
            f"- **{i:02d} `{out_name}`** — tipo `{info['bg_kind']}`; candidato `{info['candidate']}`; bbox `{info['bbox']}`; bbox relativo `{pct(info['bbox_w'])} × {pct(info['bbox_h'])}`; bright `{pct(info['bright_ratio'])}`; cantos `{info['corners']}`; dominantes: {common}"
        )

    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Inventário criado em {REPORT.relative_to(ROOT)} com {len(rows)} imagens.")


if __name__ == "__main__":
    main()
