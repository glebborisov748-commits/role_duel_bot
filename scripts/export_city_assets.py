"""Technical crop/scale export of generated city and road-hazard sheets."""
import argparse
from pathlib import Path
from PIL import Image
from atlas_bounds import crop
ROOT=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser();parser.add_argument('city',type=Path);parser.add_argument('hazards',type=Path);args=parser.parse_args()
names=['car_blue','car_gray','ped_blue','ped_rust','house_brick','house_shop','house_office','house_plum','light_red','light_amber','light_green','zebra','limit_30','limit_40','limit_50','stopline']
for path,size,keys in ((args.city,4,names),(args.hazards,2,['barrier','puddle','bump','pothole'])):
 im=Image.open(path).convert('RGBA');w,h=im.size
 for i,key in enumerate(keys):
  x,y=i%size,i//size;cell=im.crop((x*w//size,y*h//size,(x+1)*w//size,(y+1)*h//size))
  if key in ('zebra','stopline'):
   bounds=cell.getchannel('A').point(lambda a:255 if a>120 else 0).getbbox();cell=cell.crop(bounds) if bounds else cell
  else:cell=crop(cell)
  cell.thumbnail((256,256),Image.Resampling.LANCZOS);cell.save(ROOT/'assets'/f'city_{key}.webp',quality=90)
