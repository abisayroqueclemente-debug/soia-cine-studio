#!/usr/bin/env python3
"""SOIA CINE STUDIO: banda sonora original y sintetizada, sin archivos de terceros."""
import argparse
import array
import math
import os
import random
import sys
import wave

RATE = 32000
DURATION = 20.0
TWOPI = math.tau
CHIMES = [(0.10, 164.81, .68), (4.0, 110.0, .43), (8.2, 130.81, .51),
          (12.8, 87.31, .64), (17.0, 196.00, .79)]


def sound(t, rng):
    fade = min(1.0, t / .1, max(0.0, (DURATION - t) / 1.05))
    drift = .88 + .12 * math.sin(.27 * t)
    # Slowly beating subharmonics: organ, cavern rumble, a distant pulse.
    low = (math.sin(TWOPI * 41.2 * t) * .105
           + math.sin(TWOPI * 55.2 * t + .26*math.sin(t*.73)) * .080
           + math.sin(TWOPI * 82.4 * t) * .035)
    pulse = (.5+.5*math.cos(TWOPI*1.16*t))**8 * .073
    air = (rng.random() * 2 - 1) * (.023 + .014*math.sin(t*.12)**2)
    # Bell harmonics; decays with long cathedral tails.
    bells = 0.0
    for start, f, gain in CHIMES:
        d=t-start
        if 0 <= d < 5.2:
            env = (1-math.exp(-d*30)) * math.exp(-1.13*d)
            partials = (
                math.sin(TWOPI*f*.5*d)*.42
                + math.sin(TWOPI*f*d)*.34
                + math.sin(TWOPI*f*2.02*d)*.17
                + math.sin(TWOPI*f*3.11*d)*.07
            )
            bells += env * gain * .28 * partials
    # Rising spectral tension near the reveal, without melodic borrowings.
    rise = max(0.0,min(1.0,(t-15.2)/2.5))
    tension = rise * .072 * math.sin(TWOPI*(90.0*t+4*math.sin(t*.4)))
    return math.tanh((drift*low+pulse+bells+tension+air)*1.32)*fade


def make(path):
    os.makedirs(os.path.dirname(os.path.abspath(path)),exist_ok=True)
    samples=array.array("h")
    rng=random.Random(260110)
    for n in range(int(DURATION*RATE)):
        t=n/RATE
        sample=sound(t,rng)
        samples.append(int(max(-1,min(1,sample))*32767))
    if sys.byteorder != "little":
        samples.byteswap()
    with wave.open(path,"wb") as waveout:
        waveout.setnchannels(1)
        waveout.setsampwidth(2)
        waveout.setframerate(RATE)
        waveout.writeframes(samples.tobytes())
    print("Audio original:",path,"seconds:",DURATION,"rate:",RATE)


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("output")
    opts=p.parse_args()
    make(opts.output)
