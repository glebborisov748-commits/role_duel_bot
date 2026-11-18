"""Isolated new-user audit server. Actual handlers, temporary storage and fake providers."""
import os,sys,tempfile,ast,json,time,hmac,hashlib
from pathlib import Path
from urllib.parse import urlencode
from types import SimpleNamespace
from unittest.mock import AsyncMock
from aiohttp import web
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
os.environ.update(BOT_TOKEN='123456:AUDIT_ONLY',PROVOD_API_KEY='audit-only',DATA_DIR=tempfile.mkdtemp())
import app
UID=100001
app._BOT_USERNAME['v']='audit_only_bot'
app.bot.send_message=AsyncMock();app.bot.create_invoice_link=AsyncMock(return_value='https://invoice.invalid/cancelled-audit')
app.bot.get_chat_member=AsyncMock(return_value=SimpleNamespace(status='left'))
def llm(*a,**kw):
 instruction=kw['messages'][0]['content']
 if 'Return JSON only:' in instruction and 'English image description' in instruction:text=json.dumps({'allowed':True,'prompt':'One adult woman wearing an ordinary outfit in a cafe'})
 elif 'setting and lighting' in instruction:text=json.dumps({'setting':'cafe','lighting':'day'})
 else:text='Привет! Рада познакомиться. Я как раз выбирала музыку на вечер.\n\nРасскажешь, как прошёл твой день и что тебе нравится слушать?'
 return SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content=text),finish_reason='stop')])
app.call_ai=llm;app.photo_generation.token=lambda:'audit-only'
async def image(*a,**kw):return (ROOT/'assets/portrait_female.webp').read_bytes(),'webp'
app.photo_generation.generate=image
fields={'auth_date':str(int(time.time())),'user':json.dumps({'id':UID,'first_name':'Новичок'})};secret=hmac.new(b'WebAppData',os.environ['BOT_TOKEN'].encode(),hashlib.sha256).digest();fields['hash']=hmac.new(secret,'\n'.join(k+'='+v for k,v in sorted(fields.items())).encode(),hashlib.sha256).hexdigest();init=urlencode(fields)
def reset():
 app.user_data.pop(str(UID),None);u=app.get_user(UID)
 # Simulate age/agreement confirmation in Telegram, outside the Mini App scope.
 u.update(lang='ru',verified=True,agreement_accepted=True);app.save_data(app.user_data)
reset()
async def sdk(request):
 script='window.__tgSdkSettled=true;window.Telegram={WebApp:{initData:'+json.dumps(init)+',themeParams:{},ready(){},expand(){},setHeaderColor(){},setBackgroundColor(){},disableVerticalSwipes(){},BackButton:{hide(){},show(){},onClick(){},offClick(){}},HapticFeedback:{impactOccurred(){},selectionChanged(){},notificationOccurred(){}},showConfirm(t,cb){cb(true)},showPopup(o,cb){cb(null)},openInvoice(u,cb){cb({status:"cancelled"})},openTelegramLink(){},openLink(){}}};'
 return web.Response(text=script,content_type='application/javascript')
async def inspect(request):return web.json_response({'user':app.get_user(UID),'init':init})
async def reset_route(request):reset();return web.json_response({'ok':True})
site=web.Application();seen=set()
for n in ast.walk(ast.parse((ROOT/'app.py').read_text())):
 if isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute) and n.func.attr in ('add_get','add_post') and len(n.args)>=2 and isinstance(n.args[0],ast.Constant) and isinstance(n.args[0].value,str) and isinstance(n.args[1],ast.Name):
  path=n.args[0].value;method=n.func.attr
  if path=='/tg-sdk.js' or (method,path) in seen:continue
  if hasattr(app,n.args[1].id):getattr(site.router,method)(path,getattr(app,n.args[1].id));seen.add((method,path))
site.router.add_get('/tg-sdk.js',sdk);site.router.add_get('/__audit__/inspect',inspect);site.router.add_post('/__audit__/reset',reset_route)
web.run_app(site,host='127.0.0.1',port=8769,print=lambda *a:None)
