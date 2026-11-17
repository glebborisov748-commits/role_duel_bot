"""Short CC0 connector contacts and original soft flowing-water effects.

No television-like electrical hiss, repetitive plucked drop tones, or changes to
key.wav. Rebuild: python scripts/build_refresh_audio.py interface.zip impact.zip
"""
import math,random,zipfile,sys
from build_game_audio import source,write,RATE
interface=zipfile.ZipFile(sys.argv[1]);impact=zipfile.ZipFile(sys.argv[2])
for k,suffix in enumerate('abc'):
    contact=source(interface,f'switch_{k+1:03}.ogg',.13,.35)
    metal=source(impact,f'impactMetal_light_{k:03}.ogg',.1,.16)
    values=[0.]*(int(.21*RATE))
    for i in range(len(values)):
        t=i/RATE
        values[i]=(contact[i] if i<len(contact) else 0)+(metal[i] if i<len(metal) else 0)
        if .075<t<.135:values[i]+=.025*math.sin(2*math.pi*(920+70*k)*(t-.075))*math.sin(math.pi*(t-.075)/.06)**2
    write('wire'+suffix,values)
    rng=random.Random(20261117+k);flow=[];low=0.;smooth=0.
    for i in range(round(.65*RATE)):
        t=i/RATE;noise=rng.uniform(-1,1);low+=.09*(noise-low);smooth+=.007*(low-smooth)
        env=min(1,t/.07)*min(1,(.65-t)/.13)
        # Continuous low-volume flow, with smooth low-frequency liquid movement.
        ripple=.018*math.sin(2*math.pi*(180*t+4*math.sin(12*t)))*(.5+.5*math.sin(33*t))
        flow.append(((low-smooth)*.38+ripple)*max(0,env))
    write('waterplant'+suffix,flow)
# The generic drop event shares the quiet water flow, rather than a bright UI pluck.
write('drop',flow)
