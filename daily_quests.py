"""Daily missions. Selection and claims are stable across page reloads and restarts."""
import hashlib
import random
import secrets

# key, event, target, reward kind, amount, RU/EN/DE title
CATALOG = (
 ('courier10','courier',10,'bucks',300,('Доставь 10 заказов','Deliver 10 orders','Liefere 10 Bestellungen')),
 ('courier20','courier',20,'energy',40,('Доставь 20 заказов','Deliver 20 orders','Liefere 20 Bestellungen')),
 ('hack3','hack',3,'bucks',300,('Выполни 3 взлома','Complete 3 hacks','Schaffe 3 Hacks')),
 ('hack5','hack',5,'energizers',1,('Выполни 5 взломов','Complete 5 hacks','Schaffe 5 Hacks')),
 ('catch20','catch',20,'energy',40,('Поймай 20 денежных предметов','Catch 20 money items','Fange 20 Geldobjekte')),
 ('catch35','catch',35,'bucks',350,('Поймай 35 денежных предметов','Catch 35 money items','Fange 35 Geldobjekte')),
 ('plant2','plant',2,'bucks',200,('Посади 2 растения','Plant 2 crops','Pflanze 2 Pflanzen')),
 ('water2','water',2,'energy',40,('Полей растения 2 раза','Water crops twice','Gieße Pflanzen zweimal')),
 ('harvest2','harvest',2,'bucks',400,('Собери урожай с 2 грядок','Harvest 2 plots','Ernte 2 Beete')),
 ('chat4','chat',4,'bucks',200,('Напиши 4 содержательных сообщения','Write 4 meaningful messages','Schreibe 4 gehaltvolle Nachrichten')),
 ('chat8','chat',8,'scenes',1,('Напиши 8 содержательных сообщений','Write 8 meaningful messages','Schreibe 8 gehaltvolle Nachrichten')),
 ('share1','share',1,'bucks',300,('Поделись ботом с другом','Share the bot with a friend','Teile den Bot mit einem Freund')),
 ('courier40','courier',40,'bucks',700,('Доставь 40 заказов','Deliver 40 orders','Liefere 40 Bestellungen')),
 ('hack12','hack',12,'energy',60,('Выполни 12 взломов','Complete 12 hacks','Schaffe 12 Hacks')),
 ('catch100','catch',100,'scenes',1,('Поймай 100 денежных предметов','Catch 100 money items','Fange 100 Geldobjekte')),
 ('chat20','chat',20,'bucks',500,('Напиши 20 содержательных сообщений','Write 20 meaningful messages','Schreibe 20 gehaltvolle Nachrichten')),
 ('plant5','plant',5,'energy',60,('Посади 5 растений','Plant 5 crops','Pflanze 5 Pflanzen')),
 ('harvest5','harvest',5,'bucks',650,('Собери урожай с 5 грядок','Harvest 5 plots','Ernte 5 Beete')),

 ('pipes3','pipes',3,'bucks',300,('Соедини 3 трубопровода','Connect 3 pipelines','Verbinde 3 Rohrleitungen')),
 ('dig4','dig',4,'bucks',350,('Принеси 4 находки из раскопок','Bring back 4 finds','Bringe 4 Fundstücke zurück')),
 ('mine6','mine',6,'bucks',400,('Подними 6 находок из шахты','Haul out 6 ore finds','Bringe 6 Erzfundstücke hoch')),

)
BY_ID = {q[0]:q for q in CATALOG}


def ensure(user, day, *, allow_farm=True,allowed_events=None):
    current = user.get('daily_quests')
    allowed=lambda q: (allow_farm or q[1] not in ('plant','water','harvest')) and (allowed_events is None or q[1] in allowed_events)
    same_day=isinstance(current,dict) and current.get('day')==day and len(current.get('items',[]))==2
    if same_day and all(i.get('claimed') or i['id'] in BY_ID and (allowed_events is None or BY_ID[i['id']][1] in allowed_events) for i in current['items']):return False
    seed = user.setdefault('quest_seed', secrets.token_hex(16))
    rng = random.Random(hashlib.sha256((seed+':'+day).encode()).digest())
    pool = [q for q in CATALOG if allowed(q)]
    previous = {i.get('id') for i in (current or {}).get('items', [])} if isinstance(current, dict) else set()
    fresh = [q for q in pool if q[0] not in previous]
    if len({q[1] for q in fresh}) >= 2:
        pool = fresh
    rng.shuffle(pool)
    kept=[i for i in current['items'] if i.get('claimed') or i['id'] in BY_ID and (allowed_events is None or BY_ID[i['id']][1] in allowed_events)] if same_day else []
    items=list(kept);used={BY_ID[i['id']][1] for i in items if i['id'] in BY_ID}
    for q in pool:
        if len(items)==2:break
        if q[1] in used:continue
        items.append({'id':q[0],'progress':0,'claimed':False});used.add(q[1])
    user['daily_quests']={'day':day,'items':items}
    return True


def record(user, event, amount=1):
    for item in user['daily_quests']['items']:
        definition = BY_ID[item['id']]
        if definition[1] == event and not item['claimed']:
            item['progress'] = min(definition[2], item['progress'] + amount)


def snapshot(user, lang, subscribed):
    ix = {'ru':0,'en':1,'de':2}.get(lang,1)
    result=[]
    for item in user['daily_quests']['items']:
        definition=BY_ID[item['id']]
        result.append({**item,'title':definition[5][ix],'target':definition[2],
            'event':definition[1], 'reward':{'kind':definition[3],
            'amount':definition[4] * (2 if subscribed and definition[3]=='bucks' else 1)}})
    return result


def take(user, day, quest_id, subscribed):
    if user.get('daily_quests',{}).get('day') != day:
        return None
    item=next((i for i in user['daily_quests']['items'] if i['id']==quest_id),None)
    if not item or item['claimed'] or item['progress'] < BY_ID[quest_id][2]:
        return None
    definition=BY_ID[quest_id]
    item['claimed']=True
    return definition[3], definition[4]*(2 if subscribed and definition[3]=='bucks' else 1)
