"""Export equal-cell generated asset atlases; originals remain in generated_images."""
from pathlib import Path
from PIL import Image
root=Path(__file__).resolve().parents[1]
wardrobe=Image.open('/workspace/generated_images/exec-af187c37-ea52-4157-bc11-f96aaf218bb6.png')
keys=['bunny_outfit','latex_bodysuit','stockings','dress','heels','tracksuit','pajamas','collar','vibrator','shirt','trousers','hat','scarf','crop_top','oversized_shirt','denim_shorts','pencil_skirt','qipao','cap','cat_ears_headband','maid_outfit','nurse_outfit','lace_panties','collar_leash','garter_stockings','business_suit','sportswear','casual_outfit','leather_jacket','stripper_outfit','police_male','police_female','firefighter_male','firefighter_female','boxer_outfit','display_stand']
for i,key in enumerate(keys):
 x=i%6;y=i//6;w,h=wardrobe.size
 wardrobe.crop((round(x*w/6),round(y*h/6),round((x+1)*w/6),round((y+1)*h/6))).save(root/'assets'/('catalog_'+key+'.webp'),quality=90)
extras=Image.open('/workspace/generated_images/exec-b93b2e0a-3d52-4fe3-a3f4-647698468e73.png')
for i,key in enumerate(['photo_pack_1','photo_pack_5','photo_pack_15','energy_can','tailor_female','tailor_male']):
 x=i%3;y=i//3;w,h=extras.size
 extras.crop((round(x*w/3),round(y*h/2),round((x+1)*w/3),round((y+1)*h/2))).save(root/'assets'/(key+'.webp'),quality=90)
