"""Real catalog serialization, purchases, persistence and equip route; no network."""
import os,sys,json,tempfile,asyncio
from pathlib import Path
from unittest.mock import AsyncMock
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
os.environ.update(BOT_TOKEN='123456:TEST_ONLY_NOT_REAL',PROVOD_API_KEY='test-only',DATA_DIR=tempfile.mkdtemp())
import app,profile_options as wardrobe
class LocalLoop(asyncio.SelectorEventLoop):
 def _make_self_pipe(self):self._ssock=None;self._csock=None
 def _close_self_pipe(self):pass
 def _write_to_self(self):pass
 def _run_once(self):self.call_later(.01,lambda:None);super()._run_once()
async def run():
 u=app.get_user(907);u.update(lang='ru',verified=True,agreement_accepted=True,personality_ready=True,world='anime',gender='male',style='honest',bucks=100000,xp_migrated_v2=True,xp_migrated_v3=True,appearance={})
 app.photo_generation.generate=AsyncMock(side_effect=AssertionError('Catalog action submitted a model job'))
 assert not (await app.perform_webapp_purchase(u,907,'adult_shop','police_male'))['ok']
 u['xp']=app.LEVEL_XP_THRESHOLD[5]
 new={k:v for k,v in wardrobe.WARDROBE.items() if v.get('catalog_only')}
 for key,item in new.items():
  category='adult_shop' if item['adult'] else 'wardrobe';balance=u['bucks']
  assert (await app.perform_webapp_purchase(u,907,category,key))['ok']
  assert u['inventory'][key]==1 and u['bucks']==balance-item['price']
  balance=u['bucks'];assert not (await app.perform_webapp_purchase(u,907,category,key))['ok'];assert u['bucks']==balance
 shop=app.serialize_shop_state(u)
 listed={i['key']:i for c in shop['categories'] for i in c['items'] if c['key'] in ('wardrobe','adult_shop')}
 for key,item in new.items():
  public=listed[key]
  assert public['owned'] and public['catalog_only'] and public['tags']==item['tags'] and public['gender']==item['gender']
  assert public['image'] is None and 'не подключено' in public['effects']
  assert public['category']==('adult_shop' if item['adult'] else 'wardrobe')
 body={'outfit':'police_male'}
 async def request(_):return 907,u,body,None
 app._play_request=request
 assert not json.loads((await app.api_wardrobe_handler(None)).text)['ok']
 assert not wardrobe.active_outfit(u)
 app.save_data(app.user_data)
 disk=json.loads(Path(app.DATA_FILE).read_text())['907'];assert all(disk['inventory'][k]==1 for k in new)
 app.photo_generation.generate.assert_not_awaited()
 print('22 new catalog entries: localized metadata, price/category, permanent purchases, duplicate protection, persistence and no generation passed')
with asyncio.Runner(loop_factory=LocalLoop) as runner:runner.run(run())
