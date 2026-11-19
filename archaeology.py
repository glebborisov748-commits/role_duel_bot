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
 user['dig_run']={'id':secrets.token_hex(12),'depth':0,'bag':[],'damage':0,'actions':0,'last_action':0,'upgrades':{},'started':time.time()}
 new_layer(user);return snapshot(user)

def new_layer(user):
 r=user['dig_run'];r['depth']+=1;r['choice']=None;r['collapse']=False;r['cells']=[]
 hidden=RNG.sample(range(25),4)
 for index in range(25):
  rarity=RNG.choices(range(4),weights=[60,28,10+r['depth'],2+r['upgrades'].get('luck',0)])[0]
  r['cells'].append({'earth':RNG.randint(2,4)+min(3,r['depth']//2),'loot':rarity if index in hidden else None,'found':False})

def probabilities(user):
 r=user.get('dig_run') or {'depth':1,'upgrades':{}};weights=[60,28,10+r['depth'],2+r['upgrades'].get('luck',0)];total=sum(weights)
 return [{'name':item[1],'chance':round(weight/total*100,2)} for item,weight in zip(LOOT,weights)]

def snapshot(user):
 r=user.get('dig_run');rank=min(4,int(user.get('dig_tool_rank',0)))
 meta={'tools':TOOLS,'rank':rank,'upgrade_price':COSTS[rank] if rank<len(COSTS) else None,'ready_in':max(0,int(user.get('dig_ready_at',0)-time.time())),'collection':dict(user.get('dig_collection',{})),'chances':probabilities(user)}
 if not r:return dict(meta,run=None)
 public={k:r[k] for k in ('id','depth','damage','actions','upgrades')}
 public.update(bag_value=sum(v['value'] for v in r['bag']),bag=list(r['bag']),choice=r.get('choice'),collapse=r.get('collapse',False),
               cells=[{'earth':c['earth'],'found':c['found'],'loot':LOOT[c['loot']][1] if c['found'] and c['loot'] is not None else None} for c in r['cells']])
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
 if kind!='dig' or r.get('choice'):raise DigError('Сначала выбери улучшение')
 i=body.get('cell');tool=body.get('tool','brush')
 if type(i) is not int or i not in range(25) or tool not in TOOLS:raise DigError('Неизвестная клетка или инструмент')
 delay=max(.2,.65-.1*r['upgrades'].get('speed',0)-.05*user.get('dig_tool_rank',0))
 if time.time()-r['last_action']<delay:raise DigError('Инструмент ещё в движении')
 cell=r['cells'][i]
 if i>=5 and r['cells'][i-5]['earth']>0:raise DigError('Сначала сними грунт сверху — раскоп идёт послойно')
 if cell['earth']<=0:raise DigError('Здесь уже раскопано')
 r['last_action']=time.time();r['actions']+=1
 targets=[i]
 if r['upgrades'].get('area') and tool=='shovel':targets += [j for j in (i-1,i+1) if j in range(25) and j//5==i//5]
 for j in targets:
  c=r['cells'][j]
  if c['earth']<=0:continue
  power=TOOLS[tool]['power']+user.get('dig_tool_rank',0)//2
  c['earth']=max(0,c['earth']-power)
  if c['earth']==0 and c['loot'] is not None and not c['found']:
   key,name,base=LOOT[c['loot']];damage=TOOLS[tool]['damage'];condition=max(.3,1-.2*damage)
   c['found']=True;r['bag'].append({'key':key,'name':name,'value':round(base*condition*(1+.12*(r['depth']-1))),'condition':round(condition*100)})
   if damage:r['damage']+=damage
 if r['damage']>=8:
  # A collapse loses half this expedition's loot, never owned currency or tools.
  r['bag']=r['bag'][::2];r['damage']=0;r['collapse']=True;r['choice']=list(UPGRADES)
 elif all(c['earth']==0 for c in r['cells']) or sum(c['found'] for c in r['cells'])>=4:
  r['choice']=list(UPGRADES) if r['depth']<8 else ['cashout']
 return 0
