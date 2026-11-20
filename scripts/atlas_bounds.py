"""Find crop bounds of the principal atlas object, excluding neighbouring cells.
Only bounds are calculated; source pixels are never painted or recolored.
"""
from collections import deque

def dominant_bounds(im):
 a=im.convert('RGBA').getchannel('A');w,h=im.size;mask=bytearray(1 if v>150 else 0 for v in a.tobytes());components=[]
 for start in range(w*h):
  if not mask[start]:continue
  mask[start]=0;q=[start];count=0;x0=w;y0=h;x1=y1=0
  while q:
   i=q.pop();x=i%w;y=i//w;count+=1;x0=min(x0,x);x1=max(x1,x);y0=min(y0,y);y1=max(y1,y)
   for j in ((i-1 if x else -1),(i+1 if x+1<w else -1),i-w,i+w):
    if 0<=j<w*h and mask[j]:mask[j]=0;q.append(j)
  if count>8:components.append((count,x0,y0,x1+1,y1+1))
 if not components:raise ValueError('Empty asset')
 main=max(components);_,x0,y0,x1,y1=main
 for c in components:
  area,l,t,r,b=c;cy=(t+b)/2
  if area>=main[0]*.08 and y0<=cy<=y1 and abs((l+r-x0-x1)/2)<max(x1-x0,20)*2:
   x0=min(x0,l);x1=max(x1,r);y0=min(y0,t);y1=max(y1,b)
 pad=3
 return max(0,x0-pad),max(0,y0-pad),min(w,x1+pad),min(h,y1+pad)

def crop(im):return im.crop(dominant_bounds(im))
