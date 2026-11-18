"""Signed real API integration: excavation payouts, crop bonus and online skin persistence."""
import os,sys,json,tempfile,asyncio,time,hmac,hashlib
from pathlib import Path
from urllib.parse import urlencode
from datetime import datetime,timedelta
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
os.environ.update(BOT_TOKEN='123456:TEST_ONLY',PROVOD_API_KEY='test',DATA_DIR=tempfile.mkdtemp())
import app,photo_wallet
class Loop(asyncio.SelectorEventLoop):
 def _make_self_pipe(self):self._ssock=None;self._csock=None
 def _close_self_pipe(self):pass
 def _write_to_self(self):pass
 def _run_once(self):self.call_later(.01,lambda:None);super()._run_once()
class Request:
 def __init__(self,uid,body):
  self.body=body;data={'auth_date':str(int(time.time())),'user':json.dumps({'id':uid})};key=hmac.new(b'WebAppData',os.environ['BOT_TOKEN'].encode(),hashlib.sha256).digest();data['hash']=hmac.new(key,'\n'.join(k+'='+v for k,v in sorted(data.items())).encode(),hashlib.sha256).hexdigest();self.headers={'X-Telegram-Init-Data':urlencode(data)}
 async def json(self):return self.body
async def call(handler,uid,**body):return json.loads((await handler(Request(uid,body))).text)
async def run():
 for uid in (920,921):
  u=app.get_user(uid);u.update(lang='ru',verified=True,agreement_accepted=True,personality_ready=True,style='honest',world='anime',gender='male',bucks=50000,xp_migrated_v2=True,xp_migrated_v3=True)
  u['subscription']={'active':True,'level':'super_pro','expires_at':(datetime.now()+timedelta(days=30)).isoformat()}
 u=app.get_user(920)
 result=await call(app.api_work_dig_handler,920,action='start');assert result['ok'];run=u['dig_run'];id=run['id'];before=u['bucks']
 assert all(c['loot'] is None for c in result['dig']['run']['cells'])
 assert not (await call(app.api_work_dig_handler,920,action='cashout',id='forged',amount=999999))['ok'] and u['bucks']==before
 run['bag']=[{'key':'relic','name':'Артефакт','value':320,'condition':100}]
 out=await call(app.api_work_dig_handler,920,action='cashout',id=id);assert out['ok'];after=u['bucks'];assert after==before+out['awarded'] and out['awarded']>0
 assert not (await call(app.api_work_dig_handler,920,action='cashout',id=id))['ok'] and u['bucks']==after
 assert not (await call(app.api_work_dig_handler,920,action='start'))['ok']
 # Daily price is locked at planting, and only applied once on harvest.
 market=app.farm_market();crop=market['crop'];assert app.farm_plant(u,0,crop)
 raw=u['farm_plots'][0];assert raw['market_multiplier']==1.5
 raw['planted_at']=(datetime.now()-timedelta(hours=app.CROPS[crop]['grow_hours']+1)).isoformat()
 snap=app.farm_state(u)[0];assert snap['payout_preview']==round(app.CROPS[crop]['base_payout']*1.5)
 assert app.farm_harvest(u,0)>0 and app.farm_harvest(u,0) is None
 # New wheel rewards credit the common wallet/inventory; published odds sum to 100%.
 count=photo_wallet.balance(u);app.apply_spin_prize(u,{'type':'photos','value':3});assert photo_wallet.balance(u)==count+3
 state=app.serialize_spin_state(u);assert abs(sum(p['chance'] for p in state['prizes'])-100)<.02
 expected=sum(p['value']*w for p,w in zip(app.SPIN_PRIZES,app.spin_weights(u)) if p['type']=='photos')/sum(app.spin_weights(u))
 print('Wheel: expected photo credits per spin',round(expected,4),'cost at $0.04',round(expected*.04,5))
 # Both skins survive server validation and appear to the opposite player.
 out=await call(app.api_online_handler,920,action='start',game='rps18',kind='friend',bet=100,adult=True,skin='anime_m_crop');assert out['ok'];code=out['state']['room']['id']
 out=await call(app.api_online_handler,921,action='join',code=code,bet=100,adult=True,skin='anime_f_long');assert out['ok']
 assert len(out['state']['room']['skins'])==2 and 'female_long' in out['state']['room']['skins'][1]['image']
 out=await call(app.api_online_handler,920,action='state');assert 'female_long' in out['state']['room']['skins'][1]['image']
 assert not (await call(app.api_online_handler,920,action='start',game='rps18',kind='friend',bet=0,adult=True,skin='../../secret'))['ok']
 app.save_data(app.user_data);disk=json.loads(Path(app.DATA_FILE).read_text());assert disk['920']['online_skin']=='anime_m_crop' and disk['920']['dig_collection']['relic']==1
 print('Real API: hidden excavation state, forged/replayed payouts, market bonus, photo wheel grants, odds and two-player skins passed')
with asyncio.Runner(loop_factory=Loop) as runner:runner.run(run())
