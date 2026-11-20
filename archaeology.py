"""Server-owned archaeological expeditions and tool progression; no client payouts."""
from datetime import datetime,timedelta
import random,secrets,time
RNG=random.SystemRandom()
TOOLS={'brush':{'name':'Кисть','power':1,'damage':0},'shovel':{'name':'Лопатка','power':2,'damage':1},'pick':{'name':'Кирка','power':4,'damage':3}}
UPGRADES={'speed':'Быстрые руки','area':'Широкий захват','luck':'Чутьё археолога'}
LOOT=[('shard','Черепок',18),('coin','Старая монета',45),('amulet','Амулет',120),('relic','Редкий артефакт',320)]
COSTS=[500,1500,4000,9000]
class DigError(ValueError):pass

def start(user):
 run=user.get('dig_run')
 if run:return snapshot(user)
 if time.time()<user.get('dig_ready_at',0):raise DigError('Перед следующей экспедицией нужно отдохнуть: '+str(int(user['dig_ready_at']-time.time()))+' сек.')
 user['dig_run']={'id':secrets.token_hex(12),'depth':0,'bag':[],'damage':0,'actions':0,'last_action':0,'upgrades':{},'started':time.time(),'version':2,'width':9,'height':12}
 new_layer(user);return snapshot(user)

def new_layer(user):
 r=user['dig_run'];r['depth']+=1;r['choice']=None;r['collapse']=False;r['cells']=[]
 width=r.get('width',5);height=r.get('height',5);count=width*height;r.update(x=width//2,y=-1,target_loot=8 if r.get('version')==2 else 4)
 hidden=RNG.sample(range(width,count),r['target_loot']) if r.get('version')==2 else RNG.sample(range(count),4)
 for index in range(count):
  rarity=RNG.choices(range(4),weights=[60,28,10+r['depth'],2+r['upgrades'].get('luck',0)])[0]
  r['cells'].append({'earth':RNG.randint(2,4)+min(3,r['depth']//2),'loot':rarity if index in hidden else None,'found':False})

def probabilities(user):
 r=user.get('dig_run') or {'depth':1,'upgrades':{}};weights=[60,28,10+r['depth'],2+r['upgrades'].get('luck',0)];total=sum(weights)
 return [{'name':item[1],'chance':round(weight/total*100,2)} for item,weight in zip(LOOT,weights)]

def snapshot(user):
 r=user.get('dig_run');rank=min(4,int(user.get('dig_tool_rank',0)))
 delay=max(.2,.65-.1*(r or {}).get('upgrades',{}).get('speed',0)-.05*rank)
 meta={'ready_ms':max(0,int((((r or {}).get('last_action',0))+delay-time.time())*1000)),'tools':TOOLS,'rank':rank,'upgrade_price':COSTS[rank] if rank<len(COSTS) else None,'ready_in':max(0,int(user.get('dig_ready_at',0)-time.time())),'collection':dict(user.get('dig_collection',{})),'chances':probabilities(user)}
 if not r:return dict(meta,run=None)
 public={k:r[k] for k in ('id','depth','damage','actions','upgrades')}
 public.update(width=r.get('width',5),height=r.get('height',5),x=r.get('x',2),y=r.get('y',-1),version=r.get('version',1),bag_value=sum(v['value'] for v in r['bag']),bag=list(r['bag']),choice=r.get('choice'),collapse=r.get('collapse',False),
               cells=[{'earth':c['earth'],'found':c['found'],'loot':LOOT[c['loot']][1] if c['found'] and c['loot'] is not None else None,'glint':bool(c['loot'] is not None and c['earth']<=2 and abs(i%r.get('width',5)-r.get('x',2))+abs(i//r.get('width',5)-r.get('y',-1))<=2)} for i,c in enumerate(r['cells'])])
 return dict(meta,run=public)

def action(user,body):
 kind=body.get('action')
 if kind=='start':start(user);return 0
 if kind=='tool_upgrade':
  rank=user.get('dig_tool_rank',0)
  if rank>=len(COSTS):raise DigError('Инструменты уже улучшены')
  if user.get('bucks',0)<COSTS[rank]:raise DigError('Не хватает баксов')
  user['bucks']-=COSTS[rank];user['dig_tool_rank']=rank+1;return 0
 r=user.get('dig_run')
 if not r or body.get('id')!=r['id']:raise DigError('Экспедиция устарела. Обнови экран.')
 if kind=='cashout':
  payout=sum(v['value'] for v in r['bag']);collection=user.setdefault('dig_collection',{})
  for v in r['bag']:collection[v['key']]=collection.get(v['key'],0)+1
  user.pop('dig_run');user['dig_ready_at']=time.time()+60;return payout
 if kind=='upgrade':
  if r['depth']>=8:raise DigError('Экспедиция завершена. Забери добычу и возвращайся в новый заход.')
  option=body.get('upgrade')
  if option not in (r.get('choice') or []):raise DigError('Выбери одно из предложенных улучшений')
  r['upgrades'][option]=r['upgrades'].get(option,0)+1;new_layer(user);return 0
 if kind=='step':
  if r.get('choice'):raise DigError('Сначала выбери улучшение')
  directions={'left':(-1,0),'right':(1,0),'down':(0,1),'up':(0,-1)}
  if not isinstance(body.get('direction'),str) or body.get('direction') not in directions:raise DigError('Выбери направление')
  dx,dy=directions[body['direction']];width=r.get('width',5);height=r.get('height',5);x=r.get('x',width//2)+dx;y=r.get('y',-1)+dy
  if not 0<=x<width or not -1<=y<height:raise DigError('Край раскопа')
  if y==-1 or r['cells'][y*width+x]['earth']<=0:
   if time.time()-r.get('last_move',0)<.14:raise DigError('Дождись шага')
   r.update(x=x,y=y,last_move=time.time());return 0
  body={**body,'cell':y*width+x,'action':'dig'};kind='dig'
 if kind!='dig' or r.get('choice'):raise DigError('Сначала выбери улучшение')
 i=body.get('cell');tool=body.get('tool','brush')
 if type(i) is not int or i not in range(len(r['cells'])) or not isinstance(tool,str) or tool not in TOOLS:raise DigError('Неизвестная клетка или инструмент')
 delay=max(.2,.65-.1*r['upgrades'].get('speed',0)-.05*user.get('dig_tool_rank',0))
 if time.time()-r['last_action']<delay:raise DigError('Инструмент ещё в движении')
 cell=r['cells'][i]
 if r.get('version')==2:
  width=r['width'];distance=abs(i%width-r['x'])+abs(i//width-r['y'])
  if distance!=1:raise DigError('Копай рядом с персонажем')
 elif i>=5 and r['cells'][i-5]['earth']>0:raise DigError('Сначала сними грунт сверху — раскоп идёт послойно')
 if cell['earth']<=0:raise DigError('Здесь уже раскопано')
 r['last_action']=time.time();r['actions']+=1
 targets=[i]
 if r['upgrades'].get('area') and tool=='shovel':targets += [j for j in (i-1,i+1) if j in range(len(r['cells'])) and j//r.get('width',5)==i//r.get('width',5)]
 for j in targets:
  c=r['cells'][j]
  if c['earth']<=0:continue
  power=TOOLS[tool]['power']+user.get('dig_tool_rank',0)//2
  c['earth']=max(0,c['earth']-power)
  if c['earth']==0 and c['loot'] is not None and not c['found']:
   key,name,base=LOOT[c['loot']];damage=TOOLS[tool]['damage'];condition=max(.3,1-.2*damage)
   c['found']=True;r['bag'].append({'key':key,'name':name,'value':round(base*condition*(1+.12*(r['depth']-1))),'condition':round(condition*100)})
   if damage:r['damage']+=damage
 if r.get('version')==2 and r['cells'][i]['earth']==0:r.update(x=i%r['width'],y=i//r['width'])
 if r['damage']>=8:
  # A collapse loses half this expedition's loot, never owned currency or tools.
  r['bag']=r['bag'][::2];r['damage']=0;r['collapse']=True;r['choice']=list(UPGRADES)
 elif all(c['earth']==0 for c in r['cells']) or sum(c['found'] for c in r['cells'])>=r.get('target_loot',4):
  r['choice']=list(UPGRADES) if r['depth']<8 else ['cashout']
 return 0
