"""Real app integration, with isolated profiles and mocked image/LLM providers."""
import os,tempfile,sys,asyncio,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
os.environ.update(BOT_TOKEN='123456:TEST_ONLY_NOT_REAL',PROVOD_API_KEY='test-only',DATA_DIR=tempfile.mkdtemp())
import app,character_options
from types import SimpleNamespace
class LocalLoop(asyncio.SelectorEventLoop):
 def _make_self_pipe(self):self._ssock=None;self._csock=None
 def _close_self_pipe(self):pass
 def _write_to_self(self):pass
 def _run_once(self):self.call_later(.01,lambda:None);super()._run_once()
async def run():
 u=app.get_user(11);u.update(lang='ru',verified=True,agreement_accepted=True,personality_ready=True,world='anime',gender='female',style='rude',energy=150,energizers=2,history=[{'role':'user','content':'Привет'},{'role':'assistant','content':'Привет'}])
 u['subscription']={'active':True,'level':'super_pro','expires_at':'2099-01-01T00:00:00'}
 assert len(app.BASE_STYLE_KEYS)==5 and len(app.STYLES)==20
 assert app.STYLES['rude']['label']=='Без фильтра'
 calls=[]
 async def image(prompt):
  calls.append(prompt)
  return Path('assets/portrait_female.webp').read_bytes(),'webp'
 app.photo_generation.token=lambda:'fake';app.photo_generation.generate=image
 body={'appearance':character_options.validate({'hair_color':'silver','eyes':'green','skin':'olive','hair_style':'curls'})}
 async def req(r):return 11,u,body,None
 app._play_request=req;app._app_request=req
 state=app.serialize_app_state(u)
 assert any(item['key']=='intellectual' and item['locked'] for item in state['character']['styles'])
 result=json.loads((await app.api_app_appearance_handler(None)).text)
 assert result['ok'] and u['portrait_pending']
 await asyncio.sleep(1.3)
 assert u['portrait_url'].startswith('/avatars/') and not u['portrait_pending']
 assert 'green eyes' in calls[0] and 'silver' in calls[0] and 'olive skin' in calls[0]
 app.request_character_portrait(u);assert len(calls)==1
 assert u['energy']==150
 history=list(u['history']);body={'style':'intellectual'}
 assert not json.loads((await app.api_app_settings_handler(None)).text)['ok']
 u['subscription']['level']='elite'
 assert json.loads((await app.api_app_settings_handler(None)).text)['ok']
 assert u['history']==history
 app.call_ai=lambda *a,**kw:SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content='{"allowed":true,"prompt":"Adult in a casual outfit"}'))])
 await app.app_photo_generate(11,u,'Покажи себя')
 assert u['energy']==110 and u['history'][-1]['photo'].endswith('.webp')
 assert 'silver' in calls[-1] and 'green eyes' in calls[-1]
 print('Real integration passed: 20 personalities, appearance validation, portrait cache, photo appearance, tier enforcement, history preservation')
with asyncio.Runner(loop_factory=LocalLoop) as runner:runner.run(run())
