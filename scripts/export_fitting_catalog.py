"""Crop/register generated atlas figures; no repainting or clothing compositing.
Usage: python scripts/export_fitting_catalog.py [--source-dir /workspace/generated_images]
Atlas order and source filenames live in fitting_catalog.json.
"""
import argparse,json,sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(Path(__file__).resolve().parent))
from calibrate_fitting import anchors

def register(im):
    alpha=im.getchannel('A').point(lambda v:255 if v>155 else 0)
    box=alpha.getbbox()
    if not box:raise ValueError('Empty atlas cell')
    im=im.crop(box);im.thumbnail((264,474),Image.Resampling.LANCZOS)
    canvas=Image.new('RGBA',(320,512));canvas.alpha_composite(im,((320-im.width)//2,500-im.height))
    return canvas

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--source-dir',type=Path,default=ROOT.parent/'generated_images');parser.add_argument('--force-sheet',type=int);args=parser.parse_args()
    data=json.loads((ROOT/'fitting_catalog.json').read_text());out=ROOT/'assets';exported={};jobs=[]
    for sheet,filename in sorted(data['atlases'].items(),key=lambda p:int(p[0])):
        atlas=Image.open(args.source_dir/filename).convert('RGBA');w,h=atlas.size
        for n,row in enumerate(data['rows'][int(sheet)*8:int(sheet)*8+8]):
            cell=atlas.crop((round(n%4*w/4),round(n//4*h/2),round((n%4+1)*w/4),round((n//4+1)*h/2)))
            name=f"fitting_catalog_{row['gender']}_{row['item']}.webp"
            if cell.getchannel('A').getextrema()[0]>=20:raise ValueError(f'Atlas {sheet}, cell {n} has an opaque backdrop')
            jobs.append((name,cell,args.force_sheet==int(sheet)))
    def export(job):
        name,cell,force=job;path=out/name
        if force or not path.exists() or path.stat().st_size<128:
            temp=path.with_suffix('.tmp.webp');register(cell).save(temp,quality=92,method=4);temp.replace(path)
        return name,anchors(path)
    with ThreadPoolExecutor(max_workers=4) as pool:
        exported.update(pool.map(export,jobs))
    anchor_path=ROOT/'fitting_anchors.json';all_anchors=json.loads(anchor_path.read_text());all_anchors.update(exported)
    anchor_path.write_text(json.dumps(all_anchors,ensure_ascii=False,indent=2)+'\n')
    print('Registered',len(exported),'complete mannequin views')
if __name__=='__main__':main()
