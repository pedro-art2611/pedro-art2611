from __future__ import annotations

import hashlib
import re
import shutil
import zipfile
from collections import Counter
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


def analyze(path: Path) -> dict:
    with Image.open(path) as im:
        im.seek(0)
        rgba = im.convert("RGBA")
        w, h = rgba.size
        pixels = list(rgba.getdata())
        total = max(1, len(pixels))
        alpha_pixels = sum(1 for r, g, b, a in pixels if a < 255)
        magenta = sum(1 for r, g, b, a in pixels if r >= 245 and g <= 15 and b >= 245)

        sample = []
        step = max(1, int((total / 6000) ** 0.5))
        for y in range(0, h, step):
            for x in range(0, w, step):
                sample.append(rgba.getpixel((x, y))[:3])
        common = Counter(sample).most_common(6)

        corner_pts = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]
        corners = [rgba.getpixel(p)[:3] for p in corner_pts]

        checker_candidates = 0
        grayish = []
        for color, count in common:
            r, g, b = color
            if max(color) - min(color) <= 8 and 130 <= r <= 235:
                grayish.append((color, count))
        if len(grayish) >= 2:
            checker_candidates = sum(c for _, c in grayish[:3])

        return {
            "size": f"{w}x{h}",
            "mode": im.mode,
            "frames": getattr(im, "n_frames", 1),
            "alpha": alpha_pixels / total,
            "magenta": magenta / total,
            "checker": checker_candidates / max(1, len(sample)),
            "corners": corners,
            "common": common,
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
        "| # | Origem no ZIP | Extraído como | Dimensões | Frames | Alpha | Magenta | Checker provável | SHA1 |",
        "|---:|---|---|---:|---:|---:|---:|---:|---|",
    ]

    for i, original, out_name, size_bytes, digest, info in rows:
        lines.append(
            f"| {i} | `{original}` | [`{out_name}`](./source_raw/{out_name}) | {info['size']} | {info['frames']} | {pct(info['alpha'])} | {pct(info['magenta'])} | {pct(info['checker'])} | `{digest}` |"
        )

    lines += ["", "## Diagnóstico de fundo", ""]
    for i, original, out_name, size_bytes, digest, info in rows:
        common = ", ".join(f"rgb{c}:{n}" for c, n in info["common"][:4])
        lines.append(f"- **{i:02d} `{out_name}`** — cantos: `{info['corners']}`; cores amostradas dominantes: {common}")

    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Inventário criado em {REPORT.relative_to(ROOT)} com {len(rows)} imagens.")


if __name__ == "__main__":
    main()
