"""Technical atlas export: crop and register generated source artwork, never repaint it."""
import sys
from pathlib import Path
from PIL import Image
from atlas_bounds import dominant_bounds
source=Image.open(sys.argv[1]).convert('RGBA');out=Path(__file__).resolve().parents[1]/'assets'
keys=('starter_female','starter_male','police_female','police_male','denim_female','denim_male','tshirt_female','tshirt_male')
for i,key in enumerate(keys):
 col=i%4;row=i//4;w,h=source.size
 tile=source.crop((round(col*w/4),round(row*h/2),round((col+1)*w/4),round((row+1)*h/2)))
 tile=tile.crop(dominant_bounds(tile));tile.thumbnail((280,488),Image.Resampling.LANCZOS)
 canvas=Image.new('RGBA',(320,512));canvas.alpha_composite(tile,((320-tile.width)//2,500-tile.height));canvas.save(out/('nov23_'+key+'.webp'),quality=92)
