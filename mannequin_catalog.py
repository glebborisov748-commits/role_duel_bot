"""Generated fitting views for every wearable and supported mannequin gender."""
import json
from pathlib import Path

DATA=json.loads(Path(__file__).with_name('fitting_catalog.json').read_text())
VIEWS={(r['gender'],r['item']):r for r in DATA['rows'] if r['slot']!='base'}

def image(gender,key):
    if (gender,key) not in VIEWS:return None
    return f'/assets/fitting_catalog_{gender}_{key}.webp'

def base(gender):
    return f'/assets/fitting_catalog_{gender}___base__.webp'

def group(slots):
    if len(slots)>1 or 'body' in slots:return 'sets'
    slot=next(iter(slots),'body')
    return 'hats' if slot=='head' else 'accessories' if slot in ('face','neck','ears','wrist') else 'clothes'
