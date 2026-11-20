"""Asset crop regressions: neighbours outside a product and inside full-body frames."""
import sys
from pathlib import Path
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from atlas_bounds import dominant_bounds
im=Image.new('RGBA',(120,140));d=ImageDraw.Draw(im);d.rectangle((25,50,95,130),fill='purple');d.rectangle((0,0,119,8),fill='blue')
assert dominant_bounds(im)[1]>=45,'Neighbour strip was included in the product crop'
for key in ('beanie','beret','cardigan','bomber_jacket','sneakers','ankle_boots','pendant'):
 im=Image.open(ROOT/'assets'/('clean_catalog_'+key+'.webp')).convert('RGBA');bounds=dominant_bounds(im)
 assert bounds[1]<=4,(key,bounds,im.size)
for path in list((ROOT/'assets').glob('body_view_*.webp'))+list((ROOT/'assets').glob('complete_clean_*.webp')):
 im=Image.open(path).convert('RGBA');assert im.size==(320,512),(path,im.size)
 assert max(im.getchannel('A').crop((0,504,320,512)).getdata())<150,(path,'neighbour below mannequin')
print('Product neighbour strips excluded; complete mannequins remain within a shared 320x512 frame.')
