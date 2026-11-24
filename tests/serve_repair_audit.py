"""Local-only real-API browser audit. Fake credentials, isolated data, mocked providers."""
import os,sys,json,time,tempfile,hmac,hashlib,asyncio
from datetime import datetime,timedelta
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock
from urllib.parse import urlencode
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
os.environ.update(BOT_TOKEN='123456:TEST_ONLY',PROVOD_API_KEY='mock',DATA_DIR=tempfile.mkdtemp(prefix='rd-repair-audit-'))
import app,profile_options as wardrobe,photo_wallet,mine,archaeology
from aiohttp import web
UID=7287815074
app.bot.create_invoice_link=AsyncMock(return_value='https://invoice.test/avatar');app.bot.send_message=AsyncMock(return_value=SimpleNamespace(message_id=123));app.bot.get_me=AsyncMock(return_value=SimpleNamespace(username='repair_audit_bot'));app._BOT_USERNAME['v']='repair_audit_bot'
app.photo_generation.token=lambda:'mock';prompts=[]
async def image(prompt,**kwargs):prompts.append(prompt);return (ROOT/'assets/body_view_dress.webp').read_bytes(),'webp'
app.photo_generation.generate=image
app.promo_of_day=lambda:{('food','water'):.15}
app.energizer_discount_today=lambda:.2
app.WEBAPP_URL='http://127.0.0.1:8901';app.APP_MODE=True

def model(*args,**kwargs):
 instruction=kwargs.get('messages',[{}])[0].get('content','')
 if 'Resolve a named FICTIONAL' in instruction:content=json.dumps(dict(recognized=True,adult=True,canonical_name='Astarion',source='Baldur’s Gate 3',gender='male',race='elf',appearance=dict(hair_style='medium',hair_color='silver',eyes='red',skin='fair')))
 elif 'Return JSON' in instruction or 'Extract the CURRENT' in instruction:content='{"allowed":true,"setting":"home","lighting":"soft","pose":"leaning_closer","framing":"three_quarter"}'
 else:content='*Аля подходит к тебе ближе.* Привет! Как проходит твой день?'
 return SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content=content))])
app.call_ai=model

def reset(mode='chat',uid=UID):
 u=app.get_user(uid);u.clear();u.update(_telegram_id=uid,lang='ru',verified=True,agreement_accepted=True,personality_ready=mode!='onboarding',gender='female',world='anime',style='warm',scene='live',char_name='Аля',appearance=dict(app.character_options.DEFAULT),appearance_race_v2=True,bucks=100000,energy=80,energizers=3,satiety=100,water=100,tour_seen=True,xp_migrated_v2=True,xp_migrated_v3=True,xp=app.LEVEL_XP_THRESHOLD[5],inventory={k:1 for k in wardrobe.WARDROBE},photo_wallet_version=1,photo_trial_granted=True,photo_credits=1,subscription={'active':True,'level':'super_pro','term_days':7,'expires_at':(datetime.now()+timedelta(days=7)).isoformat()},history=[{'id':'u0','role':'user','content':'Привет! Как твой день?','user_reaction':'💖'},{'id':'a0','role':'assistant','content':'*Аля подходит к тебе ближе.* Привет! Рада тебя видеть.','reaction':'🤔'}],relationship={})
 u['inventory'].pop('beanie',None)
 if mode in ('mine','dig'):
  mine.start(u);archaeology.start(u);m=u['mine_run']['maze'];n=m['size'];m['cells'][n+2].update(wall=False,ore=0,left=1);u['dig_run']['cells'][u['dig_run']['x']].update(earth=1,loot=0)
 if mode=='wardrobe':wardrobe.equip(u,'female_corset_skirt',5)
 app.save_data(app.user_data);return u
reset()

def init_data(uid=UID):
 fields={'auth_date':str(int(time.time())),'user':json.dumps({'id':uid,'first_name':'Audit'})};secret=hmac.new(b'WebAppData',os.environ['BOT_TOKEN'].encode(),hashlib.sha256).digest();fields['hash']=hmac.new(secret,'\n'.join(k+'='+v for k,v in sorted(fields.items())).encode(),hashlib.sha256).hexdigest();return urlencode(fields)
async def sdk(request):
 data=json.dumps(init_data(int(request.cookies.get('audit_uid',UID))));script='window.__popups=[];window.__tgSdkSettled=true;window.Telegram={WebApp:{initData:'+data+',ready(){},expand(){},setHeaderColor(){},setBackgroundColor(){},disableVerticalSwipes(){},BackButton:{hide(){},show(){},onClick(){},offClick(){}},HapticFeedback:{impactOccurred(){},selectionChanged(){},notificationOccurred(){}},showConfirm(t,c){c(true)},showPopup(o,c){window.__popups.push(o);if(c)c("cancel")},showAlert(t){window.__popups.push(t)}}};'
 return web.Response(text=script,content_type='application/javascript')
async def control(request):
 body=await request.json();u=reset(body.get('mode','chat'),int(body.get('uid',UID)))
 if 'gender' in body:u['gender']=body['gender']
 if 'dead' in body:u['dead']=body['dead']
 if 'stock' in body:u['defib_stock']=body['stock']
 if 'level' in body:u['xp']=app.LEVEL_XP_THRESHOLD[body['level']]
 if 'tour' in body:u['tour_seen']=not body['tour']
 if 'inventory' in body:u['inventory']=body['inventory'];u['starter_clothes_v1']=True
 if 'maintenance_preview' in body:u['maintenance_preview']=body['maintenance_preview']
 if 'tier' in body:u['subscription'].update(active=bool(body['tier']),level=body['tier'])
 return web.json_response({'ok':True,'state':app.serialize_app_state(u),'shop':app.serialize_shop_state(u),'work':app.serialize_work_state(u)})
async def report(request):
 u=app.get_user(int(request.cookies.get('audit_uid',UID)));return web.json_response({'prompts':prompts,'photos':photo_wallet.balance(u),'history':u['history'],'avatar':u.get('avatar'),'character_template':u.get('character_template'),'custom_character':u.get('custom_character'),'app':app.serialize_app_state(u),'shop':app.serialize_shop_state(u),'work':app.serialize_work_state(u),'sent_messages':app.bot.send_message.await_count})
server=web.Application();server.add_routes([web.get('/tg-sdk.js',sdk),web.post('/audit/control',control),web.get('/audit/report',report),web.get('/app',app.app_page_handler),web.get('/shop',app.shop_page_handler),web.get('/work',app.work_page_handler),web.get('/online',app.online_page_handler),web.get('/play',app.play_page_handler),web.get('/guide',app.guide_page_handler),web.get('/agreement',app.site_page_handler),web.get('/theme.css',app.theme_css_handler),web.get('/sfx.js',app.sfx_js_handler if hasattr(app,'sfx_js_handler') else app.sfx_handler),web.get('/assets/audio/{name}',app.audio_sample_handler),web.get('/assets/{name}',app.asset_image_handler),web.get('/avatars/{name}',app.avatar_file_handler)])
for path,handler in [('/api/app/state',app.api_app_state_handler),('/api/state',app.api_state_handler),('/api/work/state',app.api_work_state_handler)]:server.router.add_get(path,handler)
for path,handler in [('/api/app/support',app.api_app_support_handler),('/api/app/photo',app.api_app_photo_handler),('/api/app/invoice',app.api_app_invoice_handler),('/api/app/send',app.api_app_send_handler),('/api/online',app.api_online_handler),('/api/app/reset',app.api_app_reset_handler),('/api/app/revive',app.api_app_revive_handler),('/api/app/create',app.api_app_create_handler),('/api/app/settings',app.api_app_settings_handler),('/api/app/avatar-generate',app.api_profile_avatar_generate_handler),('/api/app/avatar',app.api_app_avatar_handler),('/api/app/wake',app.api_app_wake_handler),('/api/wardrobe',app.api_wardrobe_handler),('/api/buy',app.api_buy_handler),('/api/work/mine',app.api_work_mine_handler),('/api/work/dig',app.api_work_dig_handler)]:server.router.add_post(path,handler)
web.run_app(server,host='127.0.0.1',port=8901,print=lambda x:print(x,flush=True))
