"""Export generated atlases into a common 320x512 fitting coordinate frame.
No provider calls, repainting or recoloring. All layer positions are stable slot anchors.
"""
import argparse,sys
from pathlib import Path
from PIL import Image
from atlas_bounds import crop
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import profile_options as wardrobe

def cells(path,n):
 im=Image.open(path).convert('RGBA');w,h=im.size
 for i in range(n*n):yield im.crop((round(i%n*w/n)+2,round(i//n*h/n)+2,round((i%n+1)*w/n)-2,round((i//n+1)*h/n)-2))
def placed(im,box):
 im=crop(im);x,y,w,h=box;scale=min(w/im.width,h/im.height);im=im.resize((round(im.width*scale),round(im.height*scale)),Image.Resampling.LANCZOS)
 frame=Image.new('RGBA',(320,512));frame.alpha_composite(im,(round(x+(w-im.width)/2),round(y+(h-im.height)/2)));return frame

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--mannequins',required=True);ap.add_argument('--ordinary',required=True);ap.add_argument('--avatars',required=True);ap.add_argument('--accessories',required=True);args=ap.parse_args();out=ROOT/'assets'
 for i,im in enumerate(cells(args.mannequins,4)):
  canvas=Image.new('RGBA',(320,512));canvas.alpha_composite(im.resize((320,512),Image.Resampling.LANCZOS),(-17,0));canvas.save(out/f'fitting_v2_{i}.webp',quality=91)
 for item,im in zip(wardrobe.ORDINARY_ITEMS,cells(args.ordinary,4)):
  if item[0]=='pendant':im=im.crop((0,45,im.width,im.height))
  if item[0]=='sunglasses':im=im.crop((0,30,im.width,im.height))
  crop(im).save(out/f'clean_catalog_{item[0]}.webp',quality=90)
 for item,im in zip(wardrobe.ACCESSORY_ITEMS,cells(args.accessories,4)):
  crop(im).save(out/f'clean_catalog_{item[0]}.webp',quality=92)
 for key,im in zip(('male_1','male_2','female_1','female_2'),cells(args.avatars,2)):
  im.resize((256,256),Image.Resampling.LANCZOS).save(out/f'default_avatar_{key}.webp',quality=90)
 anchors={'body':(74,100,172,382),'top':(60,102,200,160),'bottom':(90,240,140,237),'legs':(96,256,128,228),'outerwear':(48,100,224,270),'shoes':(101,464,118,42),'head':(106,2,108,80),'face':(124,50,72,24),'neck':(125,84,70,60),'ears':(139,48,42,16),'wrist':(103,230,15,23)}
 special={'pendant':(140,78,40,44),'scarf':(125,77,70,130),'collar_leash':(142,74,36,20),'cat_ears_headband':(128,0,64,46),'cap':(126,5,68,35),'beanie':(134,2,52,36),'beret':(125,4,70,31),'hat':(122,0,76,43),'sunglasses':(142,40,36,15),'round_glasses':(141,39,38,16),'aviator_glasses':(140,39,40,16),'pearl_necklace':(140,78,40,28),'silver_chain':(140,78,40,39),'velvet_choker':(146,75,28,13),'silk_neckerchief':(136,78,48,55),'bow_tie':(143,81,34,16),'ribbon':(145,12,30,23),'flower_clip':(169,24,17,21),'crown':(135,3,50,27),'plain_headband':(138,12,44,26)}
 for key,item in wardrobe.WARDROBE.items():
  if not item.get('slot') or item['slot']=='body':continue
  path=out/(item['image']+'.webp')
  if not path.is_file():raise FileNotFoundError(path)
  im=Image.open(path).convert('RGBA');placed(im,special.get(key,anchors[item['slot']])).save(out/f'layer_v2_{key}.webp',quality=90)
 print('Exported 16 fixed-frame mannequins, 16 ordinary icons, four avatars and all wearable layers.')
if __name__=='__main__':main()
