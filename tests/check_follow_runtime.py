"""Signed requests, real persistence and mocked providers/payments. No live messages."""
import os,sys,json,tempfile,asyncio,time,hmac,hashlib,base64
from datetime import datetime
from pathlib import Path
from urllib.parse import urlencode
from types import SimpleNamespace
from unittest.mock import AsyncMock
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
os.environ.update(BOT_TOKEN='123456:TEST_ONLY_NOT_REAL',PROVOD_API_KEY='test-only',DATA_DIR=tempfile.mkdtemp())
import app,profile_options
class LocalLoop(asyncio.SelectorEventLoop):
 def _make_self_pipe(self):self._ssock=None;self._csock=None
 def _close_self_pipe(self):pass
 def _write_to_self(self):pass
 def _run_once(self):self.call_later(.01,lambda:None);super()._run_once()
async def run():
 u=app.get_user(805);u.update(lang='ru',verified=True,agreement_accepted=True,personality_ready=False,energy=150,bucks=50000,xp_migrated_v2=True,xp_migrated_v3=True)
 init={'auth_date':str(int(time.time())),'user':json.dumps({'id':805,'first_name':'Test'})};key=hmac.new(b'WebAppData',os.environ['BOT_TOKEN'].encode(),hashlib.sha256).digest();init['hash']=hmac.new(key,'\n'.join(k+'='+v for k,v in sorted(init.items())).encode(),hashlib.sha256).hexdigest()
 body={}
 class Request:
  headers={'X-Telegram-Init-Data':urlencode(init)}
  async def json(self):return body
 req=Request();gen=AsyncMock(return_value=(Path('assets/wardrobe_model_anime_female.webp').read_bytes(),'webp'))
 app.photo_generation.generate=gen;app.photo_generation.token=lambda:'test'
 assert 'player' not in app.serialize_app_state(u)
 body={'world':'anime','gender':'female','style':'honest','scene':'phone','appearance_preset':'red'}
 assert json.loads((await app.api_app_create_handler(req)).text)['ok']
 assert u['appearance']['hair_color']=='red' and 'copper-red' in app.photo_appearance(u)
 state=app.serialize_app_state(u);assert not state['character']['avatar_url'] and state['character']['avatar']==''
 body={};assert not json.loads((await app.api_app_photo_handler(req)).text)['ok'];gen.assert_not_awaited()
 # A custom avatar is free without any subscription.
 body={'image':'data:image/webp;base64,'+base64.b64encode(Path('assets/portrait_female.webp').read_bytes()).decode()}
 assert json.loads((await app.api_app_avatar_handler(req)).text)['ok']
 assert u['avatar'] and not app.get_subscription_level(u)
 # Adult catalog lock applies to the server purchase route and the equip route.
 before=u['bucks'];res=await app.perform_webapp_purchase(u,805,'adult_shop','bunny_outfit');assert not res['ok'] and u['bucks']==before
 for k in ('dress','heels','stockings','shirt','trousers','hat'):
  assert (await app.perform_webapp_purchase(u,805,'wardrobe',k))['ok']
 for k in ('dress','heels'):
  body={'outfit':k};assert json.loads((await app.api_wardrobe_handler(req)).text)['ok']
 body={'outfit':'stockings'};assert not json.loads((await app.api_wardrobe_handler(req)).text)['ok']
 assert set(u['active_outfit'])=={'body','shoes'}
 u['xp']=app.LEVEL_XP_THRESHOLD[5];assert app.get_intimacy_level(u)==5
 assert (await app.perform_webapp_purchase(u,805,'adult_shop','bunny_outfit'))['ok']
 body={'outfit':'bunny_outfit'};assert json.loads((await app.api_wardrobe_handler(req)).text)['ok']
 # Persistent channel quest only completes on confirmed membership, never API failure.
 app.bot.get_chat_member=AsyncMock(return_value=SimpleNamespace(status='left'))
 body={'action':'channel_check'};assert not json.loads((await app.api_app_task_handler(req)).text)['ok'];assert not u.get('channel_quest_completed')
 app.bot.get_chat_member.side_effect=RuntimeError('not admin')
 assert not json.loads((await app.api_app_task_handler(req)).text)['ok'];assert app.daily_quest_state(u)['channel']
 app.bot.get_chat_member.side_effect=None;app.bot.get_chat_member.return_value=SimpleNamespace(status='member')
 assert json.loads((await app.api_app_task_handler(req)).text)['ok'];assert app.daily_quest_state(u)['channel'] is None
 # Invoice uses the exact ten-Star price; no real invoice is sent.
 app.bot.create_invoice_link=AsyncMock(return_value='https://invoice.example/test')
 body={'payload':'avatar_generate','method':'stars'}
 invoice=json.loads((await app.api_app_invoice_handler(req)).text);assert invoice['ok']
 assert app.bot.create_invoice_link.call_args.kwargs['prices'][0].amount==10
 # A confirmed 10-Star payment gives one durable credit, replay cannot give another.
 app.bot.send_message=AsyncMock();u['first_purchase_done']=True
 pay=SimpleNamespace(invoice_payload='avatar_generate',currency='XTR',telegram_payment_charge_id='test-charge',total_amount=10)
 message=SimpleNamespace(from_user=SimpleNamespace(id=805),chat=SimpleNamespace(id=805),successful_payment=pay)
 credits_before=app.photo_wallet.balance(u)
 await app.payment_success(message);await app.payment_success(message);assert app.photo_wallet.balance(u)==credits_before+1
 assert app.product_stars('avatar_generate',u)==10 and app.available_payment_methods('avatar_generate')==['stars']
 # Run exactly one explicit paid generation and persist its full-length image.
 body={};res=json.loads((await app.api_profile_avatar_generate_handler(req)).text);assert res['ok'];await asyncio.sleep(.08)
 assert gen.await_count==1 and u['avatar_generated'] and u['avatar_fullbody']==u['avatar'] and app.photo_wallet.balance(u)==credits_before
 assert 'full-length' in gen.call_args.args[0] and 'copper-red' in gen.call_args.args[0]
 assert u['energy']==150 # Stars avatar does not also spend energy.
 # Failure returns the paid attempt.
 await app.grant_product(u,'avatar_generate',805);gen.side_effect=RuntimeError('provider failed')
 body={};assert json.loads((await app.api_profile_avatar_generate_handler(req)).text)['ok'];await asyncio.sleep(.08)
 assert app.photo_wallet.balance(u)==credits_before+1 and not u.get('avatar_job')
 # Produce fixtures with the reported high multiplier and mature farm plants.
 u.update(subscription={'active':True,'level':'elite','expires_at':'2099-01-01T00:00:00'},history=[{'role':'user','content':'Встретимся в кафе?'},{'role':'assistant','content':'Давай, я уже заказала чай.','user_reaction':'💖','reaction_animated':True}])
 for key in profile_options.WARDROBE:u['inventory'][key]=1
 app._BOT_USERNAME['v']='role_duel_bot'
 appstate=app.serialize_app_state(u);appstate['settings']['tour_seen']=True;appstate['quests']['channel']={'title':'Подпишись на наш канал','url':app.CHANNEL_URL}
 appstate['character']['avatar_credits']=1
 work=app.serialize_work_state(u);work['multiplier']=2.8;work['bucks']=99999999
 # Existing farm initialization is kept; UI test fills crop snapshots from these real types.
 Path('/tmp/rd-follow-fixture.json').write_text(json.dumps({'app':appstate,'shop':app.serialize_shop_state(u),'work':work,'onboarding':app.serialize_onboarding(u)},ensure_ascii=False))
 disk=json.loads(Path(app.DATA_FILE).read_text())['805'];assert disk['active_outfit']==u['active_outfit']
 print('Signed creation without player, empty avatar, free upload, slots/adult gate, channel checks, Stars replay/credits/refund and persistence passed')
with asyncio.Runner(loop_factory=LocalLoop) as runner:runner.run(run())
