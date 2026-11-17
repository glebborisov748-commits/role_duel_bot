"""Export transparent reaction, wardrobe and navigation artwork; keep source PNGs.
Usage: python scripts/export_followup_assets.py reactions.png clothes.png nav.png
Asset preparation only; does not run in the bot or submit generation tasks.
"""
import sys,subprocess
from pathlib import Path
from export_avatar_presets import dimensions,crop
for path,names,cols,rows,size in (
 (sys.argv[1],['reaction_heart','reaction_star','reaction_flame','reaction_party'],2,2,'160:160'),
 (sys.argv[2],['wardrobe_tracksuit','wardrobe_pajamas','wardrobe_collar','wardrobe_massager','wardrobe_shirt','wardrobe_trousers','wardrobe_hat','wardrobe_scarf'],4,2,'256:256')):
 d=dimensions(path);w,h=d['width']//cols,d['height']//rows
 for i,key in enumerate(names):crop(path,i%cols*w,i//cols*h,w,h,key,size)
out=Path(__file__).resolve().parents[1]/'assets'/'nav_wardrobe.webp'
subprocess.run(['ffmpeg','-v','error','-y','-i',sys.argv[3],'-vf','scale=192:192:force_original_aspect_ratio=decrease,pad=192:192:(ow-iw)/2:(oh-ih)/2:color=0x00000000','-quality','88',str(out)],check=True)
