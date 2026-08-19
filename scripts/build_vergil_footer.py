from __future__ import annotations

import math
from pathlib import Path
from collections import deque

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "assets" / "v2" / "vergil" / "source_raw"
OUT = ROOT / "assets" / "v2" / "vergil" / "rendered"
REPORT = ROOT / "assets" / "v2" / "vergil" / "BUILD_REPORT.md"

W, H = 920, 190
GROUND_Y = 168
CHAR_H = 142

FILES = {i: next(SRC.glob(f"{i:02d}-*.png")) for i in range(1, 11)}


def is_magenta(c):
    r, g, b = c
    return r >= 175 and b >= 170 and g <= 115 and abs(r - b) <= 82


def is_gray_bg(c):
    r, g, b = c
    return max(c) - min(c) <= 30 and 112 <= (r + g + b) / 3 <= 247


def bg_kind(im: Image.Image) -> str:
    rgb = im.convert("RGB")
    w, h = rgb.size
    corners = [rgb.getpixel(p) for p in ((0,0),(w-1,0),(0,h-1),(w-1,h-1))]
    if sum(is_magenta(c) for c in corners) >= 2:
        return "magenta"
    if sum(is_gray_bg(c) for c in corners) >= 2:
        return "checker"
    return "unknown"


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
                # Gemini gera vários tons próximos do chroma; limiar amplo é seguro
                # para o Vergil, cuja paleta é azul/preto/cinza.
                if is_magenta((r, g, b)):
                    px[x, y] = (r, g, b, 0)
                elif r > 145 and b > 145 and g < 135 and abs(r-b) < 95:
                    strength = max(0, min(255, int((135-g) * 2.2)))
                    if strength > 80:
                        px[x, y] = (r, g, b, max(0, 255-strength))
        return rgba

    if kind == "checker":
        # Flood fill só pelo fundo conectado às bordas para não apagar cabelo/metal cinza.
        q = deque()
        seen = [[False] * w for _ in range(h)]
        def cand(x,y):
            return is_gray_bg(rgb.getpixel((x,y)))
        for x in range(w):
            for y in (0,h-1):
                if cand(x,y) and not seen[y][x]: seen[y][x]=True; q.append((x,y))
        for y in range(h):
            for x in (0,w-1):
                if cand(x,y) and not seen[y][x]: seen[y][x]=True; q.append((x,y))
        while q:
            x,y=q.popleft()
            for nx,ny in ((x-1,y),(x+1,y),(x,y-1),(x,y+1)):
                if 0<=nx<w and 0<=ny<h and not seen[ny][nx] and cand(nx,ny):
                    seen[ny][nx]=True; q.append((nx,ny))
        for y in range(h):
            for x in range(w):
                if seen[y][x]:
                    r,g,b,a=px[x,y]; px[x,y]=(r,g,b,0)
        return rgba

    return rgba


def split_sheet(source_id: int) -> list[Image.Image]:
    im = remove_bg(Image.open(FILES[source_id]))
    w,h=im.size
    if h <= 160:
        cols,rows=8,1
    else:
        cols,rows=6,2
    frames=[]
    for r in range(rows):
        y0=round(r*h/rows); y1=round((r+1)*h/rows)
        for c in range(cols):
            x0=round(c*w/cols); x1=round((c+1)*w/cols)
            cell=im.crop((x0,y0,x1,y1))
            box=cell.getbbox()
            if box:
                cell=cell.crop(box)
            frames.append(cell)
    return frames


def stats(frames: list[Image.Image]) -> dict:
    upper=[]; mid=[]; widths=[]; cyan=[]
    for fr in frames:
        rgba=fr.convert("RGBA")
        w,h=rgba.size
        if not w or not h: continue
        alpha=rgba.getchannel("A")
        bbox=alpha.getbbox()
        if not bbox: continue
        widths.append((bbox[2]-bbox[0])/max(1,h))
        p=rgba.load()
        counts=[0,0,0]; cyan_n=fg=0
        for y in range(h):
            region=0 if y < h*0.38 else (1 if y < h*0.72 else 2)
            for x in range(w):
                r,g,b,a=p[x,y]
                if a<40: continue
                counts[region]+=1; fg+=1
                if b>140 and g>105 and b>r*1.25: cyan_n+=1
        upper.append(counts[0]/max(1,fg)); mid.append(counts[1]/max(1,fg)); cyan.append(cyan_n/max(1,fg))
    def var(vals):
        if not vals: return 0
        m=sum(vals)/len(vals); return sum((x-m)**2 for x in vals)/len(vals)
    return {
        "upper_var":var(upper), "mid_var":var(mid), "width_var":var(widths),
        "cyan_max":max(cyan or [0]), "upper_max":max(upper or [0]), "mid_max":max(mid or [0])
    }


def scale_sprite(fr: Image.Image, target_h=CHAR_H) -> Image.Image:
    if fr.height <= 0: return fr
    s=target_h/fr.height
    nw=max(1,round(fr.width*s)); nh=max(1,round(fr.height*s))
    return fr.resize((nw,nh),Image.Resampling.NEAREST)


def isolate_cyan(fr: Image.Image) -> Image.Image:
    rgba=fr.convert("RGBA")
    out=Image.new("RGBA",rgba.size,(0,0,0,0)); src=rgba.load(); dst=out.load()
    for y in range(rgba.height):
        for x in range(rgba.width):
            r,g,b,a=src[x,y]
            if a>20 and b>=125 and g>=90 and b>r*1.18 and g>r*1.08:
                dst[x,y]=(r,g,b,min(255,a))
    return out


def draw_floor(base: Image.Image):
    # Placeholder técnico até o piso autoral entrar no pacote.
    d=ImageDraw.Draw(base)
    y=GROUND_Y
    d.rectangle((0,y, W,H), fill=(9,13,22,255))
    # pedras irregulares discretas, sem moldura
    widths=[92,118,84,126,97,112,79,121,104]
    x=-18
    for i,ww in enumerate(widths*2):
        if x>W: break
        top=y + (i%3-1)*2
        col=(22+(i%3)*4,31+(i%4)*3,45+(i%2)*5,255)
        d.rectangle((x,top,x+ww,H-2),fill=col)
        d.line((x+ww,top,x+ww-7,H-2),fill=(6,10,17,255),width=2)
        if i%2==0:
            cx=x+ww//2
            d.line((cx,top+5,cx-8,top+11,cx-3,top+18),fill=(47,68,87,255),width=1)
        x+=ww-3
    d.line((0,y,W,y), fill=(67,91,112,255), width=1)


def base_frame() -> Image.Image:
    im=Image.new("RGBA",(W,H),(0,0,0,0)); draw_floor(im); return im


def put_sprite(canvas: Image.Image, fr: Image.Image, x: float, target_h=CHAR_H, y_offset=0):
    s=scale_sprite(fr,target_h)
    px=round(x-s.width/2); py=GROUND_Y-s.height+y_offset
    canvas.alpha_composite(s,(px,py))


def blue_cast_fx(canvas: Image.Image, x: int, y: int, phase: float):
    d=ImageDraw.Draw(canvas)
    intensity=math.sin(math.pi*max(0,min(1,phase)))
    if intensity<=0.05:return
    core=(185,235,255,220)
    mid=(70,165,255,190)
    radius=round(8+16*intensity)
    d.rectangle((x-2,y-2,x+2,y+2),fill=core)
    for k in range(4):
        ang=(k*math.pi/2)+phase*0.7
        length=round(radius*(0.7+0.25*k))
        x2=round(x+math.cos(ang)*length); y2=round(y+math.sin(ang)*length)
        d.line((x,y,x2,y2),fill=mid,width=1)
    if intensity>0.72:
        d.rectangle((x-5,y-1,x+5,y+1),fill=(220,250,255,235))
        d.rectangle((x-1,y-5,x+1,y+5),fill=(130,215,255,220))


def slash_fx(canvas: Image.Image, x: int, y: int, phase: float):
    d=ImageDraw.Draw(canvas)
    length=round(42+90*phase)
    d.line((x-length//2,y+10,x+length//2,y-8),fill=(187,235,255,230),width=2)
    if phase>0.35:
        d.line((x-length//2+5,y+14,x+length//2-9,y-3),fill=(72,166,255,170),width=1)


def add(frames, durations, sprite_frames, x_positions, ds, *, target_h=CHAR_H, fx=None):
    for idx,(sf,x,dur) in enumerate(zip(sprite_frames,x_positions,ds)):
        c=base_frame(); put_sprite(c,sf,x,target_h)
        if fx: fx(c,idx,len(sprite_frames),x)
        frames.append(c); durations.append(dur)


def pick_sequences():
    seq={i:split_sheet(i) for i in range(1,11)}
    metrics={i:stats(seq[i]) for i in range(1,11) if i != 6}
    # Confirmados/fortes pelo inventário e histórico das gerações.
    walk_right=9
    compact_idle=3
    turn_a=1
    judgment_fx=6
    aura_source=2
    # Iai tende a ser o sheet de personagem com mais pixels ciano residuais.
    iai=max((i for i in metrics if i not in {2,3,9}), key=lambda i:metrics[i]["cyan_max"])
    # Hair-fix: mãos sobem à cabeça => maior variação de massa no terço superior.
    pool=[i for i in metrics if i not in {1,2,3,6,9,iai}]
    hair=max(pool,key=lambda i:metrics[i]["upper_var"])
    pool=[i for i in pool if i!=hair]
    # Cast: maior variação no tronco/mãos sem ser hair/iai.
    cast=max(pool,key=lambda i:metrics[i]["mid_var"])
    pool=[i for i in pool if i!=cast]
    turn_b=max(pool,key=lambda i:metrics[i]["width_var"]) if pool else 4
    remaining=[i for i in pool if i!=turn_b]
    extra=remaining[0] if remaining else 7
    return seq,metrics,{"walk_right":walk_right,"compact_idle":compact_idle,"turn_a":turn_a,"turn_b":turn_b,"iai":iai,"hair":hair,"cast":cast,"judgment_fx":judgment_fx,"aura":aura_source,"extra":extra}


def render():
    OUT.mkdir(parents=True,exist_ok=True)
    seq,metrics,pick=pick_sequences()
    frames=[]; durations=[]

    neutral=seq[pick["walk_right"]][0]
    idle_src=seq[pick["compact_idle"]]
    walk=seq[pick["walk_right"]]
    turn_a=seq[pick["turn_a"]]
    turn_b=seq[pick["turn_b"]]
    iai=seq[pick["iai"]]
    hair=seq[pick["hair"]]
    cast=seq[pick["cast"]]
    jfx=seq[pick["judgment_fx"]]

    # 1) idle vivo curto
    idle_frames=(idle_src[:4] if len(idle_src)>=4 else [neutral]*4)
    add(frames,durations,idle_frames,[120]*len(idle_frames),[180,150,180,260][:len(idle_frames)])

    # 2) caminhada para a direita
    wr=(walk*2)[:18]
    xs=[120+i*(520/(len(wr)-1)) for i in range(len(wr))]
    add(frames,durations,wr,xs,[90]*len(wr))

    # 3) iai slash + trail procedural
    def iaifx(c,idx,n,x):
        if 4<=idx<=8:
            slash_fx(c,round(x+65),GROUND_Y-82,(idx-3)/5)
    iai_ds=[130,100,85,70,48,38,34,42,65,90,120,220][:len(iai)]
    add(frames,durations,iai,[650]*len(iai),iai_ds,fx=iaifx)

    # 4) cabelo: duas leituras do mesmo sheet com timings diferentes
    hair_one=hair[:max(6,len(hair)//2+1)]
    add(frames,durations,hair_one,[650]*len(hair_one),[120,110,105,95,100,130,230][:len(hair_one)])

    # 5) anda até a direita e vira
    wr2=walk[:8]
    xs=[650+i*(155/(len(wr2)-1)) for i in range(len(wr2))]
    add(frames,durations,wr2,xs,[95]*len(wr2))
    add(frames,durations,turn_a,[805]*len(turn_a),[85]*len(turn_a))

    # 6) volta para a esquerda. Como os sheets de left-walk vieram inconsistentes,
    # usamos os últimos 3 frames left-facing da virada e oscilamos a ordem.
    left_seed=turn_a[-3:] if len(turn_a)>=3 else turn_a
    left_cycle=(left_seed + left_seed[-2:0:-1]) * 5
    left_cycle=left_cycle[:20]
    xs=[805-i*(555/(len(left_cycle)-1)) for i in range(len(left_cycle))]
    add(frames,durations,left_cycle,xs,[105]*len(left_cycle))

    # 7) idle + segunda virada
    add(frames,durations,[neutral,neutral],[250,250],[280,220])
    add(frames,durations,turn_b,[250]*len(turn_b),[90]*len(turn_b))

    # 8) Judgment Cut: cast corporal + energia azul concentrada
    def castfx(c,idx,n,x):
        phase=idx/max(1,n-1)
        blue_cast_fx(c,round(x+20),GROUND_Y-91,phase)
    cast_ds=[140,110,95,80,65,50,42,48,70,95,130,230][:len(cast)]
    add(frames,durations,cast,[250]*len(cast),cast_ds,fx=castfx)

    # 9) efeito espacial separado, Vergil em neutral enquanto o corte acontece à frente.
    for idx,vfx in enumerate(jfx):
        c=base_frame(); put_sprite(c,neutral,250)
        vf=isolate_cyan(vfx)
        if vf.getbbox():
            vf=scale_sprite(vf,118)
            c.alpha_composite(vf,(380,GROUND_Y-vf.height-18))
        frames.append(c); durations.append([55,45,40,38,42,46,52,60,70,85,110,180][idx] if idx<12 else 70)

    # 10) hair-fix mais demorado (segunda metade/reordenação) após o Judgment Cut.
    hair_two=hair[max(0,len(hair)//3):]
    add(frames,durations,hair_two,[250]*len(hair_two),[120]*max(0,len(hair_two)-1)+[320])

    # 11) encerra caminhando para o centro; loop volta ao idle da esquerda.
    wr3=walk[:12]
    xs=[250+i*( -130/(len(wr3)-1)) for i in range(len(wr3))]
    add(frames,durations,wr3,xs,[100]*len(wr3))

    # Salva GIF transparente. Piso é opaco somente na base.
    gif=OUT/"vergil-footer-draft.gif"
    frames[0].save(gif,save_all=True,append_images=frames[1:],duration=durations,loop=0,disposal=2,optimize=True,transparency=0)

    lines=["# Build report — Vergil footer","",f"Frames finais: **{len(frames)}**",f"Duração aproximada: **{sum(durations)/1000:.1f}s**",f"Canvas: **{W}×{H}**","","## Seleção automática de sheets","", "| Papel | Asset |", "|---|---:|"]
    for k,v in pick.items(): lines.append(f"| `{k}` | **{v:02d}** |")
    lines += ["","## Métricas por sheet","","| Asset | upper_var | mid_var | width_var | cyan_max |","|---:|---:|---:|---:|---:|"]
    for i,m in metrics.items(): lines.append(f"| {i:02d} | {m['upper_var']:.5f} | {m['mid_var']:.5f} | {m['width_var']:.5f} | {m['cyan_max']:.3f} |")
    lines += ["","## Observação","","O piso desta primeira renderização é um placeholder procedural porque nenhum dos 10 arquivos extraídos foi classificado como environment/floor. O piso autoral gerado anteriormente precisa ser adicionado ao pacote para a render final."]
    REPORT.write_text("\n".join(lines)+"\n",encoding="utf-8")
    print(gif, gif.stat().st_size, "bytes")


if __name__=="__main__":
    render()
