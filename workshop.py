"""Random, solvable pipe rotation jobs with server-checked single-use rewards."""
import secrets
import time
import random

N,E,S,W=1,2,4,8
DIRECTIONS=((0,-1,N,S),(1,0,E,W),(0,1,S,N),(-1,0,W,E))

def mask(kind,rotation):
 base=5 if kind=='straight' else 3
 return ((base<<rotation)|(base>>(4-rotation)))&15

def connected(job,rotations):
 cells=job['cells'];size=job['size']
 if not isinstance(rotations,list) or len(rotations)!=len(cells) or any(type(r) is not int or not 0<=r<4 for r in rotations):return False
 pos=job['source'];end=job['sink'];entry=W;seen=set()
 while pos not in seen:
  seen.add(pos);ports=mask(cells[pos]['kind'],rotations[pos])
  if not ports&entry:return False
  exit_port=ports^entry
  if pos==end and exit_port==E:return True
  direction=next((d for d in DIRECTIONS if d[2]==exit_port),None)
  if not direction:return False
  x,y=pos%size,pos//size;nx,ny=x+direction[0],y+direction[1]
  if not(0<=nx<size and 0<=ny<size):return False
  pos=ny*size+nx;entry=direction[3]
 return False

def make_path(size,source,sink,minimum,maximum):
 # Bounded randomized DFS gives a varied path, without an unbounded generation loop.
 visits=0;path=[source];seen={source}
 def visit(pos):
  nonlocal visits
  visits+=1
  if pos==sink:return len(path)>=minimum
  if len(path)>=maximum or visits>5000:return False
  neighbors=[];x,y=pos%size,pos//size
  for dx,dy,*_ in DIRECTIONS:
   nx,ny=x+dx,y+dy
   if 0<=nx<size and 0<=ny<size and ny*size+nx not in seen:neighbors.append(ny*size+nx)
  random.shuffle(neighbors)
  for nxt in neighbors:
   seen.add(nxt);path.append(nxt)
   if visit(nxt):return True
   seen.remove(nxt);path.pop()
  return False
 if visit(source):return path
 # Safe fallback remains a valid route even at the search budget limit.
 x,y=source%size,source//size;target_y=sink//size;path=[source]
 while y!=target_y:y+=1 if y<target_y else -1;path.append(y*size+x)
 while x<size-1:x+=1;path.append(y*size+x)
 return path

def start(user,now=None):
 now=time.time() if now is None else now
 job=user.get('pipe_job')
 if job and 0<=now-job['started']<1200:return job
 completed=max(0,int(user.get('pipe_completed',0)));size=min(6,4+completed//3)
 source=random.randrange(size)*size;sink=random.randrange(size)*size+size-1
 path=make_path(size,source,sink,size+2,min(size*size,size+6+min(14,completed//2)))
 cells=[{'kind':random.choice(('straight','elbow')),'rotation':random.randrange(4)} for _ in range(size*size)]
 solution=[c['rotation'] for c in cells]
 for i,pos in enumerate(path):
  neighbors=[path[i-1] if i else pos-1,path[i+1] if i+1<len(path) else pos+1];required=0
  for neighbor in neighbors:
   delta=neighbor-pos
   required|=E if delta==1 else W if delta==-1 else S if delta==size else N
  kind='straight' if required in (5,10) else 'elbow';cells[pos]['kind']=kind
  solution[pos]=next(r for r in range(4) if mask(kind,r)==required)
 job={'id':secrets.token_hex(12),'size':size,'source':source,'sink':sink,'cells':cells,'solution':solution,'started':now,'level':completed+1}
 if connected(job,[c['rotation'] for c in cells]):cells[source]['rotation']=(solution[source]+1)%4
 user['pipe_job']=job
 return job

def public(job):return {k:job[k] for k in ('id','size','source','sink','cells','level')}

def complete(user,job_id,values,now=None):
 now=time.time() if now is None else now;job=user.get('pipe_job')
 if not job or job.get('id')!=job_id or not 4<=now-job['started']<=1200:return False
 if not connected(job,values):return False
 user.pop('pipe_job',None);user['pipe_completed']=user.get('pipe_completed',0)+1
 return True
