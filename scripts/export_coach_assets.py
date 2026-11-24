"""Extract generated UI sprites without changing the source artwork."""
from pathlib import Path
import sys
from PIL import Image
source=Image.open(sys.argv[1]).convert('RGBA');w,h=source.size
out=Path(__file__).resolve().parents[1]/'assets'
for name,cell in [('coach_finger',(0,0,w//2,h//2)),('work_crate_closed',(w//2,0,w,h//2)),('work_crate_open',(0,h//2,w//2,h)),('work_crate_damaged',(w//2,h//2,w,h))]:
 im=source.crop(cell);a=im.getchannel('A');box=a.point(lambda v:255 if v>190 else 0).getbbox();im=im.crop(box)
 if name=='coach_finger':
  im.thumbnail((78,96),Image.Resampling.LANCZOS);alpha=im.getchannel('A');pix=alpha.load();tip=[x for y in range(min(5,im.height)) for x in range(im.width) if pix[x,y]>210];tx=round(sum(tip)/len(tip)) if tip else im.width//2
  canvas=Image.new('RGBA',(96,112));canvas.alpha_composite(im,(48-tx,8));im=canvas
 else:
  im.thumbnail((240,200),Image.Resampling.LANCZOS);canvas=Image.new('RGBA',(256,216));canvas.alpha_composite(im,((256-im.width)//2,(216-im.height)//2));im=canvas
 im.save(out/(name+'.webp'),quality=94,method=6)
if len(sys.argv)>2:
 Image.open(sys.argv[2]).convert('RGB').resize((768,768),Image.Resampling.LANCZOS).save(out/'work_mosaic_order.webp',quality=91,method=6)
