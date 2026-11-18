"""Signed real endpoints, fake accounts: rotation gates, midnight cashout and occupied slots."""
import os,sys,tempfile,json,time,hmac,hashlib,asyncio
from pathlib import Path
from urllib.parse import urlencode
from datetime import datetime,timedelta,date
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
os.environ.update(BOT_TOKEN='123456:TEST_ONLY',PROVOD_API_KEY='test',DATA_DIR=tempfile.mkdtemp())
import app,mine,work_rotation
class Loop(asyncio.SelectorEventLoop):
 def _make_self_pipe(self):self._ssock=None;self._csock=None
 def _close_self_pipe(self):pass
 def _write_to_self(self):pass
 def _run_once(self):self.call_later(.01,lambda:None);super()._run_once()
class Request:
 def __init__(self,uid,body):
  self.body=body;data={'auth_date':str(int(time.time())),'user':json.dumps({'id':uid})};secret=hmac.new(b'WebAppData',os.environ['BOT_TOKEN'].encode(),hashlib.sha256).digest();data['hash']=hmac.new(secret,'\n'.join(k+'='+v for k,v in sorted(data.items())).encode(),hashlib.sha256).hexdigest();self.headers={'X-Telegram-Init-Data':urlencode(data)}
 async def json(self):return self.body
async def call(fn,**body):return json.loads((await fn(Request(930,body))).text)
async def run():
 day=next(date(2026,11,18)+timedelta(days=n) for n in range(10) if work_rotation.is_open('mine',date(2026,11,18)+timedelta(days=n)))
 clock=[day];app.local_today=lambda:clock[0];app.local_now=lambda:datetime.combine(clock[0],datetime.min.time()).replace(hour=12)
 u=app.get_user(930);u.update(lang='ru',verified=True,agreement_accepted=True,personality_ready=True,world='anime',gender='male',style='honest',bucks=10000,xp_migrated_v2=True,xp_migrated_v3=True,xp=app.LEVEL_XP_THRESHOLD[5])
 result=await call(app.api_work_mine_handler,action='start');assert result['ok'];run=u['mine_run'];sid=run['id'];before=u['bucks']
 assert len(result['state']['rotation']['active'])==3 and result['state']['rotation']==app.serialize_work_state(app.get_user(931))['rotation']
 assert not (await call(app.api_work_mine_handler,action='haul',id='forged',amount=99999))['ok'];assert u['bucks']==before
 assert (await call(app.api_work_mine_handler,action='strike',id=sid,vein=0))['ok']
 run['bag']=[{'key':'gold','name':'Золото','value':220}]
 # Move to a closed shift: farming works and earned loot remains withdrawable once.
 clock[0]=next(day+timedelta(days=n) for n in range(1,10) if not work_rotation.is_open('mine',day+timedelta(days=n)))
 blocked=await call(app.api_work_mine_handler,action='strike',id=sid,vein=0);assert not blocked['ok'] and blocked['code']=='work_closed'
 assert not (await call(app.api_work_mine_handler,action='start'))['ok']
 payout=await call(app.api_work_mine_handler,action='haul',id=sid);assert payout['ok'] and payout['awarded']==220 and u['bucks']==before+220
 assert not (await call(app.api_work_mine_handler,action='haul',id=sid))['ok'];assert u['bucks']==before+220
 clock[0]=next(day+timedelta(days=n) for n in range(10) if not work_rotation.is_open('courier',day+timedelta(days=n)))
 closed='courier'
 game='hacker_combo' if closed=='clicker' else closed
 assert not (await call(app.api_work_hit_handler,game=game))['ok'];assert u['bucks']==before+220
 if not work_rotation.is_open('workshop',clock[0]):assert not (await call(app.api_work_workshop_handler,action='start'))['ok']
 assert app.farm_plant(u,0,'carrot')
 u['inventory']={k:1 for k in app.profile_options.WARDROBE}
 assert (await call(app.api_wardrobe_handler,outfit='police_male'))['ok'];shop=app.serialize_shop_state(u)
 assert len(shop['slot_locks'])==len(app.profile_options.SLOTS)-1
 assert not (await call(app.api_wardrobe_handler,outfit='hat'))['ok'];assert app.profile_options.active_outfit(u)=={'body':'police_male'}
 assert (await call(app.api_wardrobe_handler,outfit=None,slot='body'))['ok']
 assert not (await call(app.api_wardrobe_handler,outfit='dress'))['ok']
 assert not (await call(app.api_wardrobe_handler,outfit='stockings'))['ok']
 assert (await call(app.api_wardrobe_handler,outfit='tracksuit'))['ok'];assert set(app.profile_options.SLOTS)-set(app.serialize_shop_state(u)['slot_locks'])-{'body'}=={'head','shoes','neck'}
 # Real fixtures for mobile checks on an open mining day.
 clock[0]=day;u.pop('mine_ready_at',None);mine.start(u)
 Path('/tmp/rd-mine-fixture.json').write_text(json.dumps({'work':app.serialize_work_state(u),'shop':app.serialize_shop_state(u),'user':u},ensure_ascii=False))
 app.save_data(app.user_data);disk=json.loads(Path(app.DATA_FILE).read_text())['930'];assert disk['mine_collection']['gold']==1 and disk['active_outfit']['body']=='tracksuit'
 print('Signed endpoints: shared 3-job schedule, closed-job payout gates, midnight cashout once, always-open farm, slot locks and durable inventory passed')
with asyncio.Runner(loop_factory=Loop) as runner:runner.run(run())
