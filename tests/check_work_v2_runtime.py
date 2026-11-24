"""Real signed work APIs, private preview isolation and public rollout. Offline providers."""
import asyncio,copy,hashlib,hmac,json,os,sys,tempfile,time
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock
from urllib.parse import urlencode
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
os.environ.update(BOT_TOKEN='123456:TEST_ONLY',PROVOD_API_KEY='FAKE',DATA_DIR=tempfile.mkdtemp(prefix='rd-work-v2-'))
import app,casual_work
from test_casual_work import solution
OWNER=app.MAIN_ADMIN_ID;GUEST=5255398262

def setup(uid):
 u=app.get_user(uid);u.update(lang='ru',verified=True,agreement_accepted=True,personality_ready=True,bucks=777,energy=80,satiety=100,water=100,gender='female');app.save_data(app.user_data);return u

def auth(uid):
 fields={'auth_date':str(int(time.time())),'user':json.dumps({'id':uid,'first_name':'Test'})};secret=hmac.new(b'WebAppData',os.environ['BOT_TOKEN'].encode(),hashlib.sha256).digest();fields['hash']=hmac.new(secret,'\n'.join(k+'='+v for k,v in sorted(fields.items())).encode(),hashlib.sha256).hexdigest();return urlencode(fields)

def request(uid,body=None,mode='live',method='POST'):
 return SimpleNamespace(headers={'X-Telegram-Init-Data':auth(uid),'X-Work-Mode':mode},method=method,json=AsyncMock(return_value=body or {}))

async def call(handler,uid,body=None,mode='live',method='POST'):
 response=await handler(request(uid,body,mode,method));return json.loads(response.text)

async def main():
 owner=setup(OWNER);guest=setup(GUEST)
 state=(await call(app.api_work_state_handler,OWNER,method='GET'))['state'];assert state['sandbox'] and state['work_v2'] and state['bucks']==10000
 main_bucks=owner['bucks'];sandbox=app.work_profile(owner)
 # Unsigned caller cannot enter any work profile.
 bad=request(GUEST);bad.headers['X-Telegram-Init-Data']='bad';response=await app.api_work_casual_handler(bad);assert response.status==401
 # Forged sandbox header never grants another user preview access.
 denied=await call(app.api_work_casual_handler,GUEST,dict(game='puzzle',action='start'),mode='sandbox');assert not denied['ok'];assert guest['bucks']==777
 denied=await call(app.api_work_casual_handler,GUEST,dict(game='puzzle',action='start'));assert not denied['ok']
 for invalid in ([],{},None,'unknown'):
  rejected=await call(app.api_work_casual_handler,OWNER,dict(game=invalid,action='start'),mode='sandbox');assert not rejected['ok'] and owner['bucks']==main_bucks
 # Retired old mechanics cannot create new jobs through stale clients in v2.
 old=await call(app.api_work_mine_handler,OWNER,dict(action='start'),mode='sandbox');assert not old['ok'] and not sandbox.get('mine_run')
 # Play an actual generated solvable puzzle through the signed handler.
 started=await call(app.api_work_casual_handler,OWNER,dict(game='puzzle',action='start'),mode='sandbox');run=started['state']['puzzle']['run'];path=solution(run['board'])
 real_action=casual_work.action;clock=[time.time()+5]
 def timed(user,game,body):
  clock[0]+=.3;return real_action(user,game,body,now=clock[0])
 casual_work.action=timed
 awarded=0
 for index in path:
  result=await call(app.api_work_casual_handler,OWNER,dict(game='puzzle',action='move',id=run['id'],revision=run['revision'],index=index),mode='sandbox');assert result['ok'],result.get('error');awarded+=result['awarded'];run=result['state']['puzzle']['run']
 assert awarded>0 and run['status']=='won';assert sandbox['bucks']==10000+awarded and owner['bucks']==main_bucks
 replay=await call(app.api_work_casual_handler,OWNER,dict(game='puzzle',action='move',id=run['id'],revision=run['revision'],index=0),mode='sandbox');assert replay['awarded']==0
 # Catch money, powerup and farm spending use the same sandbox account.
 hit=await call(app.api_work_hit_handler,OWNER,dict(game='catch'),mode='sandbox');assert hit['ok'] and hit['awarded']>0;assert owner['bucks']==main_bucks
 before=sandbox['bucks'];await call(app.api_work_farm_buy_slot_handler,OWNER,mode='sandbox');assert sandbox['bucks']<before and owner['bucks']==main_bucks;assert not owner.get('farm_slots_bought')
 # A mode change rejects queued writes from the previous scope.
 owner['work_preview_enabled']=False;app.save_data(app.user_data)
 rejected=await call(app.api_work_hit_handler,OWNER,dict(game='catch'),mode='sandbox');assert rejected['code']=='work_scope_changed' and owner['bucks']==main_bucks
 owner['work_preview_enabled']=True;app.save_data(app.user_data)
 rejected=await call(app.api_work_hit_handler,OWNER,dict(game='catch'),mode='live');assert rejected['code']=='work_scope_changed' and owner['bucks']==main_bucks
 # Only a private chief command can publish/rollback for others.
 before=copy.deepcopy(app.user_data.get('__settings__',{}))
 msg=SimpleNamespace(from_user=SimpleNamespace(id=GUEST),chat=SimpleNamespace(type='private'),text='/work_release on',answer=AsyncMock());await app.work_testing_cmd(msg);assert app.user_data.get('__settings__',{})==before
 msg.from_user.id=OWNER;msg.chat.type='group';await app.work_testing_cmd(msg);assert app.user_data.get('__settings__',{})==before
 msg.chat.type='private';await app.work_testing_cmd(msg)
 state=(await call(app.api_work_state_handler,GUEST,method='GET'))['state'];assert state['work_v2'] and not state['sandbox']
 # Closed-day jobs can finish an issued puzzle, never start a fresh one.
 app.work_is_open=lambda *args:True
 result=await call(app.api_work_casual_handler,GUEST,dict(game='warehouse',action='start'));assert result['ok'];r=guest['warehouse_job'];index=next(i for i,v in enumerate(r['contents']) if v)
 result=await call(app.api_work_casual_handler,GUEST,dict(game='warehouse',action='open',id=r['id'],revision=0,index=index));assert result['ok'];assert 'contents' not in result['state']['warehouse']['run']
 app.work_is_open=lambda *args:False
 result=await call(app.api_work_casual_handler,GUEST,dict(game='warehouse',action='cashout',id=r['id'],revision=1));assert result['ok'] and result['awarded']>0
 paid=guest['bucks'];result=await call(app.api_work_casual_handler,GUEST,dict(game='warehouse',action='cashout',id=r['id'],revision=r['revision']));assert guest['bucks']==paid
 result=await call(app.api_work_casual_handler,GUEST,dict(game='warehouse',action='start'));assert result['code']=='work_closed'
 # Old cargo remains withdrawable even after the replacement and daily closure.
 app.mine.start(guest);guest['mine_run']['bag']=[{'key':'coal','value':19}];ident=guest['mine_run']['id'];before=guest['bucks']
 result=await call(app.api_work_mine_handler,GUEST,dict(action='haul',id=ident));assert result['ok'] and guest['bucks']>before
 before=guest['bucks'];await call(app.api_work_mine_handler,GUEST,dict(action='haul',id=ident));assert guest['bucks']==before
 app.archaeology.start(guest);guest['dig_run']['bag']=[{'key':'coin','value':23}];ident=guest['dig_run']['id'];before=guest['bucks']
 result=await call(app.api_work_dig_handler,GUEST,dict(action='cashout',id=ident));assert result['ok'] and guest['bucks']>before
 # Rollback retains both the new game's data and any legacy progress.
 guest['mine_rank']=2;msg.text='/work_release off';await app.work_testing_cmd(msg);assert guest['mine_rank']==2 and guest['warehouse_job']['status']=='paid'
 assert not (await call(app.api_work_state_handler,GUEST,method='GET'))['state']['work_v2']
 casual_work.action=real_action
 print('Work v2 signed API: sandbox wallet/farm isolation, forged/stale scope guards, replay-safe payout, old-game retirement, chief-only publication and rollback, rotation/cashout and hidden-crate secrecy passed')
asyncio.run(main())
