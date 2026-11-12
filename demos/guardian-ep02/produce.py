#!/usr/bin/env python3
"""SOIA CINE STUDIO | EL GUARDIAN OSCURO, EP02 | 90-second documentary-horror short.
Original artwork, original score/foley, natural Mexican Spanish neural narration.
Historical claims bounded: traditional Setne fiction, NOT evidence of literal magic.
"""
from __future__ import annotations

import array
import asyncio
import io
import json
import math
import os
from pathlib import Path
import random
import subprocess
import sys
import urllib.parse
import urllib.request
import wave

import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance, ImageOps
import edge_tts

ROOT=Path(__file__).resolve().parent
OUT=Path("renders/guardian-thot-90s")
OUT.mkdir(parents=True,exist_ok=True)
W,H=720,1280
FPS=24
SCENE_SECONDS=9
SCENES=10
LENGTH=90
SR=24000
VIDEO_NAME="EL_GUARDIAN_OSCURO_02_EL_LIBRO_DE_THOT_90S.mp4"
FONTREG="/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
FONTBOLD="/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
FONTSANS="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FNT_SMALL=ImageFont.truetype(FONTSANS,21)
FNT_TITLE=ImageFont.truetype(FONTBOLD,43)
FNT_NAME=ImageFont.truetype(FONTBOLD,25)

LINES=[
("EL LIBRO PROHIBIDO", "¿Y si existiera un libro que te revelara lo que nadie debe saber... pero cobrara tu vida por cada página?"),
("LOS SECRETOS DE THOT", "En Egipto, la leyenda hablaba de un texto escrito por Thot, dios de la escritura y guardián de los secretos."),
("UN PODER IMPOSIBLE", "Se decía que sus palabras permitían comprender a los animales y contemplar misterios ocultos para cualquier mortal."),
("LA TUMBA SELLADA", "El príncipe Setne, protagonista de un antiguo relato, descubrió que el libro reposaba en una tumba sellada."),
("EL DUEÑO DE LA TUMBA", "Allí lo esperaba Naneferkaptah. O, mejor dicho... la sombra de alguien que había pagado un precio terrible por poseerlo."),
("UNA ADVERTENCIA", "Una voz surgió de la oscuridad para advertirle: la búsqueda de aquel conocimiento había destruido a una familia."),
("LA PÁGINA ROBADA", "Pero Setne no escuchó. Extendió la mano, tomó el libro... y la cripta quedó en un silencio imposible."),
("EL PRECIO DEL SABER", "La leyenda cuenta que el objeto debía regresar a su lugar. Ningún poder justificaba el sufrimiento que dejaba atrás."),
("¿HISTORIA O LEYENDA?", "Hay textos egipcios antiguos que cuentan esta historia. No prueban que existiera un libro capaz de realizar prodigios."),
("¿TÚ LO LEERÍAS?", "Y ahora te pregunto... si encontraras sus páginas bajo tierra... ¿las leerías? Soy... el Guardián Oscuro.")
]

PUBLIC_DOMAIN_SOURCES=[
 {"key":"karnak","filename":"Great Hypostyle Hall.jpg","license":"Public domain","author":"Markh (Wikimedia Commons)","source":"https://commons.wikimedia.org/wiki/File:Great_Hypostyle_Hall.jpg"},
 {"key":"thoth","filename":"Thoth and Khepri from the Papyrus of Imenemsauf.jpg","license":"Public domain — ancient artwork","author":"Ancient Egyptian artist, photographic reproduction (Wikimedia Commons)","source":"https://commons.wikimedia.org/wiki/File:Thoth_and_Khepri_from_the_Papyrus_of_Imenemsauf.jpg"},
 {"key":"temple","filename":"Karnak Temple Great Hypostyle Hall 2014.jpg","license":"CC0 1.0","author":"Tsyganov Sergey (Wikimedia Commons)","source":"https://commons.wikimedia.org/wiki/File:Karnak_Temple_Great_Hypostyle_Hall_2014.jpg"},
 {"key":"panorama","filename":"Karnakpanorama.jpg","license":"Public domain","author":"Blalonde (Wikimedia Commons)","source":"https://commons.wikimedia.org/wiki/File:Karnakpanorama.jpg"}
]

def sh(cmd, **kw):
 print("$"," ".join(map(str,cmd))[:480],flush=True)
 return subprocess.run(cmd,check=True,**kw)

def safe_photo(info):
 # Historic openly licensed art/photos; failure is safe: original painted scene instead.
 url="https://commons.wikimedia.org/wiki/Special:FilePath/"+urllib.parse.quote(info["filename"])+"?width=1100"
 try:
  request=urllib.request.Request(url,headers={"User-Agent":"SOIA-CineStudio/1.0 (video media research educational; public-domain images)","Accept":"image/jpeg,image/png,*/*"})
  with urllib.request.urlopen(request,timeout=15) as r:
   content=r.read(10_000_000)
  img=Image.open(io.BytesIO(content))
  img.load()
  if img.width<380 or img.height<300:raise ValueError("source too small")
  print("PUBLIC-DOMAIN IMAGE LOADED:",info["key"],img.size,flush=True)
  return img.convert("RGB")
 except Exception as e:
  print("PD IMAGE UNAVAILABLE; ORIGINAL PAINTED ALTERNATIVE:",info["key"],str(e)[:150],flush=True)
  return None

def fitted(img,w,h):
 # ImageOps.fit avoids black bars and ugly stretch.
 return ImageOps.fit(img,(w,h),method=Image.Resampling.LANCZOS,centering=(.50,.44))

def backdrop(seed,source=None):
 rng=np.random.default_rng(seed)
 if source is not None:
  im=fitted(source,W,H)
  im=ImageEnhance.Contrast(im).enhance(1.6)
  im=ImageEnhance.Color(im).enhance(.19)
  base=np.asarray(im.convert("RGB"),dtype=np.float32)
  # Unified chiaroscuro: cool silver moonlight + smoky amber highlights.
  base=base*np.array([.63,.68,.83],np.float32)+np.array([2,5,9],np.float32)
 else:
  y=np.arange(H,dtype=np.float32)[:,None]
  x=np.arange(W,dtype=np.float32)[None,:]
  cloud=np.sin(x*.009+seed)+np.sin((x+y*.17)*.019+seed*2)*.6+np.cos(y*.012+seed)
  shade=18+10*np.maximum(cloud,0)+16*(1-y/H)
  base=np.zeros((H,W,3),dtype=np.float32)
  base[:,:,0]=shade*.75;base[:,:,1]=shade*.85;base[:,:,2]=shade*1.16
  # Thin naturalistic shaft of moonlight in the far side of the ruined temple.
  shaft=(np.exp(-((x-W*.55-y*.06)/150)**2)*(.1+y/H*.24))*45
  base+=shaft[:,:,None]*np.array([.75,.85,1.05],dtype=np.float32)
 gr=rng.normal(0,4.2,(H,W,1)).astype(np.float32)
 base=np.clip(base+gr,0,255).astype(np.uint8)
 return Image.fromarray(base,"RGB").convert("RGBA")

def fog(im,seed,power=1):
 rng=random.Random(seed)
 layer=Image.new("RGBA",(W,H))
 d=ImageDraw.Draw(layer,"RGBA")
 for j in range(25):
  x=rng.randrange(-280,W+280);y=rng.randrange(150,H+120)
  radius=rng.randrange(80,250)
  d.ellipse((x-radius,y-radius//3,x+radius,y+radius//3),fill=(129,146,168,int(rng.randrange(2,11)*power)))
 layer=layer.filter(ImageFilter.GaussianBlur(34))
 return Image.alpha_composite(im,layer)

def beam(im,x,y,radius,color=(255,182,83),amount=125):
 lay=Image.new("RGBA",(W,H))
 d=ImageDraw.Draw(lay,"RGBA")
 d.ellipse((x-radius,y-radius,x+radius,y+radius),fill=(*color,amount))
 lay=lay.filter(ImageFilter.GaussianBlur(max(15,radius//2)))
 return Image.alpha_composite(im,lay)

def glyphs(draw,x,y,scale,count,seed,color=(191,138,69,190)):
 rng=random.Random(seed)
 for i in range(count):
  a=x+(i%7)*23*scale+rng.randint(-3,3)
  b=y+(i//7)*30*scale+rng.randint(-3,3)
  k=i%5
  width=max(1,int(scale*2))
  if k==0:
   draw.ellipse((a,b,a+11*scale,b+14*scale),outline=color,width=width)
   draw.line((a+6*scale,b+14*scale,a+7*scale,b+23*scale),fill=color,width=width)
  elif k==1:
   draw.line((a,b+13*scale,a+12*scale,b,a+17*scale,b+19*scale),fill=color,width=width)
  elif k==2:
   draw.arc((a,b,a+18*scale,b+16*scale),180,360,fill=color,width=width)
   draw.line((a+9*scale,b+9*scale,a+9*scale,b+21*scale),fill=color,width=width)
  elif k==3:
   draw.line((a,b,a+13*scale,b+17*scale,a+13*scale,b),fill=color,width=width)
  else:
   draw.ellipse((a,b,a+6*scale,b+6*scale),fill=color)
   draw.line((a+3*scale,b+5*scale,a+9*scale,b+20*scale),fill=color,width=width)

def pillars(im,seed):
 d=ImageDraw.Draw(im,"RGBA")
 rng=random.Random(seed)
 for x in (-40,90,600,740):
  w=54 if x in (90,600) else 105
  d.polygon([(x,40),(x+w,40),(x+w+14,H),(x-12,H)],fill=(8,8,13,218))
  for k in range(6):
   xx=x+9+k*max(4,int(w/7))
   d.line((xx,65,xx+int(8*math.sin(k)),H),fill=(121,113,110,24),width=3)
  for y in range(130,1100,160):
   d.rectangle((x-11,y,x+w+11,y+19),fill=(9,9,12,180),outline=(109,91,66,45),width=2)
 return im

def pedestal(im,y=955):
 d=ImageDraw.Draw(im,"RGBA")
 d.polygon([(130,y),(590,y),(674,H),(40,H)],fill=(13,12,17,255),outline=(106,77,44,190),width=5)
 for yy in range(y+42,H,62):
  d.line((75,yy,650,yy),fill=(137,98,63,29),width=2)
 return im

def artifact_book(im,seed,y=730,size=1.0,closed=False):
 # Original imaginative artifact: stone table, bound black cover and lit parchment.
 rng=random.Random(seed)
 im=beam(im,W//2,int(y),290,(231,127,43),120)
 d=ImageDraw.Draw(im,"RGBA")
 w=int(230*size);h=int(126*size);cx=W//2
 if closed:
  pts=[(cx-w,y-45),(cx+w,y-45),(cx+w+30,y+h),(cx-w-30,y+h)]
  d.polygon(pts,fill=(34,20,19,255),outline=(202,143,64,255),width=8)
  d.polygon([(cx-w+21,y-20),(cx+w-21,y-20),(cx+w+3,y+h-20),(cx-w-3,y+h-20)],fill=(21,22,25,220),outline=(143,114,66,220),width=3)
  glyphs(d,cx-70,y+4,1.0,20,seed+100,(224,161,84,205))
 else:
  d.polygon([(cx-14,y-40),(cx-w-15,y-88),(cx-w-45,y+h),(cx-8,y+h+32)],fill=(168,128,75,255),outline=(252,181,86,255),width=4)
  d.polygon([(cx+14,y-40),(cx+w+15,y-88),(cx+w+45,y+h),(cx+8,y+h+32)],fill=(184,137,81,255),outline=(251,190,99,255),width=4)
  d.polygon([(cx-13,y-40),(cx-15,y+h+23),(cx+16,y+h+23),(cx+14,y-40)],fill=(80,54,36,255))
  for k in range(1,8):
   d.line((cx-20-k*24,y-51+(k%2)*5,cx-17-k*27,y+h-6),fill=(69,50,42,92),width=2)
   d.line((cx+21+k*24,y-49+(k%2)*5,cx+17+k*27,y+h-5),fill=(69,50,42,92),width=2)
  glyphs(d,cx-183,y-10,.75,28,seed,(69,37,29,215))
  glyphs(d,cx+43,y-10,.75,28,seed+10,(76,40,30,215))
  d.ellipse((cx-14,y+20,cx+14,y+55),outline=(228,145,41,235),width=5)
 for i in range(120):
  xx=cx+rng.gauss(0,w*.65);yy=y+rng.gauss(0,h*.95)
  rr=rng.choice([1,1,2,3])
  d.ellipse((xx-rr,yy-rr,xx+rr,yy+rr),fill=(244,167,74,rng.randrange(35,130)))
 return im

def tomb(im,seed):
 d=ImageDraw.Draw(im,"RGBA")
 im=beam(im,370,480,230,(128,164,192),95);d=ImageDraw.Draw(im,"RGBA")
 d.polygon([(135,400),(580,400),(655,1060),(65,1060)],fill=(13,14,19,243),outline=(119,98,70,240),width=12)
 for k in range(8):
  y=475+k*61
  d.line((125+k*2,y,600-k*2,y),fill=(114,104,92,36),width=2)
 d.ellipse((242,595,485,820),outline=(178,111,50,155),width=7)
 d.ellipse((260,610,469,803),outline=(217,159,85,125),width=2)
 glyphs(d,275,645,.83,30,seed,(226,156,83,184))
 im=beam(im,359,700,205,(219,113,44),95)
 return im

def figure(im,seed,guardian=False):
 d=ImageDraw.Draw(im,"RGBA")
 cx=355;top=245 if guardian else 295
 # Tall silhouette with severe black and gold regalia, face fully hidden.
 d.polygon([(cx,top),(cx-77,top+140),(cx-80,top+228),(cx+87,top+228),(cx+73,top+140)],fill=(9,10,16,255),outline=(195,141,66,240) if guardian else (112,103,98,150),width=5)
 d.ellipse((cx-58,top+210,cx+55,top+345),fill=(1,2,7,255))
 d.polygon([(cx-98,top+270),(cx+108,top+270),(cx+206,H),(cx-210,H)],fill=(5,7,14,255),outline=(152,116,73,187) if guardian else (111,117,133,130),width=5)
 for dx in (-75,75):
  d.line((cx+dx,top+380,cx+int(dx*1.35),H),fill=(184,128,61,139) if guardian else (114,131,156,74),width=5)
 if guardian:
  d.line((cx,top+20,cx,top+214),fill=(222,164,91,165),width=5)
  d.ellipse((cx-26,top+92,cx+26,top+146),outline=(198,145,63,195),width=3)
  d.line((cx+170,top+400,cx+200,top+50),fill=(160,107,51,229),width=11)
  d.ellipse((cx+162,top+24,cx+237,top+83),outline=(225,153,65,200),width=8)
 else:
  d.ellipse((cx-25,top+271,cx+19,top+291),fill=(202,161,98,90))
 return im

def draw_scene(index,photos):
 key={1:"karnak",2:"thoth",3:"temple",4:"karnak",6:"panorama",8:"thoth"}.get(index)
 base=backdrop(index*115+7,photos.get(key) if key else None)
 # Darkness is deliberate but narrative events must remain legible.
 if index in (0,3,5,6,7,9):base=pillars(base,index+3)
 if index==0:
  base=beam(base,380,600,220,(239,155,75),110)
  base=pedestal(base,885);base=artifact_book(base,1,700,.72,closed=True)
 elif index==1:
  base=beam(base,310,405,245,(116,165,194),100)
 elif index==2:
  base=beam(base,412,445,330,(190,133,64),115)
  d=ImageDraw.Draw(base,"RGBA")
  glyphs(d,75,540,1.28,80,2,(218,166,94,143))
 elif index==3:
  base=tomb(base,3)
 elif index==4:
  base=figure(base,4,guardian=False);base=beam(base,355,700,170,(173,131,76),79)
 elif index==5:
  base=beam(base,365,470,200,(160,183,190),80)
  base=figure(base,5,guardian=False)
  d=ImageDraw.Draw(base,"RGBA")
  for k in range(4):
   d.arc((130+k*20,450+k*5,580-k*20,920),205,335,fill=(186,184,196,22),width=5)
 elif index==6:
  base=pedestal(base,900);base=artifact_book(base,6,635,.83,closed=False)
 elif index==7:
  base=pedestal(base,925);base=artifact_book(base,7,680,.72,closed=False)
  d=ImageDraw.Draw(base,"RGBA")
  for k in range(11):
   x=120+k*45;d.line((x,280,x+23,390),fill=(181,114,61,31),width=2)
 elif index==8:
  base=beam(base,350,610,250,(116,154,184),65)
  d=ImageDraw.Draw(base,"RGBA")
  glyphs(d,65,640,1.25,63,89,(224,169,103,95))
 else:
  base=figure(base,9,guardian=True);base=beam(base,350,520,220,(224,118,41),70)
  d=ImageDraw.Draw(base,"RGBA")
  for x in (315,392):
   d.ellipse((x-19,540,x+19,549),fill=(255,184,65,223))
   d.ellipse((x-8,541,x+8,544),fill=(254,241,189,243))
 # Fog, rays, analog vignette.
 base=fog(base,index+17,power=1.5)
 d=ImageDraw.Draw(base,"RGBA")
 rng=random.Random(200+index)
 for k in range(85):
  x=rng.randint(0,W);y=rng.randint(0,H)
  r=rng.choice([1,1,2,3])
  d.ellipse((x-r,y-r,x+r,y+r),fill=(255,185,96,rng.randrange(20,100)))
 # Dark areas above and below as dynamic-friendly cinematic safe zones.
 overlay=Image.new("RGBA",(W,H),(0,0,0,0))
 od=ImageDraw.Draw(overlay,"RGBA")
 for y in range(0,250):
  od.line((0,y,W,y),fill=(0,0,0,int(190*(1-y/250))),width=1)
 for y in range(930,H):
  od.line((0,y,W,y),fill=(0,0,0,int(210*((y-930)/(H-930)))),width=1)
 base=Image.alpha_composite(base,overlay)
 d=ImageDraw.Draw(base,"RGBA")
 # Brand at top, small and below notches.
 d.text((W/2,81),"EL GUARDIÁN OSCURO",font=FNT_NAME,anchor="mm",fill=(226,184,119,242),stroke_width=1,stroke_fill=(0,0,0,240))
 d.line((W*.29,106,W*.71,106),fill=(169,104,58,150),width=2)
 d.text((W/2,1158),LINES[index][0],font=FNT_TITLE,anchor="mm",fill=(244,225,192,252),stroke_width=3,stroke_fill=(0,0,0,225))
 d.text((W/2,1205),"LIBROS CONDENADOS  •  EPISODIO 02",font=FNT_SMALL,anchor="mm",fill=(198,160,117,236))
 # Vignette with precomputation at output scale.
 xs=np.linspace(-1,1,W,dtype=np.float32)[None,:]
 ys=np.linspace(-1,1,H,dtype=np.float32)[:,None]
 v=np.clip(1-.47*(xs*xs+ys*ys),.22,1.0)
 a=np.asarray(base.convert("RGB"),dtype=np.float32)
 a=np.clip(a*v[:,:,None],0,255).astype(np.uint8)
 path=OUT/f"scene_{index+1:02}.jpg"
 Image.fromarray(a).save(path,quality=91,subsampling=0)
 return path

def build_artwork():
 refs={}
 used=[]
 for source in PUBLIC_DOMAIN_SOURCES:
  im=safe_photo(source)
  if im is not None:
   refs[source["key"]]=im
   used.append({k:source[k] for k in ("key","source","license","author")})
 paths=[draw_scene(i,refs) for i in range(SCENES)]
 (OUT/"image_sources.json").write_text(json.dumps(used,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
 print("Scene art complete:",len(paths),"PD images:",len(used),flush=True)
 return paths

async def synthesize_voice():
 voice=np.zeros(SR*LENGTH,dtype=np.float32)
 segments=[]
 name="es-MX-JorgeNeural"
 for i,(_,line) in enumerate(LINES):
  start=i*SCENE_SECONDS+.66
  filename=OUT/f"voz_{i+1:02}.mp3"
  # Consistency: same male natural voice for the entire 90 seconds.
  communicate=edge_tts.Communicate(line,voice=name,rate="-4%",pitch="-8Hz")
  await communicate.save(str(filename))
  if not filename.exists() or filename.stat().st_size<1000:
   raise RuntimeError(f"No se generó voz para la escena {i+1}")
  raw=subprocess.check_output(["ffmpeg","-v","error","-i",str(filename),
    "-ac","1","-ar",str(SR),"-f","s16le","-"])
  pcm=np.frombuffer(raw,dtype="<i2").astype(np.float32)/32768
  length=len(pcm)/SR
  max_length=SCENE_SECONDS-1.05
  speed=max(1.,length/max_length)
  if speed>1.005:
   if speed>1.32:raise RuntimeError(f"Locución demasiado larga en escena {i+1}: {length:.2f} s")
   pcm_raw=subprocess.check_output(["ffmpeg","-v","error","-i",str(filename),
    "-af",f"atempo={speed:.4f}","-ac","1","-ar",str(SR),"-f","s16le","-"])
   pcm=np.frombuffer(pcm_raw,dtype="<i2").astype(np.float32)/32768
  ix=int(start*SR)
  fade=int(.085*SR)
  pcm=pcm.copy()
  pcm[:min(fade,len(pcm))]*=np.linspace(0,1,min(fade,len(pcm)))
  pcm[-min(fade,len(pcm)):]*=np.linspace(1,0,min(fade,len(pcm)))
  right=min(len(voice),ix+len(pcm))
  voice[ix:right]+=pcm[:right-ix]*.73
  segments.append({"scene":i+1,"start_seconds":round(start,2),"raw_duration":round(length,2),
    "speed":round(speed,3),"text":line})
  print("VOICE",i+1,"length",round(length,2),"speed",round(speed,3),flush=True)
 (OUT/"voice_timing.json").write_text(json.dumps(segments,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
 return voice

def make_score():
 rng=np.random.default_rng(20261111)
 n=SR*LENGTH
 t=np.arange(n,dtype=np.float32)/SR
 # Atmospheric noise, moving wind, ritual chimes, not a continuous deep tone.
 coarse=rng.normal(0,1,int(LENGTH*13)+2).astype(np.float32)
 wind=np.interp(np.arange(n,dtype=np.float32),np.arange(len(coarse),dtype=np.float32)*SR/13,coarse).astype(np.float32)
 score=.022*wind+.008*rng.normal(0,1,n).astype(np.float32)
 bell_times=[1.3,10.0,19.0,29.0,37.5,47.0,56.0,65.0,76.0,84.0]
 for j,start in enumerate(bell_times):
  off=int(start*SR);duration=int(SR*3.0)
  sl=min(duration,n-off)
  if sl<=0:continue
  q=np.arange(sl,dtype=np.float32)/SR
  fall=np.exp(-q*(1.28 if j%3 else 1.75))
  bell=(.57*np.sin(2*math.pi*(161+j*4)*q)+
        .23*np.sin(2*math.pi*(322+j*8)*q)+
        .12*np.sin(2*math.pi*(501+j*9)*q))*.15*fall
  score[off:off+sl]+=bell.astype(np.float32)
 for start in [23.5,40.0,53.5,70.0,80.6]:
  ix=int(start*SR);length=min(int(1.9*SR),n-ix)
  q=np.arange(length,dtype=np.float32)/SR
  boom=(np.sin(2*math.pi*113*q)*np.exp(-3.6*q)*.17+
        np.sin(2*math.pi*233*q)*np.exp(-5*q)*.04)
  score[ix:ix+length]+=boom.astype(np.float32)
 # Organic pulses only at transitions; highpass removes any infrasonic hum.
 for k in range(9):
  ix=int((k+1)*SCENE_SECONDS*SR)
  if ix>=n:continue
  length=min(SR,n-ix)
  q=np.arange(length,dtype=np.float32)/SR
  score[ix:ix+length]+=(.04*np.sin(2*math.pi*181*q)*np.exp(-3*q)).astype(np.float32)
 return score

def wavewrite(path,samples):
 clipped=np.clip(samples,-.97,.97)
 pcm=(clipped*32767).astype("<i2")
 with wave.open(str(path),"wb") as w:
  w.setnchannels(1);w.setsampwidth(2);w.setframerate(SR)
  w.writeframes(pcm.tobytes())

def mix_sound(voice,score):
 # Predictable manual ducking under narration, smooth scene-level envelope.
 gain=np.full(len(voice),.28,dtype=np.float32)
 for i in range(SCENES):
  a=int((i*SCENE_SECONDS+.40)*SR)
  b=int(((i+1)*SCENE_SECONDS-.45)*SR)
  gain[a:b]=.105
 # Avoid sudden gain changes by samplewise 150ms ramps.
 kernel=int(.18*SR)
 coarse=np.interp(np.arange(len(gain),dtype=np.float32),np.arange(0,len(gain),kernel,dtype=np.float32),gain[::kernel]).astype(np.float32) if len(gain[::kernel])>1 else gain
 mixture=voice+score*coarse
 peak=float(np.max(np.abs(mixture)))
 if peak>.87:mixture*=.87/peak
 # score only separately useful for later SOIA editing
 wavewrite(OUT/"musica_y_efectos.wav",score*.26)
 wavewrite(OUT/"narracion_solamente.wav",voice)
 wavewrite(OUT/"mezcla_final.wav",mixture)
 return OUT/"mezcla_final.wav"

def make_video(stills):
 clips=[]
 for i,img in enumerate(stills):
  clip=OUT/f"clip_{i+1:02}.mp4"
  z="min(zoom+0.00034,1.073)"
  x="iw/2-iw/zoom/2+8*sin(on/27)"
  y="ih/2-ih/zoom/2+5*cos(on/33)"
  vf=f"scale=900:1600:force_original_aspect_ratio=increase,crop=900:1600,zoompan=z='{z}':x='{x}':y='{y}':d={FPS*SCENE_SECONDS}:s=720x1280:fps={FPS},format=yuv420p"
  sh(["ffmpeg","-nostdin","-v","warning","-y","-loop","1","-framerate",str(FPS),
    "-i",str(img),"-vf",vf,"-frames:v",str(FPS*SCENE_SECONDS),
    "-an","-c:v","libx264","-preset","veryfast","-crf","23",
    "-pix_fmt","yuv420p",str(clip)])
  clips.append(clip)
 listpath=OUT/"concat.txt"
 listpath.write_text("".join("file '"+p.name+"'\n" for p in clips),encoding="utf8")
 picture=OUT/"picture.mp4"
 sh(["ffmpeg","-nostdin","-v","error","-y","-f","concat","-safe","0",
     "-i",str(listpath),"-c","copy",str(picture)])
 return picture

def export(picture,sound):
 final=OUT/VIDEO_NAME
 sh(["ffmpeg","-nostdin","-v","error","-y","-i",str(picture),"-i",str(sound),
     "-map","0:v:0","-map","1:a:0","-c:v","copy","-c:a","aac",
     "-b:a","192k","-ar","48000","-ac","2","-t","90",
     "-movflags","+faststart",str(final)])
 sh(["ffmpeg","-nostdin","-v","error","-y","-ss","83.5","-i",str(final),
     "-frames:v","1",str(OUT/"PORTADA.jpg")])
 p=subprocess.check_output(["ffprobe","-v","error","-show_entries",
   "format=duration,size:stream=codec_type,codec_name,width,height,r_frame_rate",
   "-of","json",str(final)],text=True)
 probe=json.loads(p)
 if abs(float(probe["format"]["duration"])-90.0)>.15:
  raise RuntimeError("La duración del video es incorrecta "+str(probe["format"]["duration"]))
 if not any(s.get("codec_type")=="video" and s.get("codec_name")=="h264" and
            s.get("width")==720 and s.get("height")==1280 for s in probe["streams"]):
  raise RuntimeError("H264 720x1280 no validado")
 if not any(s.get("codec_type")=="audio" and s.get("codec_name")=="aac" for s in probe["streams"]):
  raise RuntimeError("AAC no validado")
 (OUT/"reporte_tecnico.json").write_text(json.dumps(probe,indent=2)+"\n",encoding="utf8")
 print("EPISODIO 02 COMPLETO / MP4",final,"90.0 segundos",flush=True)
 return final

def make_info():
 guion="# EL GUARDIÁN OSCURO — EPISODIO 02: EL LIBRO DE THOT\n\n"
 guion+="Duración 01:30. Ficción dramatizada de un relato egipcio tradicional. 10 escenas de 9 segundos.\n\n"
 for i,(caption,narration) in enumerate(LINES):
  guion+=f"**{i*9:02}–{(i+1)*9:02} s · {caption}**\n\n{narration}\n\n"
 guion+="### Nota histórica\nEl Setne legendario no prueba la existencia de un libro mágico; el relato procede de literatura egipcia antigua.\n"
 guion+="El 'Ancient Egyptian Book of Thoth' estudiado por investigadores es una composición textual egipcia de otro carácter.\n"
 guion+="\n### Fuentes\n"
 guion+="- Google Drive del usuario: Jacques Bergier, *Los libros condenados*, capítulo «El libro de Toth» (documento propio, inspiración argumental).\n"
 guion+="- M. Lichtheim, *The First Tale of Setne Khamwas* (traducción): https://www.attalus.org/egypt/setne.html\n"
 guion+="- Johns Hopkins: *The Ancient Egyptian Book of Thoth*: https://neareast.jhu.edu/faculty-books/the-ancient-egyptian-book-of-thoth/\n"
 (OUT/"GUION_Y_FUENTES.md").write_text(guion,encoding="utf8")

async def go():
 make_info()
 stills=build_artwork()
 # Optional force-artwork-only for diagnosing visuals.
 if os.getenv("SOIA_ONLY_ARTWORK")=="1":
  return
 voice=await synthesize_voice()
 score=make_score()
 sound=mix_sound(voice,score)
 video=make_video(stills)
 export(video,sound)

if __name__=="__main__":
 asyncio.run(go())
