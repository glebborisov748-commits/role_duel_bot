"""Technical sprite export for farm, curtains and the neutral collection catalog."""
from pathlib import Path
from PIL import Image
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(Path(__file__).resolve().parent))
from atlas_bounds import crop
SOURCE=ROOT.parent/'generated_images'
def save(cell,name,max_size):
 im=crop(cell);im.thumbnail(max_size,Image.Resampling.LANCZOS);im.save(ROOT/'assets'/name,quality=92,method=4)
def grid(filename,names):
 im=Image.open(SOURCE/filename).convert('RGBA');w,h=im.size
 for n,name in enumerate(names):save(im.crop((n%4*w//4,n//4*h//2,(n%4+1)*w//4,(n//4+1)*h//2)),name,(256,256))
if __name__=='__main__':
 grid('exec-897d420c-0bf9-4bf1-817a-65cb5d85ada8.png',[f'work_{k}.webp' for k in ('strawberry','chili','pineapple','mango','fertilizer','fertilizer_scoop','farm_v3_seedling','farm_v3_young')])
 im=Image.open(SOURCE/'exec-71a8a6a3-fa65-47d0-a99f-41af5513b354.png').convert('RGBA');w,h=im.size
 for name,box,size in [('left',(0,0,w//2,int(h*.66)),(320,720)),('right',(w//2,0,w,int(h*.66)),(320,720)),('podium',(0,int(h*.66),w//2,h),(440,200)),('spotlight',(w//2,int(h*.66),w,h),(320,420))]:save(im.crop(box),'stage_'+name+'.webp',size)
 if len(sys.argv)>1:grid(sys.argv[1],[f'collection_{k}.webp' for k in ('vibrator','plug','dildo','cuffs','gag','stroker','massager','gift')])
