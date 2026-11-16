"""Original soft planting/watering design using CC0 Kenney grass impacts and generated water tones."""
from build_game_audio import source,write,RATE
import math,random,zipfile,sys
z=zipfile.ZipFile(sys.argv[1])
for variant,idx in zip('abc',range(3)):
    dirt=source(z,f'footstep_grass_{idx:03}.ogg',.35,.55)
    samples=[0.]*(int(RATE*.38));rng=random.Random(880+idx)
    for i in range(len(samples)):
        t=i/RATE;x=dirt[i] if i<len(dirt) else 0
        # Soft ground contact followed by a short springy sprout pop; original sound, not PVZ audio.
        pop=.07*math.sin(2*math.pi*(150+idx*17)*t+22*t*t)*math.exp(-18*t)
        samples[i]=x*.62+pop
    write('soil'+variant,samples)
    drops=[0.]*(int(RATE*.5))
    for offset,freq in [(0,710+idx*60),(.095,1050+idx*90),(.19,835+idx*70)]:
        for i in range(int(RATE*.2)):
            at=int(offset*RATE)+i
            if at>=len(drops):break
            t=i/RATE;drops[at]+=.075*math.sin(2*math.pi*(freq*t-500*t*t))*math.exp(-22*t)
    write('waterplant'+variant,drops)
    harvest=source(z,f'footstep_grass_{idx+1:03}.ogg',.3,.4)
    for i in range(len(harvest)):
        t=i/RATE;harvest[i]+=.04*math.sin(2*math.pi*(740+idx*70)*t)*math.exp(-18*t)
    write('harvest'+variant,harvest)
