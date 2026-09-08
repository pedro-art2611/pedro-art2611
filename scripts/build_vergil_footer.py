from __future__ import annotations

import math
import statistics
from collections import deque
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "assets" / "v2" / "vergil" / "source_raw"
OUT = ROOT / "assets" / "v2" / "vergil" / "rendered"
REPORT = ROOT / "assets" / "v2" / "vergil" / "BUILD_REPORT.md"
FLOOR_PATH = ROOT / "floor.jpg"

W, H = 1000, 230
CHAR_H = 148
FILES = {i: next(SRC.glob(f"{i:02d}-*.png")) for i in range(1, 11)}

GRID = {
    1: (6, 2),
    2: (6, 2),
    3: (8, 1),
    4: (6, 2),
    5: (6, 2),
    6: (4, 3),
    7: (6, 2),
    8: (6, 2),
    9: (6, 2),
    10: (6, 2),
}

CHARACTER_SOURCES = {1, 3, 4, 5, 7, 8, 9, 10}


def magenta_like(c: tuple[int, int, int]) -> bool:
    r, g, b = c
    return (
        r >= 105
        and b >= 110
        and g <= 150
        and g < min(r, b) * 0.78
        and abs(r - b) <= 125
    )


def strong_magenta(c: tuple[int, int, int]) -> bool:
    r, g, b = c
    return r >= 75 and b >= 82 and g <= 92 and (r + b) > g * 2.45 and abs(r - b) < 95


def gray_checker_like(c: tuple[int, int, int]) -> bool:
    r, g, b = c
    avg = (r + g + b) / 3
    return max(c) - min(c) <= 28 and 112 <= avg <= 245


def border_palette(rgb: Image.Image) -> list[tuple[int, int, int]]:
    w, h = rgb.size
    colors: list[tuple[int, int, int]] = []
    step_x = max(1, w // 24)
    step_y = max(1, h // 18)
    for x in range(0, w, step_x):
        colors.append(rgb.getpixel((x, 0)))
        colors.append(rgb.getpixel((x, h - 1)))
    for y in range(0, h, step_y):
        colors.append(rgb.getpixel((0, y)))
        colors.append(rgb.getpixel((w - 1, y)))
    return colors


def detect_bg_kind(im: Image.Image) -> str:
    rgb = im.convert("RGB")
    colors = border_palette(rgb)
    if sum(magenta_like(c) for c in colors) >= max(4, len(colors) // 4):
        return "magenta"
    if sum(gray_checker_like(c) for c in colors) >= max(4, len(colors) // 4):
        return "checker"
    return "unknown"


def color_distance(a: tuple[int, int, int], b: tuple[int, int, int]) -> float:
    return ((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2 + (a[2] - b[2]) ** 2) ** 0.5


def connected_background_mask(rgb: Image.Image, kind: str) -> list[list[bool]]:
    w, h = rgb.size
    seen = [[False] * w for _ in range(h)]
    q: deque[tuple[int, int]] = deque()
    border = border_palette(rgb)

    if kind == "magenta":
        refs = [c for c in border if magenta_like(c)]
        if not refs:
            refs = [(255, 0, 255)]

        def candidate(x: int, y: int) -> bool:
            c = rgb.getpixel((x, y))
            if not magenta_like(c):
                return False
            return min(color_distance(c, ref) for ref in refs[:: max(1, len(refs) // 12)]) <= 95

    elif kind == "checker":
        refs = [c for c in border if gray_checker_like(c)]
        if not refs:
            refs = [(170, 175, 180), (220, 225, 230)]

        def candidate(x: int, y: int) -> bool:
            c = rgb.getpixel((x, y))
            if not gray_checker_like(c):
                return False
            return min(color_distance(c, ref) for ref in refs[:: max(1, len(refs) // 16)]) <= 38

    else:
        return seen

    def seed(x: int, y: int) -> None:
        if not seen[y][x] and candidate(x, y):
            seen[y][x] = True
            q.append((x, y))

    for x in range(w):
        seed(x, 0)
        seed(x, h - 1)
    for y in range(h):
        seed(0, y)
        seed(w - 1, y)

    while q:
        x, y = q.popleft()
        for nx, ny in (
            (x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1),
            (x - 1, y - 1), (x + 1, y - 1), (x - 1, y + 1), (x + 1, y + 1),
        ):
            if 0 <= nx < w and 0 <= ny < h and not seen[ny][nx] and candidate(nx, ny):
                seen[ny][nx] = True
                q.append((nx, ny))
    return seen


def nearest_non_magenta(px, w: int, h: int, x: int, y: int, radius: int = 3):
    best = None
    best_d = 999
    for yy in range(max(0, y - radius), min(h, y + radius + 1)):
        for xx in range(max(0, x - radius), min(w, x + radius + 1)):
            r, g, b, a = px[xx, yy]
            if a == 0 or strong_magenta((r, g, b)):
                continue
            d = abs(xx - x) + abs(yy - y)
            if d < best_d:
                best = (r, g, b, 255)
                best_d = d
    return best


def decontaminate_magenta_edges(im: Image.Image) -> Image.Image:
    rgba = im.convert("RGBA")
    src = rgba.copy()
    sp = src.load()
    dp = rgba.load()
    w, h = rgba.size

    for y in range(h):
        for x in range(w):
            r, g, b, a = sp[x, y]
            if a == 0 or not strong_magenta((r, g, b)):
                continue
            touches_clear = False
            for yy in range(max(0, y - 2), min(h, y + 3)):
                for xx in range(max(0, x - 2), min(w, x + 3)):
                    if sp[xx, yy][3] == 0:
                        touches_clear = True
                        break
                if touches_clear:
                    break
            if touches_clear:
                replacement = nearest_non_magenta(sp, w, h, x, y, radius=4)
                if replacement:
                    dp[x, y] = replacement
                else:
                    dp[x, y] = (0, 0, 0, 0)
    return rgba


def remove_bottom_magenta_artifacts(im: Image.Image) -> Image.Image:
    rgba = im.convert("RGBA")
    px = rgba.load()
    w, h = rgba.size
    start = round(h * 0.84)
    for y in range(start, h):
        for x in range(w):
            r, g, b, a = px[x, y]
            if a and strong_magenta((r, g, b)):
                px[x, y] = (0, 0, 0, 0)
    return rgba


def remove_background_cell(im: Image.Image, character: bool = True) -> Image.Image:
    rgba = im.convert("RGBA")
    rgb = rgba.convert("RGB")
    kind = detect_bg_kind(im)
    mask = connected_background_mask(rgb, kind)
    px = rgba.load()
    w, h = rgba.size

    for y in range(h):
        for x in range(w):
            if mask[y][x]:
                px[x, y] = (0, 0, 0, 0)
            else:
                r, g, b, _ = px[x, y]
                px[x, y] = (r, g, b, 255)

    if character:
        rgba = remove_bottom_magenta_artifacts(rgba)
        rgba = decontaminate_magenta_edges(rgba)
    return rgba


def trim(im: Image.Image, pad: int = 2) -> Image.Image:
    box = im.getchannel("A").getbbox()
    if not box:
        return Image.new("RGBA", (1, 1), (0, 0, 0, 0))
    x0, y0, x1, y1 = box
    return im.crop((max(0, x0 - pad), max(0, y0 - pad), min(im.width, x1 + pad), min(im.height, y1 + pad)))


def split_sheet(source_id: int) -> list[Image.Image]:
    # V3: recorta a grade PRIMEIRO e só então remove o fundo de cada célula.
    raw = Image.open(FILES[source_id]).convert("RGBA")
    cols, rows = GRID[source_id]
    w, h = raw.size
    frames: list[Image.Image] = []
    for row in range(rows):
        y0 = round(row * h / rows)
        y1 = round((row + 1) * h / rows)
        for col in range(cols):
            x0 = round(col * w / cols)
            x1 = round((col + 1) * w / cols)
            cell = raw.crop((x0, y0, x1, y1))
            clean = remove_background_cell(cell, character=source_id in CHARACTER_SOURCES)
            frames.append(trim(clean, pad=2))
    return frames


def sequence_scale(frames: list[Image.Image], target_h: int = CHAR_H) -> float:
    heights: list[int] = []
    for fr in frames:
        box = fr.getchannel("A").getbbox()
        if box:
            heights.append(box[3] - box[1])
    if not heights:
        return 1.0
    med = statistics.median(heights)
    return target_h / max(1.0, med)


def scale_sequence(frames: list[Image.Image], target_h: int = CHAR_H) -> list[Image.Image]:
    # Um único fator por sequência. Nada de zoom involuntário frame a frame.
    s = sequence_scale(frames, target_h)
    out: list[Image.Image] = []
    for fr in frames:
        out.append(fr.resize((max(1, round(fr.width * s)), max(1, round(fr.height * s))), Image.Resampling.NEAREST))
    return out


def foot_anchor(im: Image.Image) -> tuple[float, float]:
    alpha = im.getchannel("A")
    box = alpha.getbbox()
    if not box:
        return im.width / 2, im.height
    x0, y0, x1, y1 = box
    width = x1 - x0
    # Exclui extremos horizontais para Yamato/casaco não puxarem o anchor.
    cx0 = round(x0 + width * 0.24)
    cx1 = round(x1 - width * 0.20)
    start_y = max(y0, y1 - max(8, round((y1 - y0) * 0.10)))
    xs: list[int] = []
    for y in range(start_y, y1):
        for x in range(max(x0, cx0), min(x1, cx1)):
            if alpha.getpixel((x, y)) >= 180:
                xs.append(x)
    if not xs:
        return (x0 + x1) / 2, y1 - 1
    xs.sort()
    return xs[len(xs) // 2], y1 - 1


def mirror_frames(frames: list[Image.Image]) -> list[Image.Image]:
    return [fr.transpose(Image.Transpose.FLIP_LEFT_RIGHT) for fr in frames]


def prepare_floor() -> tuple[Image.Image, int]:
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    if not FLOOR_PATH.exists():
        d = ImageDraw.Draw(layer)
        top = H - 48
        d.rectangle((0, top, W, H), fill=(14, 21, 31, 255))
        d.line((0, top, W, top), fill=(69, 94, 115, 255), width=2)
        return layer, top + 3

    raw = Image.open(FLOOR_PATH).convert("RGB")
    w, h = raw.size

    # O piso gerado tem chroma acima. Detecta a primeira faixa realmente ocupada por pedra.
    row_scores: list[float] = []
    for y in range(h):
        non_magenta = 0
        for x in range(0, w, max(1, w // 250)):
            c = raw.getpixel((x, y))
            if not magenta_like(c) and sum(c) < 620:
                non_magenta += 1
        samples = len(range(0, w, max(1, w // 250)))
        row_scores.append(non_magenta / max(1, samples))

    start = 0
    for y in range(max(0, h // 4), h):
        window = row_scores[y : min(h, y + 4)]
        if len(window) >= 3 and sum(v >= 0.34 for v in window) >= 3:
            start = max(0, y - 2)
            break

    crop = Image.open(FLOOR_PATH).convert("RGBA").crop((0, start, w, h))
    crop = remove_background_cell(crop, character=False)
    crop = trim(crop, pad=0)

    if crop.width <= 1 or crop.height <= 1:
        return layer, H - 46

    desired_h = min(82, max(54, round(crop.height * (W / crop.width))))
    crop = crop.resize((W, desired_h), Image.Resampling.NEAREST)
    y = H - crop.height
    layer.alpha_composite(crop, (0, y))
    return layer, y + 7


def paste_sprite(canvas: Image.Image, sprite: Image.Image, x: float, ground_y: int) -> None:
    ax, ay = foot_anchor(sprite)
    px = round(x - ax)
    py = round(ground_y - ay)
    canvas.alpha_composite(sprite, (px, py))


def fit_effect(fr: Image.Image, max_w: int, max_h: int) -> Image.Image:
    fr = trim(fr, pad=1)
    if fr.width <= 1 or fr.height <= 1:
        return Image.new("RGBA", (1, 1), (0, 0, 0, 0))
    s = min(max_w / fr.width, max_h / fr.height)
    return fr.resize((max(1, round(fr.width * s)), max(1, round(fr.height * s))), Image.Resampling.NEAREST)


def isolate_cyan(fr: Image.Image) -> Image.Image:
    src = fr.convert("RGBA")
    out = Image.new("RGBA", src.size, (0, 0, 0, 0))
    sp, dp = src.load(), out.load()
    for y in range(src.height):
        for x in range(src.width):
            r, g, b, a = sp[x, y]
            if a and b >= 120 and g >= 78 and b > r * 1.10 and g > r * 0.96:
                dp[x, y] = (r, g, b, 255)
    return out


def blue_cast_fx(canvas: Image.Image, x: int, y: int, phase: float) -> None:
    d = ImageDraw.Draw(canvas)
    intensity = math.sin(math.pi * max(0.0, min(1.0, phase)))
    if intensity < 0.08:
        return
    radius = round(8 + 20 * intensity)
    for k in range(5):
        ang = k * (math.pi * 2 / 5) + phase * 0.8
        p1 = (round(x + math.cos(ang) * 4), round(y + math.sin(ang) * 4))
        p2 = (round(x + math.cos(ang) * radius), round(y + math.sin(ang) * radius))
        d.line((p1, p2), fill=(70, 168, 255, 255), width=1)
    d.rectangle((x - 2, y - 2, x + 2, y + 2), fill=(205, 245, 255, 255))
    if intensity > 0.74:
        d.line((x - 9, y, x + 9, y), fill=(225, 252, 255, 255), width=2)
        d.line((x, y - 8, x, y + 8), fill=(118, 211, 255, 255), width=1)


def iai_trail(canvas: Image.Image, x: int, y: int, phase: float) -> None:
    d = ImageDraw.Draw(canvas)
    length = round(48 + phase * 112)
    d.line((x - length // 2, y + 11, x + length // 2, y - 9), fill=(202, 244, 255, 255), width=2)
    if phase > 0.34:
        d.line((x - length // 2 + 7, y + 16, x + length // 2 - 13, y - 3), fill=(69, 163, 255, 255), width=1)


def floor_reflection(canvas: Image.Image, x: int, ground_y: int, strength: float) -> None:
    if strength <= 0:
        return
    d = ImageDraw.Draw(canvas)
    span = round(22 + 58 * strength)
    y = min(H - 5, ground_y + 10)
    d.line((x - span, y, x + span, y), fill=(42, 107, 157, 255), width=1)


def binary_alpha(im: Image.Image) -> Image.Image:
    rgba = im.convert("RGBA")
    px = rgba.load()
    for y in range(rgba.height):
        for x in range(rgba.width):
            r, g, b, a = px[x, y]
            if a < 128:
                px[x, y] = (0, 0, 0, 0)
            else:
                px[x, y] = (r, g, b, 255)
    return rgba


def append_scene(frames, durations, floor_layer, ground_y, sprites, xs, ds, fx=None) -> None:
    for idx, (sprite, x, duration) in enumerate(zip(sprites, xs, ds)):
        canvas = floor_layer.copy()
        paste_sprite(canvas, sprite, x, ground_y)
        if fx:
            fx(canvas, idx, len(sprites), x, ground_y)
        frames.append(binary_alpha(canvas))
        durations.append(duration)


def linear_positions(a: float, b: float, n: int) -> list[float]:
    if n <= 1:
        return [a]
    return [a + (b - a) * i / (n - 1) for i in range(n)]


def gif_safe_frame(im: Image.Image) -> Image.Image:
    # Reserva explicitamente palette index 0 para transparência.
    rgba = binary_alpha(im)
    alpha = rgba.getchannel("A")
    rgb = Image.new("RGB", rgba.size, (8, 12, 20))
    rgb.paste(rgba.convert("RGB"), mask=alpha)
    q = rgb.quantize(colors=255, method=Image.Quantize.FASTOCTREE, dither=Image.Dither.NONE)
    src_palette = q.getpalette()[: 255 * 3]
    palette = [0, 0, 0] + src_palette
    palette += [0] * (768 - len(palette))

    out = Image.new("P", rgba.size, 0)
    out.putpalette(palette[:768])
    qdata = list(q.getdata())
    adata = list(alpha.getdata())
    out.putdata([0 if a < 128 else min(255, idx + 1) for idx, a in zip(qdata, adata)])
    out.info["transparency"] = 0
    out.info["disposal"] = 2
    return out


def render() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    floor_layer, ground_y = prepare_floor()

    # Recorta/limpa e normaliza cada sequência com UM fator fixo por sheet.
    walk_right = scale_sequence(split_sheet(9))
    idle = scale_sequence(split_sheet(3))
    turn_full = scale_sequence(split_sheet(1))
    iai = scale_sequence(split_sheet(10))
    hair = scale_sequence(split_sheet(7))
    cast = scale_sequence(split_sheet(8))
    judgment = split_sheet(6)

    walk_left = mirror_frames(walk_right)
    idle_left = mirror_frames(idle)

    # V3 abraça uma virada low-frame-rate deliberada: cinco poses fortes, sem frames ruins.
    turn_indices = [0, 3, 5, 8, 11]
    turn_right_to_left = [turn_full[i] for i in turn_indices if i < len(turn_full)]
    turn_left_to_right = list(reversed(turn_right_to_left))

    neutral_r = idle[0] if idle else walk_right[0]
    neutral_l = idle_left[0] if idle_left else walk_left[0]

    frames: list[Image.Image] = []
    durations: list[int] = []

    idle_seq = (idle * 2)[:12]
    append_scene(frames, durations, floor_layer, ground_y, idle_seq, [120] * len(idle_seq), [210] * len(idle_seq))

    wr = (walk_right * 3)[:36]
    append_scene(frames, durations, floor_layer, ground_y, wr, linear_positions(120, 665, len(wr)), [125] * len(wr))

    iai_ds = [270, 230, 195, 160, 115, 80, 62, 72, 110, 155, 205, 380][: len(iai)]

    def iai_fx(canvas, idx, n, x, gy):
        if 4 <= idx <= 8:
            phase = (idx - 3) / 5
            iai_trail(canvas, round(x + 66), gy - 84, phase)
            floor_reflection(canvas, round(x + 34), gy, max(0, 1 - abs(phase - 0.7)))

    append_scene(frames, durations, floor_layer, ground_y, iai, [665] * len(iai), iai_ds, iai_fx)

    one_hand_indices = [0, 1, 2, 3, 4, 5, 9, 10, 11]
    hair_one = [hair[i] for i in one_hand_indices if i < len(hair)]
    hair_one_ds = [250, 220, 195, 175, 185, 215, 245, 260, 430][: len(hair_one)]
    append_scene(frames, durations, floor_layer, ground_y, hair_one, [665] * len(hair_one), hair_one_ds)

    wr_short = walk_right[:12]
    append_scene(frames, durations, floor_layer, ground_y, wr_short, linear_positions(665, 835, len(wr_short)), [128] * len(wr_short))

    turn_ds = [260, 220, 235, 220, 330][: len(turn_right_to_left)]
    append_scene(frames, durations, floor_layer, ground_y, turn_right_to_left, [835] * len(turn_right_to_left), turn_ds)

    wl = (walk_left * 3)[:36]
    append_scene(frames, durations, floor_layer, ground_y, wl, linear_positions(835, 265, len(wl)), [125] * len(wl))

    il = (idle_left * 1)[:8]
    append_scene(frames, durations, floor_layer, ground_y, il, [265] * len(il), [210] * len(il))
    append_scene(frames, durations, floor_layer, ground_y, turn_left_to_right, [265] * len(turn_left_to_right), list(reversed(turn_ds)))

    wr_mid = (walk_right * 2)[:18]
    append_scene(frames, durations, floor_layer, ground_y, wr_mid, linear_positions(265, 445, len(wr_mid)), [125] * len(wr_mid))

    cast_seq = cast[:6] + [neutral_r]
    cast_ds = [290, 245, 205, 170, 140, 120, 340][: len(cast_seq)]

    def cast_fx(canvas, idx, n, x, gy):
        phase = idx / max(1, n - 1)
        blue_cast_fx(canvas, round(x + 20), gy - 94, phase)
        floor_reflection(canvas, round(x + 16), gy, math.sin(math.pi * phase) * 0.65)

    append_scene(frames, durations, floor_layer, ground_y, cast_seq, [445] * len(cast_seq), cast_ds, cast_fx)

    j_ds = [150, 125, 110, 105, 110, 125, 145, 175, 210, 250, 310, 430][: len(judgment)]
    for idx, (jfr, dur) in enumerate(zip(judgment, j_ds)):
        canvas = floor_layer.copy()
        paste_sprite(canvas, neutral_r, 445, ground_y)
        fx = fit_effect(isolate_cyan(jfr), 300, 132)
        if fx.width > 1 and fx.height > 1:
            fx_x = min(W - fx.width - 32, 615)
            fx_y = max(16, ground_y - fx.height - 20)
            canvas.alpha_composite(fx, (fx_x, fx_y))
            strength = math.sin(math.pi * idx / max(1, len(judgment) - 1))
            floor_reflection(canvas, fx_x + fx.width // 2, ground_y, strength)
        frames.append(binary_alpha(canvas))
        durations.append(dur)

    hair_two_ds = [245, 220, 195, 185, 190, 205, 220, 235, 250, 260, 280, 450][: len(hair)]
    append_scene(frames, durations, floor_layer, ground_y, hair, [445] * len(hair), hair_two_ds)

    wr_end = (walk_right * 2)[:24]
    append_scene(frames, durations, floor_layer, ground_y, wr_end, linear_positions(445, 835, len(wr_end)), [125] * len(wr_end))
    append_scene(frames, durations, floor_layer, ground_y, turn_right_to_left, [835] * len(turn_right_to_left), turn_ds)

    wl_end = (walk_left * 3)[:36]
    append_scene(frames, durations, floor_layer, ground_y, wl_end, linear_positions(835, 120, len(wl_end)), [123] * len(wl_end))
    append_scene(frames, durations, floor_layer, ground_y, turn_left_to_right, [120] * len(turn_left_to_right), list(reversed(turn_ds)))
    append_scene(frames, durations, floor_layer, ground_y, [neutral_r, neutral_r], [120, 120], [300, 380])

    # QA RGBA: APNG preserva alpha verdadeiro, útil para separar defeitos de composição dos de GIF.
    apng_path = OUT / "vergil-footer-v3.png"
    frames[0].save(
        apng_path,
        save_all=True,
        append_images=frames[1:],
        duration=durations,
        loop=0,
        disposal=0,
        blend=0,
    )

    # GIF final de QA com índice 0 reservado exclusivamente para transparência.
    gif_frames = [gif_safe_frame(fr) for fr in frames]
    gif_path = OUT / "vergil-footer-draft.gif"
    gif_frames[0].save(
        gif_path,
        save_all=True,
        append_images=gif_frames[1:],
        duration=durations,
        loop=0,
        disposal=2,
        optimize=False,
        transparency=0,
    )

    report = [
        "# Build report — Vergil footer V3",
        "",
        f"Frames finais: **{len(frames)}**",
        f"Duração aproximada: **{sum(durations) / 1000:.1f}s**",
        f"Canvas: **{W}×{H}**",
        f"Piso autoral: **{'sim' if FLOOR_PATH.exists() else 'não'}**",
        "",
        "## Correções estruturais V3",
        "",
        "- cada célula da sprite sheet é recortada antes da remoção de fundo;",
        "- remoção de chroma é adaptativa à paleta da borda de cada célula;",
        "- resíduos magenta próximos ao contorno são substituídos por cor vizinha, não por transparência;",
        "- manchas magenta no solo dos próprios sprites são descartadas;",
        "- cada sequência usa um único fator de escala calculado pela mediana de altura; não existe zoom frame-a-frame;",
        "- anchor horizontal usa a região central dos pés, reduzindo drift causado por Yamato/casaco;",
        "- virada reduzida para 5 poses fortes, em linguagem low-frame-rate deliberada;",
        "- GIF reserva o índice 0 exclusivamente para transparência; preto/azul escuro do Vergil não pode mais virar transparente;",
        "- APNG RGBA de QA gerado em rendered/vergil-footer-v3.png;",
        "- piso autoral é detectado pela região ocupada por pedra, sem carregar o chroma superior inteiro.",
        "",
        "## Direção",
        "",
        "Se a V3 ainda apresentar deformações grandes nas poses, o gargalo restante será a inconsistência artística entre sprites. Nesse ponto faz mais sentido refazer o personagem em uma linguagem 8/16-bit mais simples e canônica do que continuar compensando os sheets atuais por código.",
    ]
    REPORT.write_text("\n".join(report) + "\n", encoding="utf-8")
    print(gif_path, gif_path.stat().st_size, "bytes")
    print(apng_path, apng_path.stat().st_size, "bytes")
    print("duration_ms", sum(durations))


if __name__ == "__main__":
    render()
