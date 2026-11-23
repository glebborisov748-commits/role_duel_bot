"""Release billing, entitlements, gated quests and tier settings using real signed APIs."""
import os,sys,tempfile,asyncio,json,time,hmac,hashlib
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock
from urllib.parse import urlencode
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
os.environ.update(BOT_TOKEN='123456:TEST_ONLY',PROVOD_API_KEY='mock',DATA_DIR=tempfile.mkdtemp())
import app,photo_wallet,premium_rules
class Loop(asyncio.SelectorEventLoop):
 def _make_self_pipe(self):self._ssock=None;self._csock=None
 def _close_self_pipe(self):pass
 def _write_to_self(self):pass
 def _run_once(self):self.call_later(.01,lambda:None);super()._run_once()
class Request:
 def __init__(self,body):
  self.body=body;fields={'auth_date':str(int(time.time())),'user':json.dumps({'id':960})};secret=hmac.new(b'WebAppData',os.environ['BOT_TOKEN'].encode(),hashlib.sha256).digest();fields['hash']=hmac.new(secret,'\n'.join(k+'='+v for k,v in sorted(fields.items())).encode(),hashlib.sha256).hexdigest();self.headers={'X-Telegram-Init-Data':urlencode(fields)}
 async def json(self):return self.body
async def call(handler,**body):return json.loads((await handler(Request(body))).text)
async def run():
 u=app.get_user(960);u.update(lang='ru',verified=True,agreement_accepted=True,personality_ready=True,gender='female',world='anime',style='warm',bucks=100000,first_purchase_done=True,xp_migrated_v2=True,xp_migrated_v3=True,history=[{'role':'user','content':'Привет'}])
 app.bot.send_message=AsyncMock();app.bot.refund_star_payment=AsyncMock();app.bot.create_invoice_link=AsyncMock(return_value='https://test.invalid/invoice')
 app.photo_generation.token=lambda:'mock';app.photo_generation.generate=AsyncMock(side_effect=AssertionError('Unexpected live generation'))
 assert not (await call(app.api_app_task_handler,id='x',day=app.local_today().isoformat()))['ok']
 assert not (await call(app.api_app_settings_handler,initiative_enabled=False))['ok']
 assert not (await call(app.api_app_settings_handler,needs_disabled=True))['ok']
 assert not (await call(app.api_spin_reminder_handler,enabled=False))['ok']
 await app.grant_product(u,'subscribe_pro_week',960);expiry=u['subscription']['expires_at'];before=photo_wallet.balance(u)
 q=premium_rules.upgrade(u);assert q['stars']==125 and q['term_days']==7
 await app.grant_product(u,'upgrade_to_super',960);assert u['subscription']['expires_at']==expiry and photo_wallet.balance(u)==before+10
 await app.grant_product(u,'upgrade_to_elite',960);assert u['subscription']['expires_at']==expiry and u['subscription']['level']=='elite'
 assert (await call(app.api_app_settings_handler,initiative_enabled=False,needs_disabled=True))['ok']
 u.update(water=0,satiety=0,water_zero_since='2000-01-01T00:00:00');app.apply_passive_satiety_decay(u)
 assert u['water']==100 and u['satiety']==100 and u['water_zero_since'] is None
 assert (await call(app.api_spin_reminder_handler,enabled=False))['ok']
 assert not (await call(app.api_app_invoice_handler,payload='photo_1',method='stars'))['ok']
 assert app.product_stars('avatar_generate',u)==5
 before=photo_wallet.balance(u);await app.grant_product(u,'avatar_generate',960)
 assert u['portrait_credits']==1 and photo_wallet.balance(u)==before
 assert app.photo_wallet.reserve_portrait(u);app.photo_wallet.finish(u,'avatar',True);assert u['portrait_credits']==1
 for payload,(amount,price) in photo_wallet.PACKS.items():
  before=photo_wallet.balance(u);await app.grant_product(u,payload,960);assert photo_wallet.balance(u)==before+amount
  assert app.product_stars(payload,u)==price
 offer=app.exchange_today();assert app.buy_exchange(u,offer)[0];before=u['bucks'];assert not app.buy_exchange(u,offer)[0] and u['bucks']==before
 app.bot.get_chat_member=AsyncMock(return_value=SimpleNamespace(status='member'))
 assert (await call(app.api_app_task_handler,action='channel_check'))['ok'];assert not app.daily_quest_state(u)['locked']
 # Standard photo receipts are also idempotent.
 before=photo_wallet.balance(u)
 receipt=SimpleNamespace(invoice_payload='photo_3',currency='XTR',telegram_payment_charge_id='photo-three',total_amount=25)
 message=SimpleNamespace(from_user=SimpleNamespace(id=960),chat=SimpleNamespace(id=960),successful_payment=receipt)
 await app.payment_success(message);await app.payment_success(message);assert photo_wallet.balance(u)==before+3
 # Stale upgrade is refunded once, never discarded after a successful Stars charge.
 payment=SimpleNamespace(invoice_payload='upgrade_to_super',currency='XTR',telegram_payment_charge_id='stale',total_amount=125)
 m=SimpleNamespace(from_user=SimpleNamespace(id=960),chat=SimpleNamespace(id=960),successful_payment=payment)
 await app.payment_success(m);await app.payment_success(m);assert app.bot.refund_star_payment.await_count==1
 states={}
 for tier in (None,'pro','super_pro','elite'):
  u['subscription']={'active':bool(tier),'level':tier,'term_days':7,'expires_at':expiry if tier else None};states[tier or 'free']=app.serialize_app_state(u)
 # Show all panels in the UI fixture as the chief would see them.
 work=app.serialize_work_state(u);work['rotation']['active']=work['rotation']['all'];app.mine.start(u);app.archaeology.start(u);work['mine']=app.mine.snapshot(u);work['dig']=app.archaeology.snapshot(u)
 Path('/tmp/rd-full-release.json').write_text(json.dumps({'states':states,'shop':app.serialize_shop_state(u),'work':work},ensure_ascii=False))
 app.photo_generation.generate.assert_not_awaited()
 print('Real APIs: weekly upgrades retain expiry; photo packs, portrait credits, exchange cooldown, quest lock, ELITE needs/initiative, PRO reminder toggle and stale-payment refunds passed')
with asyncio.Runner(loop_factory=Loop) as runner:runner.run(run())
