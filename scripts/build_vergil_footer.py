from __future__ import annotations

import math
from collections import deque
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "assets" / "v2" / "vergil" / "source_raw"
OUT = ROOT / "assets" / "v2" / "vergil" / "rendered"
REPORT = ROOT / "assets" / "v2" / "vergil" / "BUILD_REPORT.md"
FLOOR_PATH = ROOT / "floor.jpg"

W, H = 1000, 235
CHAR_H = 150
FILES = {i: next(SRC.glob(f"{i:02d}-*.png")) for i in range(1, 11)}

GRID = {
    1: (6, 2),
    2: (6, 2),
    3: (8, 1),
    4: (6, 2),
    5: (6, 2),
    6: (4, 3),  # Judgment Cut real: Gemini gerou 4x3
    7: (6, 2),
    8: (6, 2),
    9: (6, 2),
    10: (6, 2),
}


def magenta_like(c: tuple[int, int, int]) -> bool:
    r, g, b = c
    # Amplo o suficiente para JPEG/variação do Gemini, mas usado APENAS em fundo
    # conectado à borda, nunca globalmente no personagem.
    return (
        r >= 120
        and b >= 120
        and g <= 150
        and g < min(r, b) * 0.74
        and abs(r - b) <= 115
    )


def gray_checker_like(c: tuple[int, int, int]) -> bool:
    r, g, b = c
    avg = (r + g + b) / 3
    return max(c) - min(c) <= 32 and 108 <= avg <= 248


def detect_bg_kind(im: Image.Image) -> str:
    rgb = im.convert("RGB")
    w, h = rgb.size
    pts = [
        (0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1),
        (w // 2, 0), (w // 2, h - 1), (0, h // 2), (w - 1, h // 2),
    ]
    colors = [rgb.getpixel(p) for p in pts]
    if sum(magenta_like(c) for c in colors) >= 3:
        return "magenta"
    if sum(gray_checker_like(c) for c in colors) >= 3:
        return "checker"
    return "unknown"


def connected_background_mask(rgb: Image.Image, kind: str) -> list[list[bool]]:
    w, h = rgb.size
    seen = [[False] * w for _ in range(h)]
    q: deque[tuple[int, int]] = deque()

    if kind == "magenta":
        candidate = lambda x, y: magenta_like(rgb.getpixel((x, y)))
    elif kind == "checker":
        candidate = lambda x, y: gray_checker_like(rgb.getpixel((x, y)))
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
        for nx, ny in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)):
            if 0 <= nx < w and 0 <= ny < h and not seen[ny][nx] and candidate(nx, ny):
                seen[ny][nx] = True
                q.append((nx, ny))
    return seen


def remove_background(im: Image.Image) -> Image.Image:
    rgba = im.convert("RGBA")
    rgb = rgba.convert("RGB")
    kind = detect_bg_kind(im)
    mask = connected_background_mask(rgb, kind)
    w, h = rgba.size
    px = rgba.load()

    # Fundo: alpha 0 e RGB zerado. Isso evita o magenta reaparecer na quantização GIF.
    for y in range(h):
        for x in range(w):
            if mask[y][x]:
                px[x, y] = (0, 0, 0, 0)
            else:
                r, g, b, a = px[x, y]
                px[x, y] = (r, g, b, 255)

    # Chroma-spill: só corrige pixels opacos imediatamente adjacentes ao fundo removido.
    # Não apaga nada; apenas reduz vermelho de uma borda magenta para um azul/cinza frio.
    original = rgba.copy()
    op = original.load()
    for y in range(1, h - 1):
        for x in range(1, w - 1):
            r, g, b, a = op[x, y]
            if a == 0:
                continue
            touches_transparent = any(
                op[nx, ny][3] == 0
                for nx, ny in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1))
            )
            if not touches_transparent:
                continue
            if r > 75 and b > 85 and g < min(r, b) * 0.68 and abs(r - b) < 105:
                r2 = min(r, max(g + 20, int(b * 0.48)))
                b2 = max(b, g + 18)
                px[x, y] = (r2, g, b2, 255)
    return rgba


def trim(im: Image.Image, pad: int = 2) -> Image.Image:
    box = im.getchannel("A").getbbox()
    if not box:
        return Image.new("RGBA", (1, 1), (0, 0, 0, 0))
    x0, y0, x1, y1 = box
    return im.crop((max(0, x0 - pad), max(0, y0 - pad), min(im.width, x1 + pad), min(im.height, y1 + pad)))


def split_sheet(source_id: int) -> list[Image.Image]:
    im = remove_background(Image.open(FILES[source_id]))
    cols, rows = GRID[source_id]
    w, h = im.size
    frames: list[Image.Image] = []
    for row in range(rows):
        y0 = round(row * h / rows)
        y1 = round((row + 1) * h / rows)
        for col in range(cols):
            x0 = round(col * w / cols)
            x1 = round((col + 1) * w / cols)
            frames.append(trim(im.crop((x0, y0, x1, y1))))
    return frames


def foot_anchor(im: Image.Image) -> tuple[float, float]:
    alpha = im.getchannel("A")
    box = alpha.getbbox()
    if not box:
        return im.width / 2, im.height
    x0, y0, x1, y1 = box
    # pixels nos ~9 px inferiores: normalmente as botas, não Yamato/casaco.
    start_y = max(y0, y1 - max(6, round((y1 - y0) * 0.07)))
    xs: list[int] = []
    for y in range(start_y, y1):
        for x in range(x0, x1):
            if alpha.getpixel((x, y)) >= 200:
                xs.append(x)
    if not xs:
        return (x0 + x1) / 2, y1 - 1
    xs.sort()
    return xs[len(xs) // 2], y1 - 1


def scale_with_anchor(im: Image.Image, target_h: int = CHAR_H) -> tuple[Image.Image, float, float]:
    box = im.getchannel("A").getbbox()
    if not box:
        return im, im.width / 2, im.height
    bbox_h = max(1, box[3] - box[1])
    scale = target_h / bbox_h
    nw = max(1, round(im.width * scale))
    nh = max(1, round(im.height * scale))
    ax, ay = foot_anchor(im)
    out = im.resize((nw, nh), Image.Resampling.NEAREST)
    return out, ax * scale, ay * scale


def mirror_frames(frames: list[Image.Image]) -> list[Image.Image]:
    return [fr.transpose(Image.Transpose.FLIP_LEFT_RIGHT) for fr in frames]


def load_floor() -> tuple[Image.Image, int]:
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    if not FLOOR_PATH.exists():
        d = ImageDraw.Draw(layer)
        top = H - 42
        d.rectangle((0, top, W, H), fill=(15, 22, 33, 255))
        d.line((0, top, W, top), fill=(74, 96, 118, 255), width=2)
        return layer, top + 3

    floor = trim(remove_background(Image.open(FLOOR_PATH)), pad=0)
    if floor.width <= 1 or floor.height <= 1:
        return layer, H - 40
    scale = W / floor.width
    floor = floor.resize((W, max(1, round(floor.height * scale))), Image.Resampling.NEAREST)
    if floor.height > 92:
        # O asset tem espaço acima do piso; depois do trim ainda limitamos para não engolir a cena.
        ratio = 92 / floor.height
        floor = floor.resize((round(floor.width * ratio), 92), Image.Resampling.NEAREST)
        if floor.width < W:
            floor = floor.resize((W, floor.height), Image.Resampling.NEAREST)
    y = H - floor.height
    layer.alpha_composite(floor, (0, y))
    return layer, y + 4


def paste_sprite(canvas: Image.Image, fr: Image.Image, x: float, ground_y: int, target_h: int = CHAR_H) -> None:
    sprite, ax, ay = scale_with_anchor(fr, target_h)
    px = round(x - ax)
    py = round(ground_y - ay)
    canvas.alpha_composite(sprite, (px, py))


def fit_effect(fr: Image.Image, max_w: int, max_h: int) -> Image.Image:
    box = fr.getchannel("A").getbbox()
    if not box:
        return Image.new("RGBA", (1, 1), (0, 0, 0, 0))
    fr = trim(fr)
    s = min(max_w / fr.width, max_h / fr.height)
    return fr.resize((max(1, round(fr.width * s)), max(1, round(fr.height * s))), Image.Resampling.NEAREST)


def isolate_cyan(fr: Image.Image) -> Image.Image:
    src = fr.convert("RGBA")
    out = Image.new("RGBA", src.size, (0, 0, 0, 0))
    sp, dp = src.load(), out.load()
    for y in range(src.height):
        for x in range(src.width):
            r, g, b, a = sp[x, y]
            if a and b >= 125 and g >= 85 and b > r * 1.14 and g > r * 1.02:
                dp[x, y] = (r, g, b, 255)
    return out


def blue_cast_fx(canvas: Image.Image, x: int, y: int, phase: float) -> None:
    d = ImageDraw.Draw(canvas)
    intensity = math.sin(math.pi * max(0.0, min(1.0, phase)))
    if intensity < 0.08:
        return
    radius = round(8 + 22 * intensity)
    for k in range(5):
        ang = k * (math.pi * 2 / 5) + phase * 0.8
        inner = 4
        outer = round(radius * (0.72 + 0.08 * k))
        p1 = (round(x + math.cos(ang) * inner), round(y + math.sin(ang) * inner))
        p2 = (round(x + math.cos(ang) * outer), round(y + math.sin(ang) * outer))
        d.line((p1, p2), fill=(70, 168, 255, 255), width=1)
    d.rectangle((x - 2, y - 2, x + 2, y + 2), fill=(205, 245, 255, 255))
    if intensity > 0.74:
        d.line((x - 9, y, x + 9, y), fill=(225, 252, 255, 255), width=2)
        d.line((x, y - 8, x, y + 8), fill=(118, 211, 255, 255), width=1)


def iai_trail(canvas: Image.Image, x: int, y: int, phase: float) -> None:
    d = ImageDraw.Draw(canvas)
    length = round(58 + phase * 125)
    d.line((x - length // 2, y + 13, x + length // 2, y - 10), fill=(202, 244, 255, 255), width=2)
    if phase > 0.30:
        d.line((x - length // 2 + 7, y + 18, x + length // 2 - 13, y - 3), fill=(69, 163, 255, 255), width=1)


def floor_reflection(canvas: Image.Image, x: int, ground_y: int, strength: float) -> None:
    if strength <= 0:
        return
    d = ImageDraw.Draw(canvas)
    span = round(35 + 75 * strength)
    y = ground_y + 7
    d.line((x - span, y, x + span, y), fill=(45, 118, 170, 255), width=1)
    if strength > 0.65:
        d.line((x - span // 2, y + 4, x + span // 2, y + 4), fill=(85, 158, 202, 255), width=1)


def binary_alpha(im: Image.Image) -> Image.Image:
    rgba = im.convert("RGBA")
    px = rgba.load()
    for y in range(rgba.height):
        for x in range(rgba.width):
            r, g, b, a = px[x, y]
            if a < 96:
                px[x, y] = (0, 0, 0, 0)
            else:
                px[x, y] = (r, g, b, 255)
    return rgba


def append_scene(
    frames: list[Image.Image],
    durations: list[int],
    floor_layer: Image.Image,
    ground_y: int,
    sprites: list[Image.Image],
    xs: list[float],
    ds: list[int],
    fx=None,
) -> None:
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


def render() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    floor_layer, ground_y = load_floor()

    # Mapeamento manual validado pela V1/conversa. Sem classificador automático nesta fase.
    walk_right = split_sheet(9)
    idle = split_sheet(3)
    turn_full = split_sheet(1)
    iai = split_sheet(10)
    hair = split_sheet(7)
    cast = split_sheet(8)
    judgment = split_sheet(6)

    # Caminhada esquerda suave: espelha a caminhada mais estável. A prioridade da V2 é fluidez;
    # a fidelidade de orientação da Yamato pode ser refinada depois com recorte manual dedicado.
    walk_left = mirror_frames(walk_right)
    idle_left = mirror_frames(idle)

    # Virada curta: elimina poses redundantes e estabiliza timing. A volta usa exatamente a
    # mesma sequência ao contrário para evitar duas animações incompatíveis.
    turn_indices = [0, 1, 2, 4, 7, 9, 10, 11]
    turn_right_to_left = [turn_full[i] for i in turn_indices if i < len(turn_full)]
    turn_left_to_right = list(reversed(turn_right_to_left))

    neutral_r = idle[0] if idle else walk_right[0]
    neutral_l = idle_left[0] if idle_left else walk_left[0]

    frames: list[Image.Image] = []
    durations: list[int] = []

    # 1. Idle inicial: presença constante, sem congelar.
    idle_seq = (idle * 2)[:12]
    append_scene(frames, durations, floor_layer, ground_y, idle_seq, [120] * len(idle_seq), [180] * len(idle_seq))

    # 2. Caminha para a direita em 3 ciclos completos.
    wr = (walk_right * 3)[:36]
    append_scene(frames, durations, floor_layer, ground_y, wr, linear_positions(120, 675, len(wr)), [108] * len(wr))

    # 3. Iai: preparação legível, golpe rápido, recuperação lenta.
    iai_ds = [240, 210, 180, 145, 105, 78, 62, 72, 105, 145, 190, 320][: len(iai)]
    def iai_fx(canvas, idx, n, x, gy):
        if 4 <= idx <= 8:
            phase = (idx - 3) / 5
            iai_trail(canvas, round(x + 70), gy - 86, phase)
            floor_reflection(canvas, round(x + 38), gy, max(0, 1 - abs(phase - 0.7)))
    append_scene(frames, durations, floor_layer, ground_y, iai, [675] * len(iai), iai_ds, iai_fx)

    # 4. Cabelo - leitura de uma mão. Pausas maiores para o gesto ser reconhecível.
    one_hand_indices = [0, 1, 2, 3, 4, 5, 9, 10, 11]
    hair_one = [hair[i] for i in one_hand_indices if i < len(hair)]
    hair_one_ds = [220, 190, 170, 155, 165, 190, 210, 230, 360][: len(hair_one)]
    append_scene(frames, durations, floor_layer, ground_y, hair_one, [675] * len(hair_one), hair_one_ds)

    # 5. Anda até a borda direita e vira.
    wr_short = walk_right[:12]
    append_scene(frames, durations, floor_layer, ground_y, wr_short, linear_positions(675, 845, len(wr_short)), [112] * len(wr_short))
    turn_ds = [230, 190, 175, 170, 175, 190, 215, 300][: len(turn_right_to_left)]
    append_scene(frames, durations, floor_layer, ground_y, turn_right_to_left, [845] * len(turn_right_to_left), turn_ds)

    # 6. Caminha para a esquerda de forma contínua, sem usar frames traseiros como walk cycle.
    wl = (walk_left * 3)[:36]
    append_scene(frames, durations, floor_layer, ground_y, wl, linear_positions(845, 255, len(wl)), [110] * len(wl))

    # 7. Idle voltado para a esquerda + mesma virada em reverso.
    il = (idle_left * 1)[:8]
    append_scene(frames, durations, floor_layer, ground_y, il, [255] * len(il), [190] * len(il))
    append_scene(frames, durations, floor_layer, ground_y, turn_left_to_right, [255] * len(turn_left_to_right), list(reversed(turn_ds)))

    # 8. Caminha até o centro para Judgment Cut.
    wr_mid = (walk_right * 2)[:18]
    append_scene(frames, durations, floor_layer, ground_y, wr_mid, linear_positions(255, 455, len(wr_mid)), [108] * len(wr_mid))

    # 9. Judgment Cast: somente primeira fileira + neutral; nada de costas.
    cast_seq = cast[:6] + [neutral_r]
    cast_ds = [260, 220, 190, 155, 120, 105, 280][: len(cast_seq)]
    def cast_fx(canvas, idx, n, x, gy):
        phase = idx / max(1, n - 1)
        blue_cast_fx(canvas, round(x + 22), gy - 95, phase)
        floor_reflection(canvas, round(x + 18), gy, math.sin(math.pi * phase) * 0.7)
    append_scene(frames, durations, floor_layer, ground_y, cast_seq, [455] * len(cast_seq), cast_ds, cast_fx)

    # 10. Judgment Cut: efeito completo, 4x3, fit por largura+altura e bastante margem.
    j_ds = [120, 105, 95, 90, 100, 115, 135, 160, 190, 230, 280, 380][: len(judgment)]
    for idx, (jfr, dur) in enumerate(zip(judgment, j_ds)):
        canvas = floor_layer.copy()
        paste_sprite(canvas, neutral_r, 455, ground_y)
        fx = fit_effect(isolate_cyan(jfr), 335, 145)
        if fx.width > 1 and fx.height > 1:
            fx_x = min(W - fx.width - 28, 610)
            fx_y = max(14, ground_y - fx.height - 17)
            canvas.alpha_composite(fx, (fx_x, fx_y))
            strength = math.sin(math.pi * idx / max(1, len(judgment) - 1))
            floor_reflection(canvas, fx_x + fx.width // 2, ground_y, strength)
        frames.append(binary_alpha(canvas))
        durations.append(dur)

    # 11. Cabelo - versão mais longa/duas mãos após o Judgment Cut.
    hair_two = hair[:]
    hair_two_ds = [210, 185, 170, 160, 165, 175, 190, 205, 220, 225, 240, 390][: len(hair_two)]
    append_scene(frames, durations, floor_layer, ground_y, hair_two, [455] * len(hair_two), hair_two_ds)

    # 12. Caminha à direita, vira, volta ao ponto inicial e vira de novo: loop sem teleporte.
    wr_end = (walk_right * 2)[:24]
    append_scene(frames, durations, floor_layer, ground_y, wr_end, linear_positions(455, 845, len(wr_end)), [110] * len(wr_end))
    append_scene(frames, durations, floor_layer, ground_y, turn_right_to_left, [845] * len(turn_right_to_left), turn_ds)
    wl_end = (walk_left * 3)[:36]
    append_scene(frames, durations, floor_layer, ground_y, wl_end, linear_positions(845, 120, len(wl_end)), [108] * len(wl_end))
    append_scene(frames, durations, floor_layer, ground_y, turn_left_to_right, [120] * len(turn_left_to_right), list(reversed(turn_ds)))

    # Fecha com o mesmo neutral do primeiro trecho, evitando salto visual do último para o primeiro.
    append_scene(frames, durations, floor_layer, ground_y, [neutral_r, neutral_r], [120, 120], [260, 320])

    gif_path = OUT / "vergil-footer-draft.gif"
    frames[0].save(
        gif_path,
        save_all=True,
        append_images=frames[1:],
        duration=durations,
        loop=0,
        disposal=2,
        optimize=False,
        transparency=0,
    )

    report = [
        "# Build report — Vergil footer V2",
        "",
        f"Frames finais: **{len(frames)}**",
        f"Duração aproximada: **{sum(durations) / 1000:.1f}s**",
        f"Canvas: **{W}×{H}**",
        f"Piso autoral: **{'sim' if FLOOR_PATH.exists() else 'não'}**",
        "",
        "## Correções estruturais",
        "",
        "- chroma removido apenas quando conectado à borda; detalhes internos do Vergil não são mais apagados por cor;",
        "- chroma-spill corrigido somente na borda externa, sem reduzir alpha do personagem;",
        "- todos os pixels transparentes têm RGB zerado e alpha final é binário para evitar silhueta roxa no GIF;",
        "- sprites ancorados pela região dos pés em vez do centro do recorte;",
        "- turn reduzido a 8 poses e reutilizado em reverso para manter consistência;",
        "- walk-left usa ciclo de caminhada espelhado estável, não poses de virada;",
        "- timings ampliados em ações, cabelo e viradas;",
        "- Judgment Cut usa grid 4×3 e fit simultâneo de largura/altura;",
        "- piso autoral floor.jpg integrado à renderização;",
        "- loop fecha fisicamente no ponto inicial, sem teleporte.",
        "",
        "## Observação",
        "",
        "A V2 prioriza preservação do personagem e fluidez. Se a virada ainda não convencer visualmente, o próximo passo será substituir a rotação por uma transição autoral curta construída a partir de poses selecionadas, em vez de insistir na sheet do Gemini.",
    ]
    REPORT.write_text("\n".join(report) + "\n", encoding="utf-8")
    print(gif_path, gif_path.stat().st_size, "bytes", "duration_ms", sum(durations))


if __name__ == "__main__":
    render()
