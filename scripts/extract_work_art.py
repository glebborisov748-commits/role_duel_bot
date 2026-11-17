"""Export the two generated shop-style atlases to mobile WebP sprites.
Usage: python scripts/extract_work_art.py first-atlas.png second-atlas.png
Requires ffmpeg and ffprobe; source atlases are kept unchanged.
"""
import json
from pathlib import Path
import subprocess
import sys
OUT=Path(__file__).resolve().parents[1]/'assets'

def export(path,columns,keys):
 metadata=json.loads(subprocess.check_output(['ffprobe','-v','error','-select_streams','v:0','-show_entries','stream=width,height','-of','json',str(path)]))['streams'][0]
 w,h=metadata['width'],metadata['height'];rows=(len(keys)+columns-1)//columns
 for i,key in enumerate(keys):
  x=round(i%columns*w/columns);y=round(i//columns*h/rows)
  cw=round((i%columns+1)*w/columns)-x;ch=round((i//columns+1)*h/rows)-y
  subprocess.run(['ffmpeg','-v','error','-y','-i',str(path),'-vf',f'crop={cw}:{ch}:{x}:{y},scale=256:256','-c:v','libwebp','-quality','85',str(OUT/('work_'+key+'.webp'))],check=True)

if __name__=='__main__':
 export(Path(sys.argv[1]),4,['bomb','coins','bills','magnet','bed_dry','bed_wet','seedling','young','pumpkin','carrot','wheat','tomato','corn','melon','drop','parcel'])
 export(Path(sys.argv[2]),2,['shield','slow','double','can'])
