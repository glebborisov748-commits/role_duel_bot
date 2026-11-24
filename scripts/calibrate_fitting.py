"""Measure technical mannequin anchors for accessory placement; no pixel editing."""
from pathlib import Path
import json
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
def anchors(path):
 im=Image.open(path).convert('RGBA');w,h=im.size;center=w//2;rows=[]
 for y in range(min(185,h)):
  xs=[]
  for x in range(center-44,center+45):
   r,g,b,a=im.getpixel((x,y))
   if a>190 and r>110 and 2<=r-g<=36 and 1<=g-b<=36 and 7<r-b<58:xs.append(x)
  rows.append(xs)
 starts=[y for y in range(len(rows)-6) if all(len(rows[j])>=7 for j in range(y,y+6))]
 if not starts:return dict(x=160,neck=76,head_scale=1,body_scale=1)
 top=starts[0];peak=max(len(v) for v in rows[top:top+28]);bottom=top+54
 for y in range(top+22,min(top+80,len(rows)-4)):
  if all(5<=len(rows[j])<peak*.7 for j in range(y,y+4)):
   bottom=y;break
 face=[x for row in rows[top:min(bottom,len(rows))] for x in row]
 cx=sum(face)/len(face) if face else center
 neck=max(59,min(153,bottom+9));head_scale=max(.7,min(1.25,peak/36));body_scale=(500-neck)/(500-76)
 return dict(x=round(cx,1),top=top,neck=round(neck,1),head_width=peak,head_scale=round(head_scale,3),body_scale=round(body_scale,3))
if __name__=='__main__':
 data={p.name:anchors(p) for p in list((ROOT/'assets').glob('body_view_*.webp'))+list((ROOT/'assets').glob('mannequin_base_*.webp'))+list((ROOT/'assets').glob('complete_clean_*.webp'))+list((ROOT/'assets').glob('nov23_*.webp'))+list((ROOT/'assets').glob('nov24_look_*.webp'))}
 (ROOT/'fitting_anchors.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
 print('Registered accessory anchors for',len(data),'complete mannequins.')
