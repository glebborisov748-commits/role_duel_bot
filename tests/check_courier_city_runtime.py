"""Real signed courier API and rollout checks with temporary local data, no provider calls."""
import asyncio,copy,json,hashlib,hmac,os,sys,tempfile,time
from pathlib import Path
from types import SimpleNamespace
from urllib.parse import urlencode
from unittest.mock import AsyncMock
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
os.environ.update(BOT_TOKEN='123456:TEST_ONLY',PROVOD_API_KEY='FAKE',DATA_DIR=tempfile.mkdtemp(prefix='rd-city-'))
import app,courier_city as city
OWNER=app.MAIN_ADMIN_ID;GUEST=5255398262

def setup(uid):
 u=app.get_user(uid);u.update(lang='ru',verified=True,agreement_accepted=True,personality_ready=True,bucks=1000,energy=80,water=100,satiety=100);app.save_data(app.user_data);return u

def request(uid,body=None,mode='live'):
 fields=dict(auth_date=str(int(time.time())),user=json.dumps(dict(id=uid,first_name='Test')));secret=hmac.new(b'WebAppData',os.environ['BOT_TOKEN'].encode(),hashlib.sha256).digest();fields['hash']=hmac.new(secret,'\n'.join(k+'='+v for k,v in sorted(fields.items())).encode(),hashlib.sha256).hexdigest()
 return SimpleNamespace(method='POST',headers={'X-Telegram-Init-Data':urlencode(fields),'X-Work-Mode':mode},json=AsyncMock(return_value=body or {}))

async def call(handler,uid,body,mode='live'):
 return json.loads((await handler(request(uid,body,mode))).text)

async def main():
 owner=setup(OWNER);guest=setup(GUEST);before=owner['bucks']
 result=await call(app.api_work_courier_handler,OWNER,dict(action='start'),mode='sandbox');assert result['ok'] and result['sandbox'];private=app.work_profile(owner)
 assert 'seed' not in result['courier'];assert result['courier']['lane']==1
 # Legacy stateless delivery/fine paths cannot modify a new courier's account.
 for handler in (app.api_work_hit_handler,app.api_work_penalty_handler):
  blocked=await call(handler,OWNER,dict(game='courier',tip=True,hit_id='fake-delivery-1'),mode='sandbox');assert not blocked['ok']
 assert owner['bucks']==before and private['bucks']==10000
 # Preview scenario gives an auditable award only to the preview wallet.
 await call(app.api_work_courier_handler,OWNER,dict(action='scenario',scenario='tips'),mode='sandbox');r=private['courier_city'];r.update(distance=70,lane=3,speed=0,target_speed=0,hold=.7);r['last_at']=time.time()-.4
 body=dict(action='step',id=r['id'],revision=r['revision'],target_speed=0)
 award=await call(app.api_work_courier_handler,OWNER,body,mode='sandbox');assert award['awarded']>=620 and award['tip']>=400;assert owner['bucks']==before
 saved=json.loads(Path(app.DATA_FILE).read_text());assert saved[str(OWNER)]['work_preview_profile']['bucks']==private['bucks']
 paid=private['bucks'];replay=await call(app.api_work_courier_handler,OWNER,body,mode='sandbox');assert not replay['ok'] and private['bucks']==paid
 delivered=next(n for n in award['courier']['notices'] if n['kind']=='delivered');assert delivered['base_awarded']+delivered['tip_awarded']==award['awarded']
 # Mode changes fence old requests before any motion or money changes.
 owner['work_preview_enabled']=False;app.save_data(app.user_data);blocked=await call(app.api_work_courier_handler,OWNER,body,mode='sandbox');assert blocked['code']=='work_scope_changed' and owner['bucks']==before
 # Publishing other new games must not silently publish this separate courier pass.
 app.user_data.setdefault('__settings__',{})['work_games_v2']=True
 assert not app.courier_v2(guest);blocked=await call(app.api_work_courier_handler,GUEST,dict(action='start'));assert not blocked['ok']
 message=SimpleNamespace(from_user=SimpleNamespace(id=GUEST),chat=SimpleNamespace(type='private'),text='/courier_release on',answer=AsyncMock());await app.work_testing_cmd(message);assert not app.courier_v2(guest)
 message.from_user.id=OWNER;message.chat.type='group';await app.work_testing_cmd(message);assert not app.courier_v2(guest)
 message.chat.type='private';await app.work_testing_cmd(message);assert app.courier_v2(guest)
 # Even with release on, public callers cannot force tips/scenarios or spoof a sandbox.
 for mode in ('live','sandbox'):
  blocked=await call(app.api_work_courier_handler,GUEST,dict(action='scenario',scenario='tips',_work_sandbox=True),mode=mode);assert not blocked['ok'] and guest['bucks']==1000
 app.work_is_open=lambda *args:True
 started=await call(app.api_work_courier_handler,GUEST,dict(action='start'));assert started['ok'];r=guest['courier_city']
 for bad in (dict(target_speed=99),dict(steer=True),dict(target_speed=float('inf'))):
  original=copy.deepcopy(r);blocked=await call(app.api_work_courier_handler,GUEST,dict(action='step',id=r['id'],revision=r['revision'],**bad));assert not blocked['ok'] and r==original
 # Traffic fines are server-created, bounded by the wallet and durably saved.
 r.update(distance=60,speed=30,target_speed=30,elapsed=0,last_at=time.time()-.5,events=[dict(id='red',kind='intersection',s=70,offset=0,done=False)],generated_to=10000);guest['bucks']=30
 fined=await call(app.api_work_courier_handler,GUEST,dict(action='step',id=r['id'],revision=r['revision']));assert fined['penalty']==30 and guest['bucks']==0;assert r['speed']==0
 assert any(n.get('actual_penalty')==30 for n in fined['courier']['notices'])
 # A job closing mid-route permits just the already-issued delivery.
 r.update(events=[],distance=r['delivery']['s'],lane=r['delivery']['lane'],speed=0,target_speed=0,hold=.7,last_at=time.time()-.4)
 app.work_is_open=lambda *args:False
 finished=await call(app.api_work_courier_handler,GUEST,dict(action='step',id=r['id'],revision=r['revision']));assert finished['ok'] and finished['courier']['status']=='complete'
 blocked=await call(app.api_work_courier_handler,GUEST,dict(action='start'));assert blocked['code']=='work_closed'
 message.text='/courier_release off';await app.work_testing_cmd(message);assert not app.courier_v2(guest);assert guest['courier_city']['delivered']==1
 print('City courier API: independent rollout, chief/scope guards, authoritative motion/fines, server-rolled tips, durable once-only payouts, no legacy bypass and closed-day completion passed')
asyncio.run(main())
