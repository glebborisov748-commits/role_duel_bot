"""Export generated portrait and wardrobe atlases without modifying source files.
Usage: python scripts/export_avatar_presets.py anime.png realism.png wardrobe.png
Requires ffmpeg/ffprobe for asset preparation only.
"""
import json,subprocess,sys
from pathlib import Path
OUT=Path(__file__).resolve().parents[1]/'assets'
KEYS=['short','undercut','fade','crop','sidepart','slicked','curls_short','medium','long','waves','bob','short','curls','ponytail','braid','pixie']

def dimensions(path):return json.loads(subprocess.check_output(['ffprobe','-v','error','-show_entries','stream=width,height','-of','json',path]))['streams'][0]
def crop(path,x,y,w,h,name,size):
 subprocess.run(['ffmpeg','-v','error','-y','-i',path,'-vf',f'crop={w}:{h}:{x}:{y},scale={size}','-c:v','libwebp','-quality','87',str(OUT/(name+'.webp'))],check=True)
def portraits(path,world,prefix="avatar"):
 m=dimensions(path);w,h=m['width'],m['height']
 for i,key in enumerate(KEYS):
  x=round(i%4*w/4);y=round(i//4*h/4)
  crop(path,x,y,round((i%4+1)*w/4)-x,round((i//4+1)*h/4)-y,prefix+'_'+world+('_male_' if i<8 else '_female_')+key,'320:360')
if __name__=='__main__':
 portraits(sys.argv[1],'anime');portraits(sys.argv[2],'realism')
 m=dimensions(sys.argv[3]);w,h=m['width'],m['height']
 for i,key in enumerate(('bunny','latex','stockings')):
  x=round(i*w/3);crop(sys.argv[3],x,0,round((i+1)*w/3)-x,h,'wardrobe_'+key,'256:256')
