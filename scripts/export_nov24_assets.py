"""Crop and register whole generated mannequins and the calendar icon."""
import sys
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(Path(__file__).resolve().parent))
from export_fitting_assets import cells
from export_complete_looks import register
atlas=ROOT.parent/'generated_images/exec-58e44d8e-9817-48ff-83f0-af78c3b8145c.png'
for i,cell in enumerate(cells(atlas,4)):
    register(cell).save(ROOT/'assets'/f'nov24_look_{i}.webp',quality=92)
icon=Image.open(ROOT.parent/'generated_images/exec-d1a6c340-379a-4d25-b64d-9f77599e9eb0.png').convert('RGBA')
icon.thumbnail((192,192),Image.Resampling.LANCZOS)
icon.save(ROOT/'assets/offer_calendar_nov24.webp',quality=92)
