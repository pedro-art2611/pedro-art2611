"""Compõe a energia dos quatro PNGs em um loop transparente, sem animar a placa."""
from pathlib import Path
import math,json
import numpy as np
from PIL import Image,ImageDraw,ImageFilter

ROOT=Path(__file__).resolve().parents[1]
FOLDER=ROOT/'assets/v3/footer/divisor-vergil'
originals=[Image.open(FOLDER/f'source/energia-{i:02d}.png').convert('RGBA') for i in range(1,5)]
assert all(im.size==(2172,724) for im in originals)
boxes=[im.getchannel('A').point(lambda a:255 if a>8 else 0).getbbox() for im in originals]
box=(max(0,min(b[0] for b in boxes)-12),max(0,min(b[1] for b in boxes)-12),min(2172,max(b[2] for b in boxes)+12),min(724,max(b[3] for b in boxes)+12))
size=(1600,round((box[3]-box[1])*1600/(box[2]-box[0])))
def prepared(im): return im.crop(box).resize(size,Image.Resampling.LANCZOS)
images=[prepared(im) for im in originals]
arrays=[]
for im in images:
    a=np.asarray(im,dtype=np.float32)/255
    a[:,:,:3]*=a[:,:,3:4]
    arrays.append(a)

# Congela a placa, o texto, a cruz central e a linha mecânica.
mask=Image.new('L',(2172,724)); draw=ImageDraw.Draw(mask)
draw.polygon([(595,327),(755,305),(1419,305),(1586,327),(1586,384),(1419,406),(755,406),(595,384)],fill=255)
draw.rectangle((40,349,2135,368),fill=255)
draw.rectangle((1074,205,1100,505),fill=255)
draw.rectangle((30,306,145,410),fill=255)
draw.rectangle((2025,306,2140,410),fill=255)
protection=np.asarray(prepared(mask).filter(ImageFilter.GaussianBlur(1.2)),dtype=np.float32)/255
protection=protection[:,:,None]
scale=1600/(box[2]-box[0])
frames=[]
for index in range(60):
    phase=index/60
    energy=1.5*(1-math.cos(phase*2*math.pi))
    low=min(2,int(energy)); high=low+1
    mix=(1-math.cos((energy-low)*math.pi))/2
    rgba=arrays[low]*(1-mix)+arrays[high]*mix
    rgba=rgba*(1-protection)+arrays[0]*protection
    # Raios horizontais contínuos: deslocamento periódico, sem tremor da tipografia.
    bolts=Image.new('RGBA',size)
    bd=ImageDraw.Draw(bolts)
    for start,end,sign in [(175,805,-1),(1370,1990,1)]:
        points=[]
        for x in range(start,end+1,8):
            u=(x-start)/(end-start)
            envelope=math.sin(math.pi*u)
            zig=(math.sin(u*19+2*math.sin(u*51)-phase*2*math.pi)+.55*math.sin(u*83+phase*4*math.pi)+.3*math.sin(u*157-phase*6*math.pi))
            y=356+sign*(18+12*zig)*envelope
            points.append(((x-box[0])*scale,(y-box[1])*scale))
        bd.line(points,fill=(8,120,255,170),width=5)
        bd.line(points,fill=(80,220,255,205),width=2)
        bd.line(points,fill=(194,251,255,220),width=1)
    glow=bolts.filter(ImageFilter.GaussianBlur(5))
    bolts=Image.alpha_composite(glow,bolts)
    ba=np.array(bolts)
    ba[:,:,3]=(ba[:,:,3]*(1-protection[:,:,0])).astype('uint8')
    rgb=np.divide(rgba[:,:,:3],rgba[:,:,3:4],out=np.zeros_like(rgba[:,:,:3]),where=rgba[:,:,3:4]>0)
    plain=Image.fromarray(np.clip(np.concatenate((rgb,rgba[:,:,3:4]),axis=2)*255,0,255).astype('uint8'))
    frames.append(Image.alpha_composite(plain,Image.fromarray(ba)))
frames[0].save(FOLDER/'divisor-vergil.webp',save_all=True,append_images=frames[1:],duration=50,loop=0,lossless=False,quality=94,method=5)
frames[0].save(FOLDER/'divisor-vergil-estatico.png')
(FOLDER/'animacao.json').write_text(json.dumps(dict(size=size,source_crop=box,frames=60,duration_ms=3000,frame_duration_ms=50,format='WebP qualidade 94, alpha RGBA',loop='infinito',originals='source/energia-01.png a energia-04.png',motion='Transições suaves de energia e raios horizontais periódicos; placa e texto estabilizados.'),ensure_ascii=False,indent=2)+'\n',encoding='utf8')
check=Image.open(FOLDER/'divisor-vergil.webp')
assert check.n_frames==60 and check.info['loop']==0
assert frames[0].getpixel((0,0))[3]==0
print(json.dumps(dict(size=size,frames=check.n_frames,bytes=(FOLDER/'divisor-vergil.webp').stat().st_size)))
