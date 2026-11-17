"""Exercise real persistence and endpoints with isolated accounts; no provider calls."""
import os,sys,json,tempfile,asyncio,time
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
os.environ.update(BOT_TOKEN='123456:TEST_ONLY_NOT_REAL',PROVOD_API_KEY='test-only',DATA_DIR=tempfile.mkdtemp())
import app,profile_options,workshop
class LocalLoop(asyncio.SelectorEventLoop):
 def _make_self_pipe(self):self._ssock=None;self._csock=None
 def _close_self_pipe(self):pass
 def _write_to_self(self):pass
 def _run_once(self):self.call_later(.01,lambda:None);super()._run_once()
async def run():
 u=app.get_user(51);u.update(lang='ru',verified=True,agreement_accepted=True,personality_ready=True,world='anime',gender='female',style='warm',bucks=10000,history=[{'role':'user','content':'Привет'}])
 assert u['preferences']==profile_options.defaults() and u['inventory']=={} and u['race']=='human'
 second=app.get_user(52);second['preferences']['latex_style']=True
 assert not u['preferences']['latex_style']
 for field in ('preferences','inventory','race'):u.pop(field)
 u=app.get_user(51)
 assert u['preferences']==profile_options.defaults() and u['race']=='human'
 # Purchases are permanent, server priced and do not create roleplay messages.
 before=list(u['history'])
 for key,item in profile_options.WARDROBE.items():
  balance=u['bucks'];assert (await app.perform_webapp_purchase(u,51,'wardrobe',key))['ok']
  assert u['inventory'][key]==1 and u['bucks']==balance-item['price']
  balance=u['bucks'];assert not (await app.perform_webapp_purchase(u,51,'wardrobe',key))['ok'];assert u['bucks']==balance
 assert not (await app.perform_webapp_purchase(u,51,'wardrobe','unknown'))['ok']
 u['bucks']=0;u['inventory'].pop('stockings');assert not (await app.perform_webapp_purchase(u,51,'wardrobe','stockings'))['ok'];assert 'stockings' not in u['inventory']
 assert u['history']==before
 body={}
 async def request(_):return 51,u,body,None
 app._app_request=request;app._play_request=request
 for invalid in ({'preferences':{'toys':'true'}},{'preferences':{'unknown':True}},{'race':'unknown'},{'preferences':{'toys':True},'race':[] }):
  body=invalid;old=json.dumps([u['preferences'],u['race']]);assert not json.loads((await app.api_app_settings_handler(None)).text)['ok'];assert json.dumps([u['preferences'],u['race']])==old
 body={'preferences':{'latex_style':True,'toys':True},'race':'android'}
 assert json.loads((await app.api_app_settings_handler(None)).text)['ok']
 disk=json.loads(Path(app.DATA_FILE).read_text())['51'];assert disk['inventory']==u['inventory'] and disk['preferences']==u['preferences'] and disk['race']=='android'
 state=app.serialize_app_state(u);assert len(state['content_settings']['preference_options'])==5 and len(state['content_settings']['races'])==10
 shop=app.serialize_shop_state(u);wardrobe=next(c for c in shop['categories'] if c['key']=='wardrobe')
 assert len(wardrobe['items'])==5 and sum(i['owned'] for i in wardrobe['items'])==4
 Path('/tmp/rd-profile-options.json').write_text(json.dumps({'app':state,'shop':shop,'onboarding':app.serialize_onboarding(u)}))
 body={'outfit':'stockings'}
 assert not json.loads((await app.api_wardrobe_handler(None)).text)['ok']
 body={'outfit':'bunny_outfit'}
 assert json.loads((await app.api_wardrobe_handler(None)).text)['ok'] and u['wardrobe_outfit']=='bunny_outfit'
 assert 'Outfit:' in app.photo_appearance(u)
 for invalid in ({},{'outfit':[]},{'outfit':'unknown'}):
  body=invalid;assert not json.loads((await app.api_wardrobe_handler(None)).text)['ok'];assert u['wardrobe_outfit']=='bunny_outfit'
 body={'outfit':None};assert json.loads((await app.api_wardrobe_handler(None)).text)['ok'];assert u['wardrobe_outfit'] is None
 assert all(i['key'] not in ('dress','heels') for c in shop['categories'] if c['key']=='gift' for i in c['items'])
 assert next(i for i in wardrobe['items'] if i['key']=='bunny_outfit')['name']=='Костюм «Зайка»'
 # The pipe answer is not public, and a paid completion is consumed exactly once.
 app.resolve_webapp_user=lambda *a:(51,u,None)
 class Request:
  headers={}
  async def json(self):return body
 body={'action':'start'};response=json.loads((await app.api_work_workshop_handler(Request())).text);assert response['ok'] and 'solution' not in response['job']
 job=u['pipe_job'];job['started']=time.time()-5;body={'action':'complete','id':job['id'],'values':job['solution']}
 balance=u['bucks'];res=json.loads((await app.api_work_workshop_handler(Request())).text);assert res['ok'] and u['bucks']==balance+35
 assert not json.loads((await app.api_work_workshop_handler(Request())).text)['ok'] and u['bucks']==balance+35
 assert u['pipe_completed']==1
 print('Profile options, persistent wardrobe, race and single-use pipe rewards passed')
with asyncio.Runner(loop_factory=LocalLoop) as runner:runner.run(run())
