"""Four-lane courier: server-owned motion, traffic, hazards and delivery rewards."""
import math
import random
import secrets
import time

MAX_SPEED=60
STEP_CAP=.6
STOP_OFFSET=8
TIPS=((400,.01),(160,.03),(70,.08))
SCENARIOS=('red','green','pedestrians','empty_crossing','puddle','bump','barrier','pothole','speeding','delivery','tips')

class CourierError(ValueError):pass


def notify(run,kind,**values):
    run['notice_seq']+=1
    run['notices']=(run['notices']+[dict(id=run['notice_seq'],kind=kind,**values)])[-10:]


def light(run,event):
    phase=(run['elapsed']+event.get('offset',0))%20
    return 'red' if phase<10 else 'amber' if phase<12 else 'green'


def needs_stop(run,event):
    if event['kind']=='intersection':return light(run,event)!='green'
    return event['kind']=='crossing' and event.get('people',False) and run['elapsed']<event.get('walk_until',0)


def _protect_address(run):
    d=run['delivery']
    for e in run['events']:
        if e['kind'] in ('barrier','puddle','bump','pothole') and abs(e['s']-d['s'])<30 and e['lane']==d['lane']:
            e['lane']=1 if d['lane']==0 else 2


def _fill_route(run):
    while run['generated_to']<run['distance']+520:
        chunk=run['generated_to'];rng=random.Random(f"{run['seed']}:{chunk}")
        run['events'].append(dict(id=f'{chunk}-limit',kind='limit',s=chunk+20,limit=40 if chunk==0 else rng.choice((30,40,50)),done=False))
        kinds=['barrier','puddle','bump','pothole'];rng.shuffle(kinds)
        for i,s in enumerate((45,95,225,345)):
            run['events'].append(dict(id=f'{chunk}-h{i}',kind=kinds[i],s=chunk+s+rng.randint(-7,7),lane=rng.randrange(4),done=False))
        special='intersection' if chunk==0 else rng.choices(('intersection','crossing','none'),weights=(.3,.35,.35))[0]
        if special!='none':
            run['events'].append(dict(id=f'{chunk}-road',kind=special,s=chunk+155+rng.randint(-8,8),offset=rng.uniform(0,20),people=rng.random()<.55,done=False,penalized=False))
        run['generated_to']+=400
    run['events']=[e for e in run['events'] if e['s']>run['distance']-50]
    _protect_address(run)


def _address(run,rng,first=False):
    distance=run['distance']+rng.randint(250,330) if first else run['distance']+rng.randint(350,500)
    for e in run['events']:
        if e['kind'] in ('intersection','crossing') and abs(e['s']-distance)<55:distance=e['s']+65
    run['delivery_seq']+=1
    run['delivery']=dict(id=f"{run['id']}-{run['delivery_seq']}",s=distance,lane=rng.choice((0,3)),base=rng.choice((180,220,260)),number=rng.randint(10,99))
    run['integrity']=100;run['hold']=0
    _protect_address(run)


def start(user,now=None,rng=None):
    now=time.time() if now is None else now;rng=secrets.SystemRandom() if rng is None else rng
    run=user.get('courier_city')
    if run and run['status']=='active':
        run['last_at']=now;run['revision']+=1
        return run
    run=dict(id=secrets.token_hex(12),seed=secrets.token_hex(12),revision=0,status='active',lane=1,speed=0.,target_speed=0.,limit=40,
             distance=0.,elapsed=0.,last_at=now,last_lane=-1.,wet_until=0.,slow_until=0.,stun_until=0.,steer_until=0.,
             speeding=0.,speed_fined=False,integrity=100,delivered=0,missed=0,hold=0.,delivery_seq=0,notice_seq=0,notices=[],events=[],generated_to=0)
    _address(run,rng,True);_fill_route(run);user['courier_city']=run
    return run


def snapshot(user):
    run=user.get('courier_city')
    if not run:return None
    fields=('id','revision','status','lane','speed','target_speed','limit','distance','elapsed','wet_until','slow_until','stun_until','steer_until',
            'integrity','delivered','missed','hold','delivery','notice_seq','notices','close_after_delivery')
    public={k:run[k] for k in fields if k in run}
    public['delivery']=dict(run['delivery']);public['notices']=[dict(n) for n in run['notices']]
    public['events']=[]
    for e in run['events']:
        if e['s']-run['distance']>110:continue
        item=dict(e)
        if e['kind']=='intersection':item['light']=light(run,e)
        if e['kind']=='crossing':item['walking']=needs_stop(run,e)
        public['events'].append(item)
    public['tips']=[dict(amount=amount,chance=chance) for amount,chance in TIPS]
    return public


def _tip(rng):
    roll=rng.random();threshold=0
    for amount,chance in TIPS:
        threshold+=chance
        if roll<threshold:return amount
    return 0


def step(user,body,now=None,rng=None):
    now=time.time() if now is None else now;rng=secrets.SystemRandom() if rng is None else rng
    run=user.get('courier_city')
    if not run or body.get('id')!=run['id']:raise CourierError('Смена устарела. Открой курьера заново.')
    if type(body.get('revision')) is not int or body['revision']!=run['revision']:raise CourierError('Состояние уже обновилось.')
    target=body.get('target_speed',run['target_speed']);steer=body.get('steer',0);brake=body.get('brake',False)
    if type(target) not in (int,float) or not math.isfinite(target) or not 0<=target<=MAX_SPEED:raise CourierError('Неверная скорость.')
    if type(steer) is not int or steer not in (-1,0,1) or type(brake) is not bool:raise CourierError('Неверное управление.')
    if run['status']!='active':return dict(base=0,tip=0,penalty=0)
    dt=min(STEP_CAP,max(0,now-run['last_at']));run['last_at']=now;run['elapsed']+=dt;run['revision']+=1
    run['target_speed']=0 if brake else target
    if steer:
        if run['speed']<3:
            if not run.get('stop_steer_warned'):notify(run,'start_before_steer');run['stop_steer_warned']=True
        elif run['elapsed']-run['last_lane']>=(.8 if run['elapsed']<run['steer_until'] else .2):
            run['lane']=max(0,min(3,run['lane']+steer));run['last_lane']=run['elapsed'];run['stop_steer_warned']=False
    desired=min(run['target_speed'],25) if run['elapsed']<run['slow_until'] else run['target_speed']
    if run['elapsed']<run['stun_until']:desired=0
    wet=run['elapsed']<run['wet_until'];old_speed=run['speed']
    rate=12 if desired>old_speed else (45 if brake else 18)*(.55 if wet else 1)
    run['speed']=max(0,old_speed+max(-rate*dt,min(rate*dt,desired-old_speed)))
    old_distance=run['distance'];candidate=old_distance+(old_speed+run['speed'])/2/3.6*dt
    finance=dict(base=0,tip=0,penalty=0)
    for e in run['events']:
        if e['kind']=='crossing' and e.get('people') and 'walk_until' not in e and e['s']-old_distance<50:
            e['walk_from']=run['elapsed'];e['walk_until']=run['elapsed']+6
    def trigger(e):return e['s']-STOP_OFFSET if e['kind'] in ('intersection','crossing') else e['s']
    for e in sorted(run['events'],key=trigger):
        if e.get('done') or trigger(e)>candidate:continue
        kind=e['kind']
        if kind in ('intersection','crossing'):
            if needs_stop(run,e):
                if not e.get('penalized'):
                    penalty=80 if kind=='intersection' else 60;finance['penalty']+=penalty
                    notify(run,'red_light' if kind=='intersection' else 'pedestrian',penalty=penalty);e['penalized']=True
                candidate=min(candidate,e['s']-STOP_OFFSET-.5);run['speed']=0;run['target_speed']=0;run['hold']=0
                break
            e['done']=True
        elif kind=='limit':
            run['limit']=e['limit'];e['done']=True;notify(run,'limit',limit=e['limit'])
        else:
            e['done']=True
            if e['lane']!=run['lane']:continue
            if kind=='puddle':run['wet_until']=run['elapsed']+8;notify(run,'puddle')
            elif kind=='bump' and run['speed']>25:
                run['integrity']=max(0,run['integrity']-12);run['speed']*=.5;notify(run,'bump')
            elif kind=='pothole':
                run['integrity']=max(0,run['integrity']-8);run['slow_until']=run['elapsed']+4;run['steer_until']=run['elapsed']+4;notify(run,'pothole')
            elif kind=='barrier':
                finance['penalty']+=100;run['integrity']=max(0,run['integrity']-20);run['speed']=0;run['target_speed']=0;run['stun_until']=run['elapsed']+1.5
                candidate=min(candidate,e['s']);notify(run,'barrier',penalty=100);break
    run['distance']=max(old_distance,candidate)
    if run['speed']>run['limit']+5:
        run['speeding']+=dt
        if run['speeding']>=2.5 and not run['speed_fined']:
            finance['penalty']+=35;notify(run,'speeding',penalty=35);run['speed_fined']=True;run['target_speed']=run['limit']
    else:run['speeding']=0;run['speed_fined']=False
    delivery=run['delivery']
    if abs(run['distance']-delivery['s'])<=7 and run['lane']==delivery['lane'] and run['speed']<1:
        run['hold']+=dt
        if run['hold']>=.8:
            finance['base']=round(delivery['base']*(.6+.4*run['integrity']/100))
            finance['tip']=run.pop('demo_tip',None) if user.get('_work_sandbox') and 'demo_tip' in run else _tip(rng)
            notify(run,'delivered',base=finance['base'],tip=finance['tip']);run['delivered']+=1
            run['speed']=0;run['target_speed']=0
            if run.get('close_after_delivery'):run['status']='complete';run['hold']=0
            else:_address(run,rng)
    else:run['hold']=0
    if run['distance']>run['delivery']['s']+16:
        run['missed']+=1;notify(run,'missed')
        if run.get('close_after_delivery'):run['status']='complete';run['speed']=run['target_speed']=0
        else:_address(run,rng)
    _fill_route(run)
    return finance


def scenario(user,kind,now=None):
    if not user.get('_work_sandbox'):raise CourierError('Сценарии доступны только в песочнице.')
    if kind not in SCENARIOS:raise CourierError('Неизвестный сценарий.')
    user.pop('courier_city',None);r=start(user,now);r.update(events=[],generated_to=800,distance=0,elapsed=0,speed=30.,target_speed=30.,limit=40)
    r['delivery'].update(s=600,lane=3);e=dict(id='demo',kind=kind,s=70,done=False,lane=1)
    if kind in ('red','green'):e.update(kind='intersection',offset=0 if kind=='red' else 12,penalized=False)
    elif kind in ('pedestrians','empty_crossing'):e.update(kind='crossing',people=kind=='pedestrians',penalized=False)
    elif kind=='speeding':r.update(speed=55.,target_speed=55.,limit=30);e=None
    elif kind in ('delivery','tips'):
        r.update(lane=3);r['delivery'].update(s=70,lane=3,base=220)
        if kind=='tips':r['demo_tip']=400
        e=None
    if e:r['events']=[e]
    return r
