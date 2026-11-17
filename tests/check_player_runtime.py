"""Real signed Mini App requests: player setup BEFORE a companion exists; no paid jobs."""
import os,sys,json,tempfile,asyncio,time,hmac,hashlib,base64
from pathlib import Path
from urllib.parse import urlencode
from unittest.mock import AsyncMock
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
os.environ.update(BOT_TOKEN='123456:TEST_ONLY_NOT_REAL',PROVOD_API_KEY='test-only',DATA_DIR=tempfile.mkdtemp())
import app
class LocalLoop(asyncio.SelectorEventLoop):
 def _make_self_pipe(self):self._ssock=None;self._csock=None
 def _close_self_pipe(self):pass
 def _write_to_self(self):pass
 def _run_once(self):self.call_later(.01,lambda:None);super()._run_once()
async def run():
 u=app.get_user(704);u.update(lang='ru',verified=True,agreement_accepted=True,personality_ready=False,energy=150)
 init={'auth_date':str(int(time.time())),'user':json.dumps({'id':704,'first_name':'Test'})}
 key=hmac.new(b'WebAppData',os.environ['BOT_TOKEN'].encode(),hashlib.sha256).digest()
 init['hash']=hmac.new(key,'\n'.join(k+'='+v for k,v in sorted(init.items())).encode(),hashlib.sha256).hexdigest()
 body={}
 class Request:
  headers={'X-Telegram-Init-Data':urlencode(init)}
  async def json(self):return body
 req=Request()
 gen=AsyncMock(side_effect=AssertionError('No image generation on setup'))
 app.photo_generation.generate=gen
 assert app.serialize_app_state(u)['player']['required']
 body={'gender':'male','world':'anime','race':'elf','appearance':{'hair_color':'silver'},'name':'Тест'}
 result=json.loads((await app.api_player_avatar_handler(req)).text)
 assert result['ok'] and not result['state']['player']['required'] and result['state']['onboarding']
 assert not u['personality_ready'] and u['energy']==150
 own=json.loads(json.dumps(u['player_avatar']))
 body={'world':'anime','gender':'female','style':'honest','scene':'phone','appearance':{},'race':'human','name':'Собеседник'}
 result=json.loads((await app.api_app_create_handler(req)).text);assert result['ok']
 assert u['gender']=='female' and u['player_avatar']['gender']=='male' and u['player_avatar']==own
 assert not json.loads((await app.api_app_create_handler(req)).text)['ok']
 before=json.dumps(u['appearance']);body={'appearance':{'hair_color':'red'}}
 assert not json.loads((await app.api_app_appearance_handler(req)).text)['ok'] and json.dumps(u['appearance'])==before
 body={'race':'android','preferences':{'toys':True}}
 before=json.dumps([u['preferences'],u['race']])
 assert not json.loads((await app.api_app_settings_handler(req)).text)['ok'] and json.dumps([u['preferences'],u['race']])==before
 u['subscription']={'active':True,'level':'super_pro','expires_at':'2099-01-01T00:00:00'}
 body={'gender':'male','world':'anime','race':'human','appearance':{},'image':'data:image/webp;base64,'+base64.b64encode(Path('assets/portrait_male.webp').read_bytes()).decode(),'photo_consent':True}
 assert json.loads((await app.api_player_avatar_handler(req)).text)['ok']
 uploaded=Path(app.AVATAR_DIR)/u['player_avatar']['avatar'];assert uploaded.is_file()
 body={'gender':'male','world':'anime','race':'human','appearance':{},'remove_photo':True}
 assert json.loads((await app.api_player_avatar_handler(req)).text)['ok'] and not uploaded.exists()
 assert not u['player_avatar'].get('avatar')
 disk=json.loads(Path(app.DATA_FILE).read_text())['704'];assert disk['player_avatar']==u['player_avatar']
 gen.assert_not_awaited()
 print('Signed fresh-account setup, separate player/companion, server edit gates, photo consent/removal and persistence passed')
with asyncio.Runner(loop_factory=LocalLoop) as runner:runner.run(run())
