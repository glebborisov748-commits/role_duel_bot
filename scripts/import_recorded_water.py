"""Import the CC0 TyberiusGames waterflow recording; see assets/audio/SOURCES.md.
Usage: python scripts/import_recorded_water.py waterflow.mp3
No synthesized watering tones, no runtime dependency on ffmpeg.
"""
import subprocess,sys
from pathlib import Path
out=Path(__file__).resolve().parents[1]/'assets'/'audio'
for suffix,offset in zip('abc',[0.2,1.2,2.2]):
 subprocess.run(['ffmpeg','-v','error','-y','-ss',str(offset),'-i',sys.argv[1],'-t','0.8','-af','afade=t=in:d=0.03,afade=t=out:st=0.65:d=0.15,volume=0.45','-ac','1','-ar','24000',str(out/f'waterplant{suffix}.wav')],check=True)
