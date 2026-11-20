"""Technical atlas export: one whole generated mannequin per immutable preview."""
import argparse,sys
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT));sys.path.insert(0,str(Path(__file__).resolve().parent))
from export_fitting_assets import cells
from atlas_bounds import crop as crop_object

def register(im):
 crop_image=crop_object(im)
 crop=crop_image
 scale=min(280/crop.width,488/crop.height);crop=crop.resize((round(crop.width*scale),round(crop.height*scale)),Image.Resampling.LANCZOS)
 frame=Image.new('RGBA',(320,512));frame.alpha_composite(crop,((320-crop.width)//2,500-crop.height));return frame

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--female',required=True);ap.add_argument('--male',required=True);ap.add_argument('--extra',required=True);args=ap.parse_args()
 for group,path in vars(args).items():
  for i,im in enumerate(cells(path,4)):register(im).save(ROOT/'assets'/f'complete_clean_{group}_{i}.webp',quality=92)
 print('Exported 48 complete generated outfit-and-accessory previews.')
if __name__=='__main__':main()
