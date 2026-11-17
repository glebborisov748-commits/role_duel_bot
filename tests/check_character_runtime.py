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
 assert len(app.BASE_STYLE_KEYS)==5 and len(app.STYLES)==12
 assert app.STYLES['rude']['label']=='Разговорный с матом'
 calls=[]
 async def image(prompt,**kwargs):
  calls.append(prompt)
  return Path('assets/portrait_female.webp').read_bytes(),'webp'
 app.photo_generation.token=lambda:'fake';app.photo_generation.generate=image
 body={'appearance':character_options.validate({'hair_color':'silver','eyes':'green','skin':'olive','hair_style':'curls'})}
 async def req(r):return 11,u,body,None
 app._play_request=req;app._app_request=req
 state=app.serialize_app_state(u)
 assert any(item['key']=='intellectual' and item['locked'] for item in state['character']['styles'])
 result=json.loads((await app.api_app_appearance_handler(None)).text)
 assert result['ok'] and not u.get('portrait_pending')
 assert u['portrait_url'].startswith('/api/appearance-preview.svg?')
 assert 'hair_color=silver' in u['portrait_url'] and 'eyes=green' in u['portrait_url']
 app.request_character_portrait(u);assert len(calls)==0
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
 # Recreating a male realistic companion uses the free preview and parsed custom facts.
 count=len(calls)
 body={'world':'realism','gender':'male','style':'honest','scene':'phone','appearance':{},'custom':'Внешность: взрослый мужчина 25+, кошачьи уши, белые волосы, зелёные глаза. Характер: спокойный.'}
 assert json.loads((await app.api_app_create_handler(None)).text)['ok']
 assert len(calls)==count and u['appearance']['species']=='cat' and u['appearance']['hair_color']=='silver'
 assert 'gender=male' in app.look_image(u)
 assert len(app.serialize_onboarding(u)['styles'])==12
 assert all(len(item['desc'])<140 and 'Ты ' not in item['desc'] for item in app.serialize_onboarding(u)['styles'])
 await app.app_photo_generate(11,u,'Пришли фото в костюме')
 assert 'ONE adult man' in calls[-1] and 'natural human' in calls[-1] and 'silver' in calls[-1]
 # Duplicate delivery acknowledgements cannot pay twice.
 app.resolve_webapp_user=lambda *args:(11,u,None)
 class Request:
  headers={}
  async def json(self):return {'game':'courier','hit_id':'delivery-test-123'}
 before=u['bucks'];a=json.loads((await app.api_work_hit_handler(Request())).text);b=json.loads((await app.api_work_hit_handler(Request())).text)
 assert a['ok'] and a['awarded']>0 and b['awarded']==a['awarded'] and u['bucks']==before+a['awarded']
 # Native sharing prepares a message only for this user; Telegram delivery is user controlled.
 app._BOT_USERNAME['v']='role_duel_bot'
 captured=[]
 async def prepared(**kw):captured.append(kw);return SimpleNamespace(id='prepared-mock')
 app.bot.save_prepared_inline_message=prepared
 body={'kind':'referral'}
 assert json.loads((await app.api_app_share_handler(None)).text)['id']=='prepared-mock'
 assert captured[0]['user_id']==11 and '?start=ref_' in captured[0]['result'].input_message_content.message_text
 print('Real integration passed: 12 personalities, appearance validation, free instant previews, photo appearance, tier enforcement, history preservation')
with asyncio.Runner(loop_factory=LocalLoop) as runner:runner.run(run())
