"""Server-owned dark tunnels; clients only receive discovered terrain."""
import random
RNG=random.SystemRandom()
SIZE=9
DIRECTIONS={'up':(0,-1),'down':(0,1),'left':(-1,0),'right':(1,0)}
def generate(run):
 cells=[{'wall':True,'ore':None,'left':0} for _ in range(SIZE*SIZE)]
 stack=[(1,1)];cells[SIZE+1]['wall']=False
 while stack:
  x,y=stack[-1];options=[]
  for dx,dy in DIRECTIONS.values():
   nx,ny=x+dx*2,y+dy*2
   if 0<nx<SIZE-1 and 0<ny<SIZE-1 and cells[ny*SIZE+nx]['wall']:options.append((nx,ny,dx,dy))
  if not options:stack.pop();continue
  nx,ny,dx,dy=RNG.choice(options);cells[(y+dy)*SIZE+x+dx]['wall']=False;cells[ny*SIZE+nx]['wall']=False;stack.append((nx,ny))
 available=[i for i,c in enumerate(cells) if not c['wall'] and i not in (SIZE+1,(SIZE-2)*SIZE+SIZE-2)]
 for i in RNG.sample(available,min(10,len(available))):
  cells[i]['ore']=RNG.choices(range(5),weights=[55,28,12,4.5,.5])[0];cells[i]['left']=RNG.randint(2,5)
 run['maze']={'cells':cells,'x':1,'y':1,'seen':[],'collected':0}

def snapshot(run,rank):
 if 'maze' not in run:generate(run)
 m=run['maze'];radius=2+(1 if rank>=2 else 0);seen=set(m['seen']);visible=set()
 for y in range(SIZE):
  for x in range(SIZE):
   if abs(x-m['x'])+abs(y-m['y'])<=radius:visible.add(y*SIZE+x)
 seen|=visible;m['seen']=sorted(seen)
 return {'size':SIZE,'x':m['x'],'y':m['y'],'exit':(SIZE-2)*SIZE+SIZE-2,'collected':m['collected'],
         'cells':[None if i not in seen else {'wall':c['wall'],'ore':c['ore'] if i in visible else None,'left':c['left'] if i in visible else None,'lit':i in visible} for i,c in enumerate(m['cells'])]}

def at_exit(run):
 m=run.get('maze') or {};return m.get('x')==SIZE-2 and m.get('y')==SIZE-2 and m.get('collected',0)>0

def action(run,body,rank,ores,error):
 if 'maze' not in run:generate(run)
 m=run['maze'];kind=body['action']
 if kind=='move':
  direction=body.get('direction')
  if direction not in DIRECTIONS:raise error('Выбери направление')
  dx,dy=DIRECTIONS[direction];nx,ny=m['x']+dx,m['y']+dy
  if not 0<=nx<SIZE or not 0<=ny<SIZE or m['cells'][ny*SIZE+nx]['wall']:raise error('Здесь сплошная порода')
  m.update(x=nx,y=ny);run['gas']=min(100,run['gas']+1)
 else:
  cell=m['cells'][m['y']*SIZE+m['x']]
  if cell['ore'] is None:raise error('Здесь нет руды. Осмотри тоннели с фонарём.')
  cell['left']=max(0,cell['left']-(1+rank//2));run['strikes']+=1;run['gas']=min(100,run['gas']+10)
  if cell['left']==0:
   key,name,value,_=ores[cell['ore']];run['bag'].append({'key':key,'name':name,'value':round(value*(1+.1*(run['depth']-1)))});cell['ore']=None;m['collected']+=1
 if run['gas']>=100:run.update(closed=True,collapsed=True);run['bag']=run['bag'][::2]
