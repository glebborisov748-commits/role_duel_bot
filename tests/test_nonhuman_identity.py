"""Species identity must survive every photo path without human skin contradictions."""
import json
import unittest
from unittest.mock import patch
import httpx
import character_options as options
import profile_options as profile
import photo_generation as provider
import photo_context
import scene_photos

SPECIES=('robot','android','alien','furry_fox','furry_wolf','furry_cat','furry_dragon')

class NonhumanIdentityTests(unittest.TestCase):
 def test_species_are_distinct_from_costume_ears_and_available_without_appearance(self):
  for race in SPECIES:
   with self.subTest(race=race):
    self.assertEqual(profile.validate_race(race),race)
    for gender in ('male','female'):
     u={'race':race,'gender':gender}
     prompt=options.identity(u)
     self.assertIn(profile.RACE_FACTS[race],prompt)
     self.assertIn(profile.photo_subject(race,gender),prompt)
     self.assertIn('One continuous depiction',prompt)
  self.assertIn('human face',profile.RACE_FACTS['foxfolk'])
  self.assertIn('fox muzzle',profile.RACE_FACTS['furry_fox'])
 def test_nonhuman_surfaces_do_not_become_human_skin(self):
  for race in SPECIES:
   u={'race':race,'gender':'female','appearance':dict(options.DEFAULT)}
   text=options.appearance(u)
   self.assertNotIn('light beige skin',text)
   if profile.race_kind(race)=='mechanical':
    self.assertIn('shell finish',text);self.assertNotIn('hair',text);self.assertIn('optics',text)
   elif profile.race_kind(race)=='furry':self.assertIn('light beige fur',text)
   elif profile.race_kind(race)=='scaled':self.assertIn('light beige scales',text)
 def test_russian_chat_identity_matches_species_surfaces(self):
  u={'race':'robot','appearance':dict(options.DEFAULT)}
  self.assertIn('жемчужное',options.appearance(u,'ru'));self.assertNotIn('волос',options.appearance(u,'ru'))
  u['race']='alien';self.assertIn('бирюзовая',options.appearance(u,'ru'));self.assertNotIn('волос',options.appearance(u,'ru'))
 def test_costumes_keep_species_anatomy_in_avatar_scene_and_chat_prompts(self):
  for race in SPECIES:
   u={'race':race,'gender':'male','appearance':dict(options.DEFAULT),'inventory':{'tracksuit':1}}
   profile.equip(u,'tracksuit',5)
   clothes=profile.clothing_facts(u,5);appearance=options.identity(u)
   self.assertIn('tracksuit',clothes);self.assertIn(profile.anatomy_fit(race),clothes)
   self.assertIn(profile.photo_subject(race,'male'),photo_context.avatar_prompt(u,appearance,'studio',5))
   self.assertIn(profile.photo_subject(race,'male'),scene_photos.portrait_prompt(appearance,'male','{}',outfit=clothes,race=race))
   self.assertIn(profile.RACE_FACTS[race],photo_context.instruction(u,5,appearance))
 def test_fox_variants_and_unisex_previews_are_distinct(self):
  female=profile.WARDROBE['female_fox_cosplay'];male=profile.WARDROBE['male_fox_cosplay']
  self.assertEqual((female['gender'],male['gender']),('female','male'))
  self.assertNotEqual(female['image'],male['image'])
  for key in ('tracksuit','pajamas'):
   self.assertNotEqual(profile.body_preview(key,'male'),profile.body_preview(key,'female'))

class NonhumanProviderTests(unittest.IsolatedAsyncioTestCase):
 async def test_provider_preserves_nonhuman_identity_in_positive_and_negative_prompts(self):
  calls=[]
  async def handler(request):
   if request.method=='POST':calls.append(json.loads(request.content));return httpx.Response(200,json={'taskId':'mock'})
   if '/tasks/' in str(request.url):return httpx.Response(200,json={'ready':True,'status':'END_SUCCESS','result':{'taskResult':[{'url':'https://mock.invalid/image'}]}})
   return httpx.Response(200,content=b'\xff\xd8\xffmock')
  original=httpx.AsyncClient
  def client(**kw):return original(transport=httpx.MockTransport(handler),**kw)
  async def skip(*a):pass
  with patch.object(provider,'token',return_value='mock'),patch.object(provider.httpx,'AsyncClient',client),patch.object(provider.asyncio,'sleep',skip):
   for race in SPECIES:
    for gender in ('male','female'):
     await provider.generate('Clothed studio portrait',race=race,gender=gender,appearance={'hair_color':'red'})
     payload=calls[-1]
     self.assertIn(profile.RACE_FACTS[race],payload['prompt'])
     self.assertIn(profile.photo_subject(race,gender),payload['prompt'])
     self.assertNotIn('1girl',payload['prompt']);self.assertNotIn('1boy',payload['prompt'])
     if profile.race_kind(race) in ('mechanical','furry','scaled'):self.assertIn('human face',payload['negativePrompt'])
  self.assertEqual(len(calls),14)
