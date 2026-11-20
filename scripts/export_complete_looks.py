"""Technical atlas export: one whole generated mannequin per immutable preview."""
import argparse,sys
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT));sys.path.insert(0,str(Path(__file__).resolve().parent))
from export_fitting_assets import cells

def register(im):
 # Find silhouette bounds with substantial alpha occupancy, ignoring isolated edge specks.
 a=im.getchannel('A');w,h=im.size
 rows=[y for y in range(h) if sum(a.getpixel((x,y))>200 for x in range(w))>12]
 if not rows:raise ValueError('Missing mannequin')
 y0,y1=rows[0],rows[-1]+1
 xs=[x for x in range(w) if sum(a.getpixel((x,y))>200 for y in range(y0,y1))>12]
 crop=im.crop((max(0,min(xs)-4),max(0,y0-4),min(w,max(xs)+5),min(h,y1+4)))
 scale=min(280/crop.width,488/crop.height);crop=crop.resize((round(crop.width*scale),round(crop.height*scale)),Image.Resampling.LANCZOS)
 frame=Image.new('RGBA',(320,512));frame.alpha_composite(crop,((320-crop.width)//2,500-crop.height));return frame

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--female',required=True);ap.add_argument('--male',required=True);ap.add_argument('--extra',required=True);args=ap.parse_args()
 for group,path in vars(args).items():
  for i,im in enumerate(cells(path,4)):register(im).save(ROOT/'assets'/f'complete_{group}_{i}.webp',quality=92)
 print('Exported 48 complete generated outfit-and-accessory previews.')
if __name__=='__main__':main()
