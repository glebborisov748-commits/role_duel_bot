"""Export reusable artwork, leaving generated source PNGs intact.

Usage: python scripts/export_refresh_assets.py reactions.png models.png player-anime.png player-realism.png
This runs during asset preparation only. There are no runtime model calls.
"""
import sys
from export_avatar_presets import dimensions,crop,portraits

def main():
    for path,names,size,margin in (
        (sys.argv[1],['reaction_heart','reaction_star','reaction_flame','reaction_party'],'160:160',0),
        (sys.argv[2],['wardrobe_model_anime_male','wardrobe_model_anime_female','wardrobe_model_realism_male','wardrobe_model_realism_female'],'360:-1',2)):
        m=dimensions(path);w,h=m['width']//2,m['height']//2
        for i,name in enumerate(names):crop(path,i%2*w+margin,i//2*h+margin,w-2*margin,h-2*margin,name,size)
    portraits(sys.argv[3],'anime','player_avatar')
    portraits(sys.argv[4],'realism','player_avatar')

if __name__=='__main__':main()
