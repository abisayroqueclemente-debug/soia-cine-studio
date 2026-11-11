#!/usr/bin/env python3
"""Original 25s score + Foley, synced to the five shots. No third-party media."""
import array
import argparse
import math
import os
import random
import sys
import wave

HZ=32000
SECONDS=25
TAU=math.tau
def win(t,start,end,r=.15):
    return max(0,min(1,(t-start)/r,(end-t)/r))
def env(t,start,length,decay=2):
    q=t-start
    return (1-math.exp(-q*28))*math.exp(-decay*q) if 0<=q<length else 0

def main(out):
    os.makedirs(os.path.dirname(os.path.abspath(out)),exist_ok=True)
    out_samples=array.array("h")
    rng=random.Random(421826)
    bell_events=((.72,87.3,1.0),(3.65,110,.55),(5.07,65.4,.65),
                 (10.2,130.8,.4),(15.35,98,.32),(19.55,55,.96))
    for n in range(HZ*SECONDS):
        t=n/HZ
        # Low cathedral drone, dissonant fifth with shifting stereo-like beating.
        bass=(math.sin(TAU*41.2*t)*.085+math.sin(TAU*62*t+.25*math.sin(.37*t))*.043)
        organ=(math.sin(TAU*82.4*t)*.032+math.sin(TAU*123.7*t)*.021+
               math.sin(TAU*173.5*t)*.012)
        air=(rng.random()*2-1)*.018
        # Five separate pulse designs: distant metal, stone, reveal, doors, sting.
        ring=0.0
        for start,f,amp in bell_events:
            q=t-start
            if 0<=q<5:
                e=(1-math.exp(-q*37))*math.exp(-q*1.2)*amp
                ring+=(math.sin(TAU*f*.5*q)*.37+
                       math.sin(TAU*f*q)*.41+
                       math.sin(TAU*f*2.04*q)*.17+
                       math.sin(TAU*f*3.12*q)*.08)*e*.29
        stone=win(t,6.5,9.8,.4)*(rng.random()*2-1)*.053*(.65+.35*math.sin(TAU*42*t))
        rise=win(t,11.8,15,.55)
        choir=rise*.040*(math.sin(TAU*196.0*t)+.54*math.sin(TAU*207.65*t))
        door=win(t,16,20.4,.65)*(rng.random()*2-1)*.065
        door+=win(t,16.5,20.0,.55)*math.sin(TAU*(49*t+2.5*math.sin(.4*t)))*.052
        final=env(t,21.8,3.1,.9)*(math.sin(TAU*69*t)*.17+math.sin(TAU*138*t)*.075)
        pulse=(max(0,math.sin(TAU*.91*t))**12)*.048
        sample=bass+organ+air+ring+stone+choir+door+final+pulse
        fade=max(0,min(1,t/.15,(SECONDS-t)/.7))
        sample=math.tanh(sample*1.55)*fade
        out_samples.append(int(max(-1,min(1,sample))*32767))
    if sys.byteorder!="little":out_samples.byteswap()
    with wave.open(out,"wb") as w:
        w.setnchannels(1);w.setsampwidth(2);w.setframerate(HZ);w.writeframes(out_samples.tobytes())
    print("GUARDIAN V2 ORIGINAL AUDIO",SECONDS,"sec",HZ,"Hz")
if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("output")
    main(parser.parse_args().output)
