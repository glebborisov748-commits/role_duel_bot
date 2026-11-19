"""Mining shifts: choose a vein, manage gas, extract ore, haul out. Server owns all loot."""
import random,secrets,time
import mine_maze
RNG=random.SystemRandom()
ORES=[('coal','Уголь',18,55),('iron','Железо',45,28),('silver','Серебро',100,12),('gold','Золото',220,4.5),('crystal','Кристалл',480,.5)]
UPGRADE_COSTS=(600,1800,4500,9000)
class MineError(ValueError):pass

def new_veins(run):
 run['veins']=[];run['selected']=None
 for i in range(3):
  hardness=RNG.randint(2,4)+min(3,run['depth']//3);ore=RNG.choices(range(len(ORES)),weights=[x[3] for x in ORES])[0]
  run['veins'].append({'hardness':hardness,'left':hardness,'ore':ore,'gas':RNG.randint(10,22),'done':False})
 mine_maze.generate(run)

def start(user):
 if user.get('mine_run'):return
 if user.get('mine_ready_at',0)>time.time():raise MineError('Смена закончена. Перед новым спуском нужен короткий отдых.')
 run={'id':secrets.token_hex(12),'depth':1,'gas':0,'bag':[],'strikes':0,'last':0,'closed':False,'collapsed':False};new_veins(run);user['mine_run']=run

def snapshot(user):
 run=user.get('mine_run');rank=min(len(UPGRADE_COSTS),user.get('mine_rank',0))
 result={'rank':rank,'upgrade_price':UPGRADE_COSTS[rank] if rank<len(UPGRADE_COSTS) else None,'ready_in':max(0,int(user.get('mine_ready_at',0)-time.time())),
         'collection':dict(user.get('mine_collection',{})),'ores':[{'key':x[0],'name':x[1],'value':x[2],'chance':x[3]} for x in ORES],'run':None}
 if not run:return result
 result['run']={k:run[k] for k in ('id','depth','gas','strikes','closed','collapsed','selected')}
 result['run'].update(ready_ms=max(0,int((run['last']+(.15 if run.get('last_kind')=='move' else max(.25,.7-.08*rank))-time.time())*1000)),bag_value=sum(x['value'] for x in run['bag']),bag=list(run['bag']),veins=[{'hardness':v['hardness'],'left':v['left'],'gas':v['gas'],'done':v['done'],'ore':ORES[v['ore']][1]} for v in run['veins']])
 result['run']['maze']=mine_maze.snapshot(run,rank)
 return result

def action(user,body):
 kind=body.get('action')
 if kind=='start':start(user);return 0,0
 if kind=='upgrade':
  rank=user.get('mine_rank',0)
  if rank>=len(UPGRADE_COSTS):raise MineError('Кирка уже полностью улучшена')
  price=UPGRADE_COSTS[rank]
  if user.get('bucks',0)<price:raise MineError('Не хватает баксов')
  user['bucks']-=price;user['mine_rank']=rank+1;return 0,0
 run=user.get('mine_run')
 if not run or body.get('id')!=run['id']:raise MineError('Смена уже завершена или устарела')
 if kind=='haul':
  amount=sum(x['value'] for x in run['bag']);count=len(run['bag']);collection=user.setdefault('mine_collection',{})
  for ore in run['bag']:collection[ore['key']]=collection.get(ore['key'],0)+1
  user.pop('mine_run');user['mine_ready_at']=time.time()+60;return amount,count
 if run['closed']:raise MineError('Поднимись с оставшейся добычей')
 now=time.time();delay=.15 if kind=='move' else max(.25,.7-.08*user.get('mine_rank',0))
 if now-run['last']<delay:raise MineError('Дождись следующего удара')
 if kind=='vent':
  if not run['gas']:raise MineError('Воздух уже чистый')
  run['gas']=max(0,run['gas']-35);run['last']=now+1.0;return 0,0
 if kind=='descend':
  if not mine_maze.at_exit(run) and not any(v['done'] for v in run['veins']):raise MineError('Сначала добудь хотя бы одну жилу')
  if run['depth']>=10:raise MineError('Достигнут предел спуска — поднимай добычу')
  run['depth']+=1;run['gas']=min(100,run['gas']+8);run['last']=now;new_veins(run);return 0,0
 if kind in ('move','excavate'):
  mine_maze.action(run,body,user.get('mine_rank',0),ORES,MineError);run['last']=now;run['last_kind']=kind;return 0,0
 if kind!='strike':raise MineError('Неизвестное действие')
 index=body.get('vein')
 if type(index) is not int or index not in range(3):raise MineError('Выбери одну из трёх жил')
 vein=run['veins'][index]
 if vein['done']:raise MineError('Эта жила уже выработана')
 # Finishing a started tunnel before changing sides makes route choice meaningful.
 if run['selected'] is not None and run['selected']!=index and not run['veins'][run['selected']]['done']:raise MineError('Сначала закончи выбранный тоннель')
 run['selected']=index;run['last']=now;run['last_kind']='strike';run['strikes']+=1
 vein['left']=max(0,vein['left']-(1+user.get('mine_rank',0)//2));run['gas']=min(100,run['gas']+vein['gas'])
 if run['gas']>=100:
  run.update(closed=True,collapsed=True);run['bag']=run['bag'][::2];return 0,0
 if vein['left']==0:
  vein['done']=True;key,name,value,_=ORES[vein['ore']]
  run['bag'].append({'key':key,'name':name,'value':round(value*(1+.1*(run['depth']-1)))})
 if run['depth']>=10 and all(v['done'] for v in run['veins']):run['closed']=True
 return 0,0
