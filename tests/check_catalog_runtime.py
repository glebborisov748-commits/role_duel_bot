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
 app.photo_generation.generate=AsyncMock(side_effect=AssertionError('Catalog action submitted a model job'))
 users={}
 collection={**{k:wardrobe.WARDROBE[k] for k in wardrobe.OUTFIT_FACTS},**wardrobe.ADULT_CATALOG_ITEMS}
 for uid,gender in ((907,'male'),(908,'female')):
  u=app.get_user(uid);users[uid]=u
  u.update(lang='ru',verified=True,agreement_accepted=True,personality_ready=True,world='anime',gender=gender,style='honest',bucks=100000,xp_migrated_v2=True,xp_migrated_v3=True,appearance={})
  chosen='male_bdsm_outfit' if gender=='male' else 'female_corset_skirt'
  assert not (await app.perform_webapp_purchase(u,uid,'adult_shop',chosen))['ok']
  u['xp']=app.LEVEL_XP_THRESHOLD[5]
  for key,item in collection.items():
   category='adult_shop' if item['adult'] else 'wardrobe';balance=u['bucks']
   result=await app.perform_webapp_purchase(u,uid,category,key)
   if not wardrobe.gender_matches(u,key):
    assert not result['ok'] and u['bucks']==balance;continue
   assert result['ok'],(key,result)
   assert u['inventory'][key]==1 and u['bucks']==balance-item['price']
   balance=u['bucks'];assert not (await app.perform_webapp_purchase(u,uid,category,key))['ok'];assert u['bucks']==balance
  shop=app.serialize_shop_state(u)
  listed={i['key']:i for c in shop['categories'] for i in c['items'] if c['key'] in ('wardrobe','adult_shop')}
  for removed in ('firefighter_male','firefighter_female','boxer_outfit'):
   assert removed not in listed
   assert not (await app.perform_webapp_purchase(u,uid,'adult_shop',removed))['ok']
  for key,item in collection.items():
   if not wardrobe.gender_matches(u,key):assert key not in listed;continue
   public=listed[key]
   assert public['owned'] and public['catalog_only']==bool(item.get('catalog_only')) and public['tags']==item['tags'] and public['gender']==item['gender']
   assert public['category']==('adult_shop' if item['adult'] else 'wardrobe')
   if not item.get('catalog_only'):assert public['image'] and Path('.'+public['image']).is_file()
  body={'outfit':chosen}
  async def request(_):return uid,u,body,None
  app._play_request=request
  assert not json.loads((await app.api_wardrobe_handler(None)).text)['ok']
  assert not wardrobe.active_outfit(u)
  body['outfit']='police_'+gender
  assert json.loads((await app.api_wardrobe_handler(None)).text)['ok']
  assert wardrobe.active_outfit(u)['body']=='police_'+gender
 app.save_data(app.user_data)
 disk=json.loads(Path(app.DATA_FILE).read_text())
 for uid,u in users.items():
  assert disk[str(uid)]['inventory']==u['inventory']
 app.photo_generation.generate.assert_not_awaited()
 print('Both genders: catalog-only additions, level gates, removed products, purchases, persistence, equip restrictions and no image-generation calls passed')
with asyncio.Runner(loop_factory=LocalLoop) as runner:runner.run(run())
