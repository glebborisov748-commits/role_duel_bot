"""Export the generated repair atlases. Creative artwork is supplied, never painted here.
Usage: python scripts/export_game_wardrobe_assets.py --bodies first.png second.png third.png --games game.png --gestures hands.png
"""
import argparse,sys,shutil
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import profile_options
from export_fitting_assets import cells
from export_complete_looks import register
from atlas_bounds import crop

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--bodies',nargs=3,required=True);parser.add_argument('--games',required=True);parser.add_argument('--gestures',required=True);args=parser.parse_args();out=ROOT/'assets'
 keys=[k for k,v in profile_options.WARDROBE.items() if v.get('slot')=='body' and k!='male_latex_catsuit']
 groups=[keys[:16],keys[16:32],keys[32:39]+['tracksuit_male','pajamas_male','mix_tshirt','mix_sweater','mix_hoodie','mix_linen','mix_cardigan','mix_bomber','mix_robe']]
 for group,path in zip(groups,args.bodies):
  for key,im in zip(group,cells(path,4)):
   register(im).save(out/f'body_view_{key}.webp',quality=92)
   if key in ('female_wetlook_catsuit','male_wetlook_catsuit'):crop(im).save(out/f'clean_catalog_{key}.webp',quality=92)
 shutil.copyfile(out/'body_view_male_leather_bodysuit.webp',out/'body_view_male_latex_catsuit.webp')
 names=('ore_coal','ore_gold','ore_diamond','ore_copper','mine_floor','mine_wall','mine_player','mine_exit','dig_stand','dig_pick','dig_brush','dig_relic','dig_soil','dig_rock','dig_coin','dig_vase')
 for key,im in zip(names,cells(args.games,4)):crop(im).save(out/(key+'.webp'),quality=92)
 for key in ('mine_floor','mine_wall','dig_soil','dig_rock'):
  im=Image.open(out/(key+'.webp'));w,h=im.size;im.crop((round(w*.18),round(h*.22),round(w*.82),round(h*.82))).save(out/(key+'_texture.webp'),quality=92)
 im=Image.open(args.gestures).convert('RGBA')
 for i,key in enumerate(('gesture_pull','gesture_swipe')):crop(im.crop((i*im.width//2,0,(i+1)*im.width//2,im.height))).save(out/(key+'.webp'),quality=92)
 print('Exported whole wardrobe views, mining/excavation textures and gesture instructions.')
if __name__=='__main__':main()
