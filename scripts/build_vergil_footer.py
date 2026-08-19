from __future__ import annotations

import math
from collections import deque
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "assets" / "v2" / "vergil" / "source_raw"
OUT = ROOT / "assets" / "v2" / "vergil" / "rendered"
REPORT = ROOT / "assets" / "v2" / "vergil" / "BUILD_REPORT.md"

W, H = 920, 210
GROUND_Y = 186
CHAR_H = 148

FILES = {i: next(SRC.glob(f"{i:02d}-*.png")) for i in range(1, 11)}


def is_magenta(c):
    r, g, b = c
    # Gemini varia bastante o chroma. Preferimos um corte duro: pixel-art não
    # precisa de borda antialias e isso evita halo roxo no GIF.
    return r >= 165 and b >= 160 and g <= 130 and abs(r - b) <= 105


def is_gray_bg(c):
    r, g, b = c
    return max(c) - min(c) <= 34 and 105 <= (r + g + b) / 3 <= 248


def bg_kind(im: Image.Image) -> str:
    rgb = im.convert("RGB")
    w, h = rgb.size
    corners = [rgb.getpixel(p) for p in ((0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1))]
    if sum(is_magenta(c) for c in corners) >= 2:
        return "magenta"
    if sum(is_gray_bg(c) for c in corners) >= 2:
        return "checker"
    return "unknown"


def sanitize_transparency(rgba: Image.Image) -> Image.Image:
    px = rgba.load()
    for y in range(rgba.height):
        for x in range(rgba.width):
            r, g, b, a = px[x, y]
            if a < 20:
                px[x, y] = (0, 0, 0, 0)
            elif a < 255:
                # Sem alpha parcial em pixel-art: evita contaminação da paleta GIF.
                px[x, y] = (r, g, b, 255)
    return rgba


def remove_bg(im: Image.Image) -> Image.Image:
    rgba = im.convert("RGBA")
    rgb = rgba.convert("RGB")
    w, h = rgb.size
    kind = bg_kind(im)
    px = rgba.load()

    if kind == "magenta":
        for y in range(h):
            for x in range(w):
                r, g, b, a = px[x, y]
                if is_magenta((r, g, b)):
                    px[x, y] = (0, 0, 0, 0)
        return sanitize_transparency(rgba)

    if kind == "checker":
        # Remove apenas o checker conectado às bordas; cabelo/metal cinza interno fica.
        q = deque()
        seen = [[False] * w for _ in range(h)]

        def cand(x, y):
            return is_gray_bg(rgb.getpixel((x, y)))

        for x in range(w):
            for y in (0, h - 1):
                if cand(x, y) and not seen[y][x]:
                    seen[y][x] = True
                    q.append((x, y))
        for y in range(h):
            for x in (0, w - 1):
                if cand(x, y) and not seen[y][x]:
                    seen[y][x] = True
                    q.append((x, y))

        while q:
            x, y = q.popleft()
            for nx, ny in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)):
                if 0 <= nx < w and 0 <= ny < h and not seen[ny][nx] and cand(nx, ny):
                    seen[ny][nx] = True
                    q.append((nx, ny))

        for y in range(h):
            for x in range(w):
                if seen[y][x]:
                    px[x, y] = (0, 0, 0, 0)
        return sanitize_transparency(rgba)

    return sanitize_transparency(rgba)


def split_grid(im: Image.Image, cols: int, rows: int) -> list[Image.Image]:
    w, h = im.size
    frames = []
    for r in range(rows):
        y0 = round(r * h / rows)
        y1 = round((r + 1) * h / rows)
        for c in range(cols):
            x0 = round(c * w / cols)
            x1 = round((c + 1) * w / cols)
            cell = im.crop((x0, y0, x1, y1))
            box = cell.getbbox()
            if box:
                cell = cell.crop(box)
            frames.append(cell)
    return frames


def split_sheet(source_id: int) -> list[Image.Image]:
    im = remove_bg(Image.open(FILES[source_id]))
    # O Judgment Cut (06) foi gerado pelo Gemini em 4x3, apesar do prompt pedir 6x2.
    # O grid antigo 6x2 literalmente cortava os círculos no meio.
    if source_id == 6:
        return split_grid(im, 4, 3)
    if im.height <= 160:
        # Sheet horizontal; não é usado como idle na V1.
        return split_grid(im, 8, 1)
    return split_grid(im, 6, 2)


def scale_sprite(fr: Image.Image, target_h=CHAR_H) -> Image.Image:
    if fr.height <= 0:
        return fr
    s = target_h / fr.height
    nw = max(1, round(fr.width * s))
    nh = max(1, round(fr.height * s))
    return fr.resize((nw, nh), Image.Resampling.NEAREST)


def flip_sprite(fr: Image.Image) -> Image.Image:
    return fr.transpose(Image.Transpose.FLIP_LEFT_RIGHT)


def isolate_cyan(fr: Image.Image) -> Image.Image:
    rgba = fr.convert("RGBA")
    out = Image.new("RGBA", rgba.size, (0, 0, 0, 0))
    src = rgba.load()
    dst = out.load()
    for y in range(rgba.height):
        for x in range(rgba.width):
            r, g, b, a = src[x, y]
            if a > 20 and b >= 120 and g >= 85 and b > r * 1.14 and g > r * 1.03:
                dst[x, y] = (r, g, b, 255)
    return out


def draw_floor(base: Image.Image):
    # Piso provisório; será substituído pelo asset autoral quando estiver disponível.
    d = ImageDraw.Draw(base)
    y = GROUND_Y
    d.rectangle((0, y, W, H), fill=(8, 12, 20, 255))
    widths = [92, 118, 84, 126, 97, 112, 79, 121, 104]
    x = -18
    for i, ww in enumerate(widths * 2):
        if x > W:
            break
        top = y + (i % 3 - 1) * 2
        col = (21 + (i % 3) * 4, 30 + (i % 4) * 3, 44 + (i % 2) * 5, 255)
        d.rectangle((x, top, x + ww, H - 2), fill=col)
        d.line((x + ww, top, x + ww - 7, H - 2), fill=(5, 9, 16, 255), width=2)
        if i % 2 == 0:
            cx = x + ww // 2
            d.line((cx, top + 5, cx - 8, top + 11, cx - 3, top + 18), fill=(44, 65, 84, 255), width=1)
        x += ww - 3
    d.line((0, y, W, y), fill=(61, 84, 105, 255), width=1)


def base_frame() -> Image.Image:
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw_floor(im)
    return im


def put_sprite(canvas: Image.Image, fr: Image.Image, x: float, target_h=CHAR_H, y_offset=0):
    s = scale_sprite(fr, target_h)
    px = round(x - s.width / 2)
    py = GROUND_Y - s.height + y_offset
    canvas.alpha_composite(s, (px, py))


def blue_cast_fx(canvas: Image.Image, x: int, y: int, phase: float):
    d = ImageDraw.Draw(canvas)
    intensity = math.sin(math.pi * max(0, min(1, phase)))
    if intensity <= 0.04:
        return
    core = (210, 245, 255, 255)
    mid = (76, 176, 255, 255)
    radius = round(7 + 22 * intensity)
    d.rectangle((x - 2, y - 2, x + 2, y + 2), fill=core)
    for k in range(6):
        ang = (k * math.pi / 3) + phase * 0.55
        length = round(radius * (0.72 + 0.09 * k))
        x2 = round(x + math.cos(ang) * length)
        y2 = round(y + math.sin(ang) * length)
        d.line((x, y, x2, y2), fill=mid, width=1)
    if intensity > 0.68:
        d.rectangle((x - 6, y - 1, x + 6, y + 1), fill=(226, 252, 255, 255))
        d.rectangle((x - 1, y - 6, x + 1, y + 6), fill=(132, 220, 255, 255))


def slash_fx(canvas: Image.Image, x: int, y: int, phase: float):
    d = ImageDraw.Draw(canvas)
    length = round(45 + 115 * phase)
    d.line((x - length // 2, y + 12, x + length // 2, y - 8), fill=(202, 241, 255, 255), width=2)
    if phase > 0.30:
        d.line((x - length // 2 + 5, y + 16, x + length // 2 - 9, y - 2), fill=(78, 177, 255, 255), width=1)


def add(frames, durations, sprite_frames, x_positions, ds, *, target_h=CHAR_H, fx=None, y_offsets=None):
    if y_offsets is None:
        y_offsets = [0] * len(sprite_frames)
    for idx, (sf, x, dur, yo) in enumerate(zip(sprite_frames, x_positions, ds, y_offsets)):
        c = base_frame()
        put_sprite(c, sf, x, target_h, yo)
        if fx:
            fx(c, idx, len(sprite_frames), x)
        frames.append(c)
        durations.append(dur)


def render():
    OUT.mkdir(parents=True, exist_ok=True)
    seq = {i: split_sheet(i) for i in range(1, 11)}

    # Mapeamento manual validado a partir das gerações da conversa.
    walk_right = seq[9]
    turn_right_to_left = seq[1]
    iai = seq[10]
    hair = seq[7]
    cast_raw = seq[8]
    judgment_fx = seq[6]

    neutral = walk_right[0]
    walk_left = [flip_sprite(fr) for fr in walk_right]
    # Reverter a virada mantém a transição física contínua no sentido oposto.
    turn_left_to_right = list(reversed(turn_right_to_left))

    # Hair sheet: Gemini acabou entregando duas leituras em fileiras diferentes.
    hair_one = hair[:6]
    hair_two = hair[6:12] if len(hair) >= 12 else hair[max(0, len(hair) // 2):]

    # Judgment cast: a segunda fileira contém poses de costas que causavam o
    # "teleporte" visual. Mantemos a primeira fileira + retorno neutral.
    cast = cast_raw[:6]
    if cast_raw:
        cast = cast + [cast_raw[-1]]

    frames = []
    durations = []

    # 1) Idle inicial bem legível — mesma pose, micro respiração procedural.
    idle = [neutral] * 8
    add(
        frames, durations, idle,
        [120] * 8,
        [280, 220, 220, 220, 220, 220, 220, 420],
        y_offsets=[0, -1, -1, 0, 1, 1, 0, 0],
    )

    # 2) Caminhada direita: ~5 s para atravessar boa parte do rodapé.
    wr = (walk_right * 3)[:22]
    xs = [120 + i * (500 / (len(wr) - 1)) for i in range(len(wr))]
    add(frames, durations, wr, xs, [145] * len(wr))

    # 3) Pausa antes do Iai.
    add(frames, durations, [neutral] * 3, [620] * 3, [320, 260, 360])

    # 4) Iai: preparação perceptível, golpe rápido, recuperação lenta.
    def iaifx(c, idx, n, x):
        if 4 <= idx <= 8:
            phase = min(1.0, max(0.0, (idx - 3) / 5))
            slash_fx(c, round(x + 78), GROUND_Y - 86, phase)

    iai_ds_full = [220, 190, 160, 130, 82, 58, 48, 58, 88, 135, 190, 360]
    iai_ds = iai_ds_full[:len(iai)] + [180] * max(0, len(iai) - len(iai_ds_full))
    add(frames, durations, iai, [620] * len(iai), iai_ds, fx=iaifx)

    # 5) Cabelo com UMA mão — bem mais lento, para o gesto realmente aparecer.
    if hair_one:
        one_ds = [220, 210, 200, 210, 240, 420][:len(hair_one)]
        add(frames, durations, hair_one, [620] * len(hair_one), one_ds)

    # 6) Caminha até a borda direita.
    wr2 = walk_right[:8]
    xs = [620 + i * (175 / max(1, len(wr2) - 1)) for i in range(len(wr2))]
    add(frames, durations, wr2, xs, [150] * len(wr2))

    # 7) Virada real direita -> esquerda, sem trocar de posição.
    add(frames, durations, turn_right_to_left, [795] * len(turn_right_to_left), [155] * len(turn_right_to_left))
    add(frames, durations, [walk_left[0]] * 2, [795, 795], [300, 260])

    # 8) Caminhada esquerda suave usando o mesmo ciclo espelhado.
    wl = (walk_left * 3)[:24]
    xs = [795 - i * (535 / (len(wl) - 1)) for i in range(len(wl))]
    add(frames, durations, wl, xs, [150] * len(wl))

    # 9) Virada esquerda -> direita usando a mesma animação ao contrário.
    add(frames, durations, turn_left_to_right, [260] * len(turn_left_to_right), [155] * len(turn_left_to_right))
    add(frames, durations, [neutral] * 3, [260] * 3, [320, 280, 420])

    # 10) Judgment Cut cast corporal com concentração azul local.
    def castfx(c, idx, n, x):
        # pico ocorre perto do penúltimo frame, não no meio do gesto inteiro
        phase = idx / max(1, n - 1)
        shaped = min(1.0, phase * 1.35)
        blue_cast_fx(c, round(x + 31), GROUND_Y - 95, shaped)

    cast_ds = [240, 210, 180, 150, 120, 170, 420][:len(cast)]
    add(frames, durations, cast, [260] * len(cast), cast_ds, fx=castfx)

    # 11) Judgment Cut espacial. O source 06 agora é recortado corretamente em 4x3.
    # Vergil fica imóvel e o FX tem área generosa à frente dele.
    jfx_ds = [180, 150, 135, 125, 120, 130, 145, 170, 200, 240, 300, 420]
    for idx, vfx in enumerate(judgment_fx[:12]):
        c = base_frame()
        put_sprite(c, neutral, 260)
        vf = isolate_cyan(vfx)
        if vf.getbbox():
            # Mantém o efeito inteiro dentro da tela; escala menor que a V0.
            vf = scale_sprite(vf, 105)
            x = 430
            y = max(12, GROUND_Y - vf.height - 34)
            if x + vf.width > W - 18:
                x = W - 18 - vf.width
            c.alpha_composite(vf, (x, y))
        frames.append(c)
        durations.append(jfx_ds[idx] if idx < len(jfx_ds) else 180)

    # 12) Pequena pausa após o corte antes do cabelo.
    add(frames, durations, [neutral] * 2, [260, 260], [340, 300])

    # 13) Cabelo com DUAS mãos — segunda variação e ainda mais deliberada.
    if hair_two:
        two_ds = [230] * len(hair_two)
        if two_ds:
            two_ds[-1] = 480
        add(frames, durations, hair_two, [260] * len(hair_two), two_ds)

    # 14) Caminha para a direita, vira e volta ao ponto inicial para fechar o loop
    # sem teleporte de posição nem sprite andando para trás.
    wr3 = (walk_right * 2)[:16]
    xs = [260 + i * (440 / (len(wr3) - 1)) for i in range(len(wr3))]
    add(frames, durations, wr3, xs, [150] * len(wr3))

    add(frames, durations, turn_right_to_left, [700] * len(turn_right_to_left), [155] * len(turn_right_to_left))

    wl2 = (walk_left * 2)[:18]
    xs = [700 - i * (580 / (len(wl2) - 1)) for i in range(len(wl2))]
    add(frames, durations, wl2, xs, [150] * len(wl2))

    # Últimos frames equivalem ao começo (x=120, neutral visual), evitando salto no loop.
    end_neutral = walk_left[0] if walk_left else neutral
    add(frames, durations, [end_neutral] * 3, [120] * 3, [300, 260, 360])

    gif = OUT / "vergil-footer-draft.gif"
    # Todos os pixels transparentes foram zerados para impedir halo magenta/roxo.
    frames[0].save(
        gif,
        save_all=True,
        append_images=frames[1:],
        duration=durations,
        loop=0,
        disposal=2,
        optimize=True,
        transparency=0,
    )

    lines = [
        "# Build report — Vergil footer V1",
        "",
        f"Frames finais: **{len(frames)}**",
        f"Duração aproximada: **{sum(durations) / 1000:.1f}s**",
        f"Canvas: **{W}×{H}**",
        "",
        "## Correções desta versão",
        "",
        "- removido movimento de sprite right-facing para a esquerda; walk-left é um ciclo espelhado estável;",
        "- removidas poses traseiras do Judgment Cut cast;",
        "- chroma magenta agora é alpha binário sem borda semi-transparente;",
        "- pixels transparentes têm RGB zerado para evitar halo roxo no GIF;",
        "- Judgment Cut source 06 recortado em grid 4×3, evitando cortes no VFX;",
        "- timings aumentados em caminhada, cabelo, viradas e Judgment Cut;",
        "- loop fecha retornando fisicamente ao ponto inicial, sem teleporte horizontal.",
        "",
        "## Mapeamento manual",
        "",
        "- walk-right: 09",
        "- turn: 01",
        "- iai: 10",
        "- hair: 07",
        "- judgment cast: 08 (somente primeira fileira + neutral final)",
        "- judgment FX: 06 (4×3)",
        "",
        "## Pendente",
        "",
        "O piso continua procedural até o asset autoral de pedra ser disponibilizado separadamente.",
    ]
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(gif, gif.stat().st_size, "bytes", "duration", sum(durations) / 1000)


if __name__ == "__main__":
    render()
