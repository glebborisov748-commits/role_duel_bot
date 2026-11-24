"""Signed farm, Stars fulfillment, photo extraction and collection flows; no live providers."""
import asyncio,base64,copy,hashlib,hmac,json,os,sys,tempfile,time
from datetime import datetime,timedelta
from pathlib import Path
from types import SimpleNamespace
from urllib.parse import urlencode
from unittest.mock import AsyncMock
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
os.environ.update(BOT_TOKEN='123456:TEST_ONLY',PROVOD_API_KEY='FAKE',DATA_DIR=tempfile.mkdtemp(prefix='rd-final-'))
import app
UID=5255398262
app.bot.send_message=AsyncMock(return_value=SimpleNamespace(message_id=1));app.bot.create_invoice_link=AsyncMock(return_value='https://t.me/$fake');app.bot.refund_star_payment=AsyncMock();app.bot.answer_pre_checkout_query=AsyncMock()
def setup(uid=UID):
 u=app.get_user(uid);u.update(_telegram_id=uid,lang='ru',verified=True,agreement_accepted=True,personality_ready=True,gender='female',world='anime',char_name='Аля',style='warm',bucks=10000,energy=80,satiety=100,water=100,history=[],inventory={},first_purchase_done=True,subscription={'active':False});app.save_data(app.user_data);return u

def req(uid,body,mode='live'):
 fields=dict(auth_date=str(int(time.time())),user=json.dumps(dict(id=uid,first_name='Test')));secret=hmac.new(b'WebAppData',os.environ['BOT_TOKEN'].encode(),hashlib.sha256).digest();fields['hash']=hmac.new(secret,'\n'.join(k+'='+v for k,v in sorted(fields.items())).encode(),hashlib.sha256).hexdigest()
 return SimpleNamespace(method='POST',headers={'X-Telegram-Init-Data':urlencode(fields),'X-Work-Mode':mode},json=AsyncMock(return_value=body))
async def call(handler,body,uid=UID,mode='live'):return json.loads((await handler(req(uid,body,mode))).text)
async def main():
 u=setup();assert all(k in app.CROPS for k in app.farm_upgrade.NEW_CROPS)
 result=await call(app.api_work_fertilizer_handler,{'action':'buy'});assert result['ok'] and u['bucks']==8000;assert not (await call(app.api_work_fertilizer_handler,{'action':'buy'}))['ok'];assert u['bucks']==8000
 app.farm_plant(u,0,'mango');app.farm_plant(u,1,'tomato');before=app.farm_state(u);result=await call(app.api_work_fertilizer_handler,{'action':'use','slot':0});after=app.farm_state(u);assert result['ok'];assert abs(after[0]['seconds_left']-before[0]['seconds_left']/2)<3;assert abs(after[1]['seconds_left']-before[1]['seconds_left'])<3;assert result['state']['fertilizer']['ready_in']>=7198
 saved=u['farm_plots'][0]['growth_bonus_seconds'];assert not (await call(app.api_work_fertilizer_handler,{'action':'use','slot':0}))['ok'];assert u['farm_plots'][0]['growth_bonus_seconds']==saved;assert not (await call(app.api_work_fertilizer_handler,{'action':'buy'}))['ok']
 u['farm_fertilizer']={'owned':False,'ready_at':0};app.save_data(app.user_data)
 invoice=await call(app.api_work_fertilizer_handler,{'action':'invoice'});assert invoice['ok'];assert app.bot.create_invoice_link.call_args.kwargs['prices'][0].amount==5;assert not app.farm_upgrade.snapshot(u)['owned'];assert app.product_stars('farm_fertilizer',{'coupon':{'discount':.9}})==5
 query=SimpleNamespace(from_user=SimpleNamespace(id=UID),invoice_payload='farm_fertilizer',currency='XTR',total_amount=5,id='q');await app.pre_checkout(query);assert app.bot.answer_pre_checkout_query.call_args.kwargs['ok']
 await call(app.api_work_fertilizer_handler,{'action':'buy'});await app.pre_checkout(query);assert not app.bot.answer_pre_checkout_query.call_args.kwargs['ok']
 def payment(charge):return SimpleNamespace(from_user=SimpleNamespace(id=UID),chat=SimpleNamespace(id=UID),successful_payment=SimpleNamespace(invoice_payload='farm_fertilizer',telegram_payment_charge_id=charge,currency='XTR',total_amount=5),answer=AsyncMock())
 await app.payment_success(payment('raced-charge'));app.bot.refund_star_payment.assert_awaited_once();await app.payment_success(payment('raced-charge'));assert app.bot.refund_star_payment.await_count==1
 u['farm_fertilizer']={'owned':False,'ready_at':0};app.save_data(app.user_data);bucks=u['bucks'];await app.payment_success(payment('paid-charge'));assert app.farm_upgrade.snapshot(u)['owned'] and u['bucks']==bucks;await app.payment_success(payment('paid-charge'));assert u['processed_star_charges'].count('paid-charge')==1
 chief=setup(app.MAIN_ADMIN_ID);private=app.work_profile(chief);result=await call(app.api_work_fertilizer_handler,{'action':'test_stars'},uid=app.MAIN_ADMIN_ID,mode='sandbox');assert result['ok'] and private['farm_fertilizer']['owned'];assert 'farm_fertilizer' not in chief
 u=setup();image='data:image/webp;base64,'+base64.b64encode((Path(__file__).resolve().parents[1]/'assets/work_mango.webp').read_bytes()).decode()
 analyzer=AsyncMock(return_value={'appearance':{k:v for k,v in app.character_options.DEFAULT.items() if k in app.character_options.VISUAL_KEYS},'description':'Тёмные волосы.'});app.analyze_reference_photo=analyzer
 assert not (await call(app.api_photo_reference_handler,{'action':'analyze','image':image}))['ok'];analyzer.assert_not_awaited()
 u['subscription']={'active':True,'level':'pro','expires_at':(datetime.now()+timedelta(days=1)).isoformat()};app.save_data(app.user_data);history=copy.deepcopy(u['history']);old=u.get('appearance');draft=(await call(app.api_photo_reference_handler,{'action':'analyze','image':image}))['draft'];assert u.get('appearance')==old and u['history']==history
 result=await call(app.api_photo_reference_handler,{'action':'apply','token':draft['token'],'appearance':draft['appearance'],'description':'Мягкие черты лица.'});assert result['ok'] and u['photo_reference_description']=='Мягкие черты лица.';assert not u.get('avatar');assert image not in json.dumps(u);assert not (await call(app.api_photo_reference_handler,{'action':'apply','token':draft['token'],'appearance':draft['appearance']}))['ok']
 for _ in range(2):assert (await call(app.api_photo_reference_handler,{'action':'analyze','image':image}))['ok']
 assert not (await call(app.api_photo_reference_handler,{'action':'analyze','image':image}))['ok'];assert analyzer.await_count==3
 u['photo_reference_daily']={};app.save_data(app.user_data);previous=copy.deepcopy(u['appearance'])
 async def stale_reference(*args):
  u.pop('photo_reference_job',None);return {'appearance':previous,'description':'ignored'}
 analyzer.side_effect=stale_reference
 assert not (await call(app.api_photo_reference_handler,{'action':'analyze','image':image}))['ok'];assert u['appearance']==previous
 u['xp']=app.LEVEL_XP_THRESHOLD[8];app.save_data(app.user_data);blocked=await app.perform_webapp_purchase(u,UID,'toys','vibrator');assert not blocked['ok']
 u['xp']=app.LEVEL_XP_THRESHOLD[9];app.save_data(app.user_data);before=u['bucks'];result=await app.perform_webapp_purchase(u,UID,'toys','vibrator');assert result['ok'] and before-u['bucks']==app.profile_options.TOY_PRICES['vibrator'];assert not (await app.perform_webapp_purchase(u,UID,'toys','vibrator'))['ok'];assert not (await app.perform_webapp_purchase(u,UID,'adult_shop','anal_plug'))['ok']
 assert (await call(app.api_collection_favorite_handler,{'key':'vibrator'}))['ok'];assert u['favorite_collection_item']=='vibrator';assert 'vibrator' not in app.profile_options.active_outfit(u).values();assert not (await call(app.api_collection_favorite_handler,{'key':'dildo'}))['ok']
 # Dispatch real command updates: the generic chat handler must not swallow late-registered commands.
 from aiogram.types import Update,Message,Chat,User
 app.bot.session.make_request=AsyncMock(return_value=Message(message_id=2,date=datetime.now(),chat=Chat(id=app.MAIN_ADMIN_ID,type='private'),text='ok'))
 for index,command in enumerate(('/photo_model','/test_mode on')):
  event=Message(message_id=10+index,date=datetime.now(),chat=Chat(id=app.MAIN_ADMIN_ID,type='private'),from_user=User(id=app.MAIN_ADMIN_ID,is_bot=False,first_name='Chief'),text=command)
  await app.dp.feed_update(app.bot,Update(update_id=100+index,message=event))
 assert app.bot.session.make_request.await_count>=2
 print('Remaining API: targeted half-time boost, use-triggered stock, spend-once, fixed-price Stars + race refunds/replay, sandbox isolation; subscriber photo draft/apply/quota/no raw storage; level-9 owned/favorite collection and purchase guards passed')
asyncio.run(main())
