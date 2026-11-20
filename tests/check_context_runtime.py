"""Signed APIs for canonical characters, avatar independence and recent scene poses."""
import os,sys,tempfile,asyncio,json,time,hmac,hashlib,base64
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock
from urllib.parse import urlencode
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
os.environ.update(BOT_TOKEN='123456:TEST_ONLY',PROVOD_API_KEY='mock',DATA_DIR=tempfile.mkdtemp())
import app,fandom_catalog,profile_options as w
class Loop(asyncio.SelectorEventLoop):
 def _make_self_pipe(self):self._ssock=None;self._csock=None
 def _close_self_pipe(self):pass
 def _write_to_self(self):pass
 def _run_once(self):self.call_later(.01,lambda:None);super()._run_once()
class Request:
 def __init__(self,uid,body):
  self.body=body;fields={'auth_date':str(int(time.time())),'user':json.dumps({'id':uid})};secret=hmac.new(b'WebAppData',os.environ['BOT_TOKEN'].encode(),hashlib.sha256).digest();fields['hash']=hmac.new(secret,'\n'.join(k+'='+v for k,v in sorted(fields.items())).encode(),hashlib.sha256).hexdigest();self.headers={'X-Telegram-Init-Data':urlencode(fields)}
 async def json(self):return self.body
async def call(handler,uid,**body):return json.loads((await handler(Request(uid,body))).text)
async def run():
 app.bot.send_message=AsyncMock();app.photo_generation.token=lambda:'mock';app.photo_generation.generate=AsyncMock(return_value=(b'\xff\xd8\xffmock','jpg'))
 app.call_ai=lambda *a,**kw:SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content='{"allowed":true,"setting":"home","lighting":"soft","pose":"standing"}'))])
 for i,key in enumerate(fandom_catalog.TEMPLATES):
  uid=1200+i;u=app.get_user(uid);u.update(lang='ru',verified=True,agreement_accepted=True)
  result=await call(app.api_app_create_handler,uid,world='anime',style='warm',scene='live',character_template=key,avatar_preset='male_2')
  assert result['ok'],result
  assert result['state']['character']['avatar_url'].endswith('male_2.webp')
  assert u['char_name']==fandom_catalog.TEMPLATES[key]['ru']
  assert u['race']==fandom_catalog.TEMPLATES[key]['race'] and not u.get('avatar_job')
 app.photo_generation.generate.assert_not_awaited()
 # Free upload while creating, independent of appearance.
 uid=1210;u=app.get_user(uid);u.update(lang='ru',verified=True,agreement_accepted=True)
 png='iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+aJKsAAAAASUVORK5CYII='
 result=await call(app.api_app_create_handler,uid,world='anime',gender='female',style='warm',scene='live',appearance=dict(app.character_options.DEFAULT),avatar='data:image/png;base64,'+png,name='Аля')
 assert result['ok'] and u.get('avatar')
 identity=app.photo_appearance(u)
 assert (await call(app.api_app_avatar_handler,uid,preset='female_2'))['ok']
 assert app.photo_appearance(u)==identity and not u.get('avatar')
 app.photo_wallet.grant(u,4)
 u['history']=[{'role':'assistant','content':'*Аля подходит ближе и наклоняется к тебе.*'}]
 await app.app_photo_generate(uid,u,'Фото по беседе')
 prompt=app.photo_generation.generate.call_args.args[0];assert 'visibly bent at the waist' in prompt and 'inset portrait' in prompt
 u['history']=[{'role':'assistant','content':'*Аля целует тебя.*'}]
 await app.app_photo_generate(uid,u,'Фото по беседе');assert 'one face directed at the viewer' in app.photo_generation.generate.call_args.args[0]
 u['inventory']={k:1 for k in w.WARDROBE};w.equip(u,'latex_bodysuit',5)
 assert 'skin-tight glossy black latex' in w.clothing_facts(u,5)
 w.equip(u,'dress',5);w.equip(u,'cat_ears_headband',5);w.equip(u,'pendant',5)
 assert (await call(app.api_wardrobe_handler,uid,look='female_0'))['ok']
 old=dict(u['active_outfit']);u['inventory']['pendant']=0
 assert not (await call(app.api_wardrobe_handler,uid,look='female_0'))['ok'] and u['active_outfit']==old
 u['inventory']['pendant']=1
 fixture={'state':app.serialize_app_state(u),'shop':app.serialize_shop_state(u),'onboarding':app.serialize_app_state(app.get_user(1211))}
 Path('/tmp/rd-context-fixtures.json').write_text(json.dumps(fixture,ensure_ascii=False))
 print('Signed APIs: six canonical characters, free upload/presets, avatar identity independence, recent leaning pose and one-face POV kiss passed')
with asyncio.Runner(loop_factory=Loop) as runner:runner.run(run())
