#!/usr/bin/env python3
"""El Guardian Oscuro: produce voz neuronal por segmentos, libre de musica y zumbido."""
import argparse
import array
import asyncio
import json
import math
from pathlib import Path
import subprocess
import sys
import wave

import edge_tts

SR=24000
DUR=30.0
# Phrase timing matches five 30s cinematographic scenes in storyboard.json.
PHRASES=[
 (0.55,5.0,"Durante cien años... nadie escuchó aquella campana."),
 (6.30,5.0,"Hasta que una noche... algo despertó bajo la catedral."),
 (12.7,4.8,"El Guardián... reconoció la señal."),
 (19.1,4.8,"Y la puerta... comenzó a abrirse."),
 (25.45,4.05,"Dime... ¿tú habrías entrado?")
]

def probe(path):
 p=subprocess.check_output(["ffprobe","-v","error","-show_entries","format=duration",
        "-of","default=noprint_wrappers=1:nokey=1",str(path)],text=True)
 return float(p.strip())

def read_pcm(path,rate=1.0):
 ff=["ffmpeg","-v","error","-i",str(path),"-af",f"atempo={rate:.5f}",
     "-ac","1","-ar",str(SR),"-f","s16le","-"]
 output=subprocess.check_output(ff)
 samples=array.array("h");samples.frombytes(output)
 if sys.byteorder!="little":samples.byteswap()
 return samples

async def get_voice(text,mp3,voice):
 # The official Edge client may refuse remote access; never fake successful narration.
 comm=edge_tts.Communicate(text,voice=voice,rate="-8%",pitch="-9Hz",volume="+0%")
 await comm.save(str(mp3))
 if not mp3.exists() or mp3.stat().st_size<1024:
  raise RuntimeError("La voz neuronal no produjo audio utilizable")

async def main():
 parser=argparse.ArgumentParser()
 parser.add_argument("--output",default="renders/guardian-narracion-neural.wav")
 parser.add_argument("--voice",default="es-MX-JorgeNeural")
 args=parser.parse_args()
 output=Path(args.output);output.parent.mkdir(parents=True,exist_ok=True)
 backing=output.parent
 master=array.array("f",[0.0])*int(SR*DUR)
 report={"voice":args.voice,"duration_seconds":DUR,"segments":[]}
 for ix,(start,slot,text) in enumerate(PHRASES,1):
  mp3=backing/f"frase-{ix:02d}.mp3"
  await get_voice(text,mp3,args.voice)
  original=probe(mp3)
  # Speed up ONLY if natural speech overruns its allocated scene. No mechanical slow-down.
  ratio=max(1.0,original/(slot-.17))
  pcm=read_pcm(mp3,ratio)
  n0=int(start*SR)
  for k,val in enumerate(pcm):
   dst=n0+k
   if dst>=len(master):break
   # Subtle fade-in/out to remove click. Never amplify a constant hum.
   fade=min(1.0,k/(SR*.055),max(0,(len(pcm)-k)/(SR*.085)))
   master[dst]+=val/32768*.86*fade
  report["segments"].append({"start":start,"slot":slot,"text":text,
                            "original_seconds":round(original,2),
                            "playback_speed":round(ratio,3)})
  print("Narracion",ix, "original",round(original,2),"seg", "atempo",round(ratio,2))
 # Unprocessed 30s reference; then clean voice mastered by ffmpeg.
 temp=backing/"voz-cruda.wav"
 with wave.open(str(temp),"wb") as w:
  w.setnchannels(1);w.setsampwidth(2);w.setframerate(SR)
  ints=array.array("h", (round(max(-.999,min(.999,v))*32767) for v in master))
  if sys.byteorder!="little":ints.byteswap()
  w.writeframes(ints.tobytes())
 subprocess.run(["ffmpeg","-hide_banner","-loglevel","error","-y",
                 "-i",str(temp),"-af",
                 "highpass=f=95,lowpass=f=8500,acompressor=threshold=-20dB:ratio=2.2:attack=12:release=160,loudnorm=I=-17:TP=-2:LRA=9",
                 "-ac","1","-ar",str(SR),str(output)],check=True)
 subprocess.run(["ffmpeg","-hide_banner","-loglevel","error","-y",
                 "-i",str(output),"-c:a","libmp3lame","-b:a","128k",
                 str(backing/"guardian-narracion-neural.mp3")],check=True)
 (backing/"guion-y-tiempos.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
 print("OK: voz neuronal sincronizada a 30 segundos",output)

if __name__=="__main__":
 asyncio.run(main())
