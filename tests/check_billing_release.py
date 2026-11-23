"""Real app API and durable purchases, no network/provider/payment calls."""
import os,sys,tempfile,asyncio,json,time,hmac,hashlib
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock
from urllib.parse import urlencode
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
os.environ.update(BOT_TOKEN='123456:TEST_ONLY',PROVOD_API_KEY='test',DATA_DIR=tempfile.mkdtemp())
import app,photo_wallet
class Loop(asyncio.SelectorEventLoop):
 def _make_self_pipe(self):self._ssock=None;self._csock=None
 def _close_self_pipe(self):pass
 def _write_to_self(self):pass
 def _run_once(self):self.call_later(.01,lambda:None);super()._run_once()
async def run():
 u=app.get_user(910);u.update(lang='ru',verified=True,agreement_accepted=True,personality_ready=True,style='honest',gender='female',world='anime',energy=150,bucks=100000,xp_migrated_v2=True,xp_migrated_v3=True)
 app.bot.send_message=AsyncMock();app.photo_generation.generate=AsyncMock();app.photo_generation.token=lambda:'mock'
 initial=photo_wallet.balance(u);assert initial==1
 await app.grant_product(u,'photo_5',910);assert photo_wallet.balance(u)==initial+5
 await app.grant_product(u,'subscribe_pro',910);assert u['bucks']==101000 and u['intim_scenes']==2
 assert photo_wallet.balance(u)==initial+5+45
 await app.grant_product(u,'scene_photo',910);assert u['intim_scenes']==3 and photo_wallet.balance(u)==initial+5+45+1
 assert app.product_rub('subscribe_pro',u)==300 and app.product_rub('subscribe_super',u)==800
 assert app.product_rub('subscribe_pro_week',u)==120
 assert app.PRODUCTS['intim_scene']['stars']==15 and app.PRODUCTS['scene_photo']['stars']==25
 # One shared calendar offer, one purchase per 48h period.
 for key in (app.exchange_today(),):
  assert app.buy_exchange(u,key)[0];before=u['bucks'];assert not app.buy_exchange(u,key)[0] and before==u['bucks']
  assert app.exchange_ready_in(u,key)>0
 st=app.serialize_app_state(u);shop=app.serialize_shop_state(u);work=app.serialize_work_state(u)
 assert st['photos']['total']>0 and len(st['purchase_products'])==3
 # Signed channel validation and exactly-once reward.
 data={'auth_date':str(int(time.time())),'user':json.dumps({'id':910})};key=hmac.new(b'WebAppData',os.environ['BOT_TOKEN'].encode(),hashlib.sha256).digest();data['hash']=hmac.new(key,'\n'.join(k+'='+v for k,v in sorted(data.items())).encode(),hashlib.sha256).hexdigest()
 class Request:
  headers={'X-Telegram-Init-Data':urlencode(data)}
  async def json(self):return {'action':'channel_check'}
 app.bot.get_chat_member=AsyncMock(return_value=SimpleNamespace(status='member'))
 bucks=u['bucks'];photos=photo_wallet.balance(u);scenes=u['intim_scenes']
 assert json.loads((await app.api_app_task_handler(Request())).text)['ok']
 assert u['bucks']==bucks+500 and photo_wallet.balance(u)==photos+1 and u['intim_scenes']==scenes+1
 assert json.loads((await app.api_app_task_handler(Request())).text)['ok'] and u['bucks']==bucks+500
 # Fixture from actual serializers for browser coverage.
 Path('/tmp/rd-billing-fixture.json').write_text(json.dumps({'app':app.serialize_app_state(u),'shop':shop,'work':work},ensure_ascii=False))
 app.save_data(app.user_data);disk=json.loads(Path(app.DATA_FILE).read_text())['910'];assert disk['photo_credits']==u['photo_credits'] and disk['channel_reward_claimed']
 app.photo_generation.generate.assert_not_awaited()
 print('Billing: live serializers, package grants, first bonus, prices, 48h calendar offer, signed channel check, once-only reward, durable JSON passed')
with asyncio.Runner(loop_factory=Loop) as runner:runner.run(run())
