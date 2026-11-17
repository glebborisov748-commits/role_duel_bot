"""Lossless preset previews. Never paint arbitrary photographic pixels or paste body parts.

Presets illustrate hair silhouette and rendering style only. Selected pigment/race facts
are shown separately by the editor and applied to the explicitly generated portrait.
"""
import base64
from functools import lru_cache
from pathlib import Path
import character_options as options

HAIR={'brown':'#684039','black':'#23222e','blonde':'#e9c887','red':'#b65b39','silver':'#e3e2ec','pink':'#e5a1be','purple':'#b799d7','blue':'#4c628d'}
SKIN={'fair':'#f7dfd2','light':'#e9c7b2','olive':'#c4ab83','tan':'#bc8d6d','brown':'#956347','dark':'#654333'}
EYES={'brown':'#765644','blue':'#72adcd','green':'#83ad87','grey':'#9ca7b2','amber':'#c7a35f','violet':'#ac8dcd'}

@lru_cache(maxsize=64)
def base(world,gender,style,player=False):
    prefix='player_avatar' if player else 'avatar'
    path=Path(__file__).resolve().parent/'assets'/f'{prefix}_{world}_{gender}_{style}.webp'
    if not path.is_file():path=path.parent/f'portrait_{gender}.webp'
    return base64.b64encode(path.read_bytes()).decode()

def svg(raw,gender='female'):
    gender='male' if gender=='male' else 'female'
    values=options.validate(raw,gender)
    world='realism' if raw.get('world')=='realism' else 'anime'
    # Keep the complete generated image intact, including face, neck, eyes and hair.
    src='data:image/webp;base64,'+base(world,gender,values['hair_style'],raw.get('owner')=='player')
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 320 360"><image width="320" height="360" href="{src}"/></svg>'
