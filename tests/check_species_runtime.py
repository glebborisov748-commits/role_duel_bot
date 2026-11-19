"""Signed creation and image-call plumbing for non-human companions, no live provider calls."""
import os,sys,json,tempfile,asyncio,time,hmac,hashlib
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock
from urllib.parse import urlencode
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
os.environ.update(BOT_TOKEN='123456:TEST_ONLY',PROVOD_API_KEY='mock',DATA_DIR=tempfile.mkdtemp())
import app,character_options,profile_options
class Loop(asyncio.SelectorEventLoop):
 def _make_self_pipe(self):self._ssock=None;self._csock=None
 def _close_self_pipe(self):pass
 def _write_to_self(self):pass
 def _run_once(self):self.call_later(.01,lambda:None);super()._run_once()
class Request:
 def __init__(self,uid,body):
  self.body=body;fields={'auth_date':str(int(time.time())),'user':json.dumps({'id':uid})};secret=hmac.new(b'WebAppData',os.environ['BOT_TOKEN'].encode(),hashlib.sha256).digest();fields['hash']=hmac.new(secret,'\n'.join(k+'='+v for k,v in sorted(fields.items())).encode(),hashlib.sha256).hexdigest();self.headers={'X-Telegram-Init-Data':urlencode(fields)}
 async def json(self):return self.body
async def run():
 app.photo_generation.generate=AsyncMock(return_value=(b'\xff\xd8\xffmock','jpg'))
 app.photo_generation.token=lambda:'mock'
 app.bot.send_message=AsyncMock()
 def llm(*a,**kw):
  instruction=kw['messages'][0]['content']
  text='{"setting":"studio","lighting":"soft"}' if 'setting and lighting' in instruction else '{"allowed":true,"prompt":"One clothed adult in a studio"}'
  return SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content=text))])
 app.call_ai=llm
 legacy=app.get_user(946);legacy.update(personality_ready=True,gender=None,look=next(k for k,v in app.LOOKS.items() if v['gender']=='male'))
 assert app.get_user(946)['gender']=='male'
 fixtures={}
 for index,(race,gender) in enumerate((('robot','male'),('furry_fox','female'),('alien','female'),('furry_wolf','male'))):
  uid=940+index;u=app.get_user(uid);u.update(lang='ru',verified=True,agreement_accepted=True)
  # An old client can still send a hairstyle preset, but explicit race/appearance must win.
  body={'world':'anime','gender':gender,'race':race,'style':'warm','scene':'phone','appearance':dict(character_options.DEFAULT),'appearance_preset':'red'}
  result=json.loads((await app.api_app_create_handler(Request(uid,body))).text)
  assert result['ok'] and u['race']==race and u['appearance']['hair_color']=='brown'
  assert not u.get('avatar_job');app.photo_generation.generate.assert_not_awaited() if index==0 else None
  u['history']=[{'role':'user','content':'Встретимся в студии?'}]
  app.photo_wallet.grant(u,3)
  await app.app_photo_generate(uid,u,'Фото по беседе')
  assert app.photo_generation.generate.call_args.kwargs['race']==race
  prompt=app.photo_generation.generate.call_args.args[0]
  assert profile_options.RACE_FACTS[race] in prompt
  if race=='robot':assert 'natural human proportions and skin texture' not in prompt
  u['avatar_job']={'id':'avatar','started':app.datetime.now().isoformat()}
  await app.generate_profile_avatar(u,'avatar')
  assert app.photo_generation.generate.call_args.kwargs['race']==race
  assert profile_options.photo_subject(race,gender) in app.photo_generation.generate.call_args.args[0]
  scene={'text':'At a studio','photo_id':'scene','photo_status':'pending','scene_type':next(iter(app.INTIM_SCENES)),'location':'any'};u.update(last_hot_scene=scene,scene_photo_job={'id':'scene','wallet':True})
  app.photo_wallet.reserve(u,'scene')
  await app.generate_scene_photo(u,scene,'scene')
  assert app.photo_generation.generate.call_args.kwargs['race']==race
  assert scene['photo_status']=='ready'
  fixtures[race]=app.serialize_app_state(u)
  assert u['race']==race
 Path('/tmp/rd-species-fixtures.json').write_text(json.dumps({'states':fixtures,'onboarding':app.serialize_onboarding({**app.get_user(945),'lang':'ru'})},ensure_ascii=False))
 assert app.photo_generation.generate.await_count==12
 print('Signed creation: explicit race beats legacy preset; chat/avatar/scene retain species in all 12 mocked image calls; no automatic creation generation passed')
with asyncio.Runner(loop_factory=Loop) as runner:runner.run(run())
