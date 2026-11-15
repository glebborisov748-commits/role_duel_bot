"""Build game samples from the licensed Kenney CC0 packs; synthesize electrical wire hiss.
Usage: python scripts/build_game_audio.py interface.zip impacts.zip
Existing drinking/food recordings are never changed.
"""
import array
import math
from pathlib import Path
import random
import subprocess
import sys
import tempfile
import wave
import zipfile

OUT = Path(__file__).resolve().parents[1]/'assets'/'audio'
RATE = 24000


def write(name, samples):
    data = array.array('h', [max(-32767,min(32767,round(x*32767))) for x in samples])
    with wave.open(str(OUT/(name+'.wav')),'wb') as output:
        output.setparams((1,2,RATE,0,'NONE','not compressed'))
        output.writeframes(data.tobytes())


def source(archive, name, duration=.23, gain=.55):
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory)/'source.ogg';path.write_bytes(archive.read('Audio/'+name))
        raw = subprocess.run(['ffmpeg','-v','error','-i',str(path),'-af',f'atrim=0:{duration},afade=t=out:st={max(0,duration-.04)}:d=0.04,volume={gain}', '-ar',str(RATE),'-ac','1','-f','s16le','-'],capture_output=True,check=True).stdout
        data=array.array('h');data.frombytes(raw)
        return [x/32768 for x in data]


def main():
    interface,impact=map(zipfile.ZipFile,sys.argv[1:3])
    for suffix,number in zip('abc',(1,2,4)):
        write('key'+suffix,source(interface,f'click_{number:03}.ogg',.10,.38))
        write('pin'+suffix,source(impact,f'impactMetal_light_{number-1:03}.ogg',.19,.38))
        write('chess'+suffix,source(impact,f'impactWood_medium_{number-1:03}.ogg',.20,.5))
        write('counter'+suffix,source(interface,f'drop_{number:03}.ogg',.22,.6))
        base=source(impact,f'impactWood_light_{number-1:03}.ogg',.12,.52)
        rng=random.Random(number);mixed=[0.]*(RATE//2)
        for at,gain in ((0,.6),(.065,.8),(.13,.65),(.22,.4),(.30,.25)):
            offset=round((at+rng.random()*.015)*RATE)
            for i,x in enumerate(base):
                if offset+i<len(mixed):mixed[offset+i]+=x*gain
        write('dice'+suffix,mixed)
        rng=random.Random(990+number);duration=.24+number*.025;low=0.;smooth=0.;hiss=[]
        for i in range(round(RATE*duration)):
            t=i/RATE;noise=rng.uniform(-1,1);low+=.20*(noise-low);smooth+=.045*(low-smooth)
            band=low-smooth;env=min(1,t/.014)*max(0,1-t/duration)**1.4
            crackle=(rng.uniform(-1,1)*.13 if rng.random()<.012 else 0)
            buzz=.012*math.sin(2*math.pi*(100+number*15)*t)
            hiss.append((band*.48+crackle+buzz)*env)
        write('wire'+suffix,hiss)
    write('pinbreak',source(impact,'impactMetal_medium_002.ogg',.3,.5))
    write('unlock',source(interface,'switch_006.ogg',.3,.65))
    write('match',source(interface,'select_004.ogg',.3,.5))
    write('reveal',source(interface,'switch_003.ogg',.2,.6))


if __name__=='__main__':main()
