"""Decode and inspect generated fitting sprites, including real alpha transparency."""
import sys
from pathlib import Path
from PIL import Image
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import mannequin_catalog as catalog
ROOT=Path(__file__).resolve().parents[1]
paths=[catalog.image(g,k) for g,k in catalog.VIEWS]+[catalog.base(g) for g in ('female','male')]
for url in paths:
 with Image.open(ROOT/url.lstrip('/')) as image:
  rgba=image.convert('RGBA');alpha=rgba.getchannel('A');assert image.size==(320,512),url
  assert alpha.getextrema()[0]==0,url
  # No baked studio walls: corners and outer columns must remain transparent.
  for point in ((0,0),(319,0),(0,511),(319,511),(2,240),(317,240)):assert alpha.getpixel(point)<10,(url,point)
  box=alpha.point(lambda a:255 if a>160 else 0).getbbox();assert box and 20<=box[1]<=65 and 490<=box[3]<=502,(url,box)
print('Fitting sprites:',len(paths),'valid 320x512 RGBA files, transparent borders and complete registered figures')
