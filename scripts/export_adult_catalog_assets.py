"""Split two generated 4x4 shop sheets. No network or generation at runtime.

Usage: python scripts/export_adult_catalog_assets.py --first /path/a.png --second /path/b.png
Original sheets remain untouched. Order matches ADULT_CATALOG_ITEMS insertion order.
"""
import argparse
import sys
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from profile_options import ADULT_CATALOG_ITEMS

def export(first,second):
 keys=list(ADULT_CATALOG_ITEMS)
 if len(keys)!=32:raise ValueError('Expected 32 catalog items for two 4x4 sheets')
 for offset,source in ((0,first),(16,second)):
  with Image.open(source) as original:
   atlas=original.convert('RGBA');width,height=atlas.size
   for index,key in enumerate(keys[offset:offset+16]):
    x=index%4;y=index//4
    tile=atlas.crop((round(x*width/4),round(y*height/4),round((x+1)*width/4),round((y+1)*height/4)))
    tile.save(ROOT/'assets'/('catalog_'+key+'.webp'),quality=92,method=6)
 return keys

if __name__=='__main__':
 parser=argparse.ArgumentParser(description=__doc__)
 parser.add_argument('--first',type=Path,required=True);parser.add_argument('--second',type=Path,required=True)
 args=parser.parse_args();keys=export(args.first,args.second)
 print('Exported',len(keys),'transparent shop icons')
