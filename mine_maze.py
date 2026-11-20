"""Server-owned textured mine world and directional, wall-occluded flashlight."""
import math,random
RNG=random.SystemRandom();SIZE=15
DIRECTIONS={'up':(0,-1),'down':(0,1),'left':(-1,0),'right':(1,0)}
def size(m):return m.get('size') or math.isqrt(len(m['cells']))
def generate(run):
 cells=[{'wall':True,'ore':None,'left':0} for _ in range(SIZE*SIZE)];stack=[(1,1)];cells[SIZE+1]['wall']=False
 while stack:
  x,y=stack[-1];options=[]
  for dx,dy in DIRECTIONS.values():
   nx,ny=x+dx*2,y+dy*2
   if 0<nx<SIZE-1 and 0<ny<SIZE-1 and cells[ny*SIZE+nx]['wall']:options.append((nx,ny,dx,dy))
  if not options:stack.pop();continue
  nx,ny,dx,dy=RNG.choice(options);cells[(y+dy)*SIZE+x+dx]['wall']=False;cells[ny*SIZE+nx]['wall']=False;stack.append((nx,ny))
 available=[i for i,c in enumerate(cells) if not c['wall'] and i not in (SIZE+1,(SIZE-2)*SIZE+SIZE-2)]
 for i in RNG.sample(available,min(20,len(available))):cells[i]['ore']=RNG.choices(range(5),weights=[55,28,12,4.5,.5])[0];cells[i]['left']=RNG.randint(2,5)
 run['maze']={'size':SIZE,'cells':cells,'x':1,'y':1,'seen':[],'collected':0,'angle':90,'light_version':2}
def aim(run,angle,error):
 if isinstance(angle,bool) or not isinstance(angle,(int,float)) or not math.isfinite(angle):raise error('Некорректное направление фонаря')
 if 'maze' not in run:generate(run)
 run['maze']['angle']=float(angle)%360

def visible(m,rank):
 n=size(m);result={m['y']*n+m['x']};direction=math.radians(m.get('angle',90));reach=4.5+min(2,rank)*.5
 for y in range(max(0,m['y']-6),min(n,m['y']+7)):
  for x in range(max(0,m['x']-6),min(n,m['x']+7)):
   dx=x-m['x'];dy=y-m['y'];dist=math.hypot(dx,dy)
   if not dist or dist>reach:continue
   diff=(math.atan2(dy,dx)-direction+math.pi)%(2*math.pi)-math.pi
   if abs(diff)>.4:continue
   blocked=False;steps=max(1,int(dist*12))
   for k in range(1,steps):
    xx=math.floor(m['x']+.5+dx*k/steps);yy=math.floor(m['y']+.5+dy*k/steps)
    if (xx,yy)!=(x,y) and m['cells'][yy*n+xx]['wall']:blocked=True;break
   if not blocked:result.add(y*n+x)
 return result

def snapshot(run,rank):
 if 'maze' not in run:generate(run)
 m=run['maze'];n=size(m)
 if m.get('light_version')!=2:m.update(seen=[],angle=90,light_version=2)
 lit=visible(m,rank);seen=set(m['seen'])|lit;m['seen']=sorted(seen)
 return {'size':n,'x':m['x'],'y':m['y'],'angle':m.get('angle',90),'beam_degrees':46,'exit':(n-2)*n+n-2,'collected':m['collected'],
  'cells':[None if i not in seen else {'wall':c['wall'],'ore':c['ore'] if i in lit else None,'left':c['left'] if i in lit else None,'lit':i in lit} for i,c in enumerate(m['cells'])]}
def at_exit(run):
 m=run.get('maze') or {}
 return bool(m) and m.get('x')==size(m)-2 and m.get('y')==size(m)-2 and m.get('collected',0)>0

def action(run,body,rank,ores,error):
 if 'maze' not in run:generate(run)
 m=run['maze'];n=size(m);kind=body['action']
 if kind=='move':
  direction=body.get('direction')
  if not isinstance(direction,str) or direction not in DIRECTIONS:raise error('Выбери направление')
  dx,dy=DIRECTIONS[direction];nx,ny=m['x']+dx,m['y']+dy
  if not 0<=nx<n or not 0<=ny<n or m['cells'][ny*n+nx]['wall']:raise error('Здесь сплошная порода')
  m.update(x=nx,y=ny);run['gas']=min(100,run['gas']+1)
 else:
  cell=m['cells'][m['y']*n+m['x']]
  if cell['ore'] is None:raise error('Здесь нет руды. Осмотри тоннели с фонарём.')
  cell['left']=max(0,cell['left']-(1+rank//2));run['strikes']+=1;run['gas']=min(100,run['gas']+10)
  if cell['left']==0:
   key,name,value,_=ores[cell['ore']];run['bag'].append({'key':key,'name':name,'value':round(value*(1+.1*(run['depth']-1)))});cell['ore']=None;m['collected']+=1
 if run['gas']>=100:run.update(closed=True,collapsed=True);run['bag']=run['bag'][::2]
