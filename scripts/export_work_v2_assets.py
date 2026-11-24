"""Technical cropping/scaling only: generated three-icon sheet to transparent WebP assets."""
from pathlib import Path
import argparse
from PIL import Image
from atlas_bounds import crop
ROOT=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser();parser.add_argument('atlas',type=Path);args=parser.parse_args()
im=Image.open(args.atlas).convert('RGBA');w,h=im.size
for i,key in enumerate(('basket','freeze','wide')):
 cell=crop(im.crop((i*w//3,0,(i+1)*w//3,h)))
 cell.thumbnail((232,232),Image.Resampling.LANCZOS)
 frame=Image.new('RGBA',(256,256));frame.alpha_composite(cell,((256-cell.width)//2,(256-cell.height)//2));frame.save(ROOT/'assets'/f'work_{key}_v2.webp',quality=92)
