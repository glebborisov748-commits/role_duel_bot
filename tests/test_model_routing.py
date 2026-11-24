"""Persisted route settings, exact catalog selection and admin authorization."""
import asyncio,copy,json,unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock,Mock
import model_routing as routes
from test_core import load_functions

class RouteTests(unittest.TestCase):
 def test_first_migration_pins_chat_and_inherits_scene(self):
  settings={};self.assertTrue(routes.initialize(settings));self.assertEqual(routes.selected(settings,'ai'),'deepseek-v3.2');self.assertEqual(routes.selected(settings,'intim'),'deepseek-v3.2')
 def test_explicit_legacy_scene_preserved_and_migration_idempotent(self):
  settings={};routes.initialize(settings,'configured-scene-model');self.assertEqual(routes.selected(settings,'intim'),'configured-scene-model')
  routes.update(settings,'ai','selected-chat-model');before=copy.deepcopy(settings);self.assertFalse(routes.initialize(settings,'different-env-model'));self.assertEqual(settings,before)
 def test_independent_routes_and_restart(self):
  settings={};routes.initialize(settings);routes.update(settings,'intim','scene-model');routes.update(settings,'ai','chat-model');loaded=json.loads(json.dumps(settings))
  self.assertEqual(routes.selected(loaded,'ai'),'chat-model');self.assertEqual(routes.selected(loaded,'intim'),'scene-model');routes.update(loaded,'intim','same');self.assertEqual(routes.selected(loaded,'intim'),'chat-model')
 def test_catalog_exact_version_slug_and_availability(self):
  catalog=[dict(id='deepseek-v3.2',canonical_slug='deepseek/deepseek-v3.2'),dict(id='deepseek-v4-flash'),dict(id='unavailable',available=False)]
  self.assertEqual(routes.catalog_id(catalog,'deepseek/deepseek-v3.2'),'deepseek-v3.2')
  for bad in ('deepseek','DeepSeek V3.2','unavailable','missing','https://other.test/key'):
   with self.assertRaises(ValueError):routes.catalog_id(catalog,bad)
 def test_ambiguous_catalog_does_not_select_arbitrary_provider(self):
  with self.assertRaises(ValueError):routes.catalog_id([dict(id='route-a',canonical_slug='vendor/model'),dict(id='route-b',canonical_slug='vendor/model')],'vendor/model')
 def test_invalid_route_cannot_change_existing_settings(self):
  s={};routes.initialize(s);old=copy.deepcopy(s)
  for route,target in [('unknown','model'),('ai','same'),('ai','')]:
   with self.assertRaises(ValueError):routes.update(s,route,target)
  self.assertEqual(s,old)

class AdminTests(unittest.IsolatedAsyncioTestCase):
 def namespace(self):
  self.saved=[];self.state={};routes.initialize(self.state)
  ns=dict(model_routing=routes,MAIN_ADMIN_ID=7,user_data={'__settings__':self.state},save_data=lambda d:self.saved.append(copy.deepcopy(d)),sync_data=lambda:None,ai_model_keyboard=lambda:None,ai_model_catalog=AsyncMock(return_value=[dict(id='test-chat'),dict(id='test-scene')]))
  load_functions({'apply_ai_model','ai_model_settings_text','_ai_model_admin','ai_models_cmd'},ns);return ns
 def message(self,text,uid=7,chat='private'):
  return SimpleNamespace(text=text,from_user=SimpleNamespace(id=uid),chat=SimpleNamespace(type=chat),answer=AsyncMock())
 async def test_only_chief_private_command_can_switch(self):
  ns=self.namespace()
  for uid,chat in [(8,'private'),(7,'group'),(7,'supergroup')]:await ns['ai_models_cmd'](self.message('/ai_model chat test-chat',uid,chat))
  self.assertFalse(self.saved);ns['ai_model_catalog'].assert_not_awaited()
 async def test_live_command_changes_only_target_route(self):
  ns=self.namespace();await ns['ai_models_cmd'](self.message('/ai_model hot test-scene'));await ns['ai_models_cmd'](self.message('/ai_model chat test-chat'))
  self.assertEqual(routes.selected(self.state,'ai'),'test-chat');self.assertEqual(routes.selected(self.state,'intim'),'test-scene');self.assertEqual(len(self.saved),2)
 async def test_hot_same_needs_no_catalog_or_paid_call(self):
  ns=self.namespace();await ns['ai_models_cmd'](self.message('/ai_model hot same'));ns['ai_model_catalog'].assert_not_awaited();self.assertEqual(routes.selected(self.state,'intim'),'deepseek-v3.2')
 async def test_missing_catalog_model_does_not_mutate_state(self):
  ns=self.namespace();before=copy.deepcopy(self.state);await ns['ai_models_cmd'](self.message('/ai_model chat not-listed'));self.assertEqual(self.state,before);self.assertFalse(self.saved)
 async def test_network_failure_keeps_previous_routes(self):
  ns=self.namespace();before=copy.deepcopy(self.state);ns['ai_model_catalog'].side_effect=RuntimeError('offline');await ns['ai_models_cmd'](self.message('/ai_model chat test-chat'));self.assertEqual(self.state,before);self.assertFalse(self.saved)
 async def test_failed_persistence_rolls_back_in_memory(self):
  ns=self.namespace();before=copy.deepcopy(self.state);ns['save_data']=Mock(side_effect=OSError('disk full'));await ns['ai_models_cmd'](self.message('/ai_model chat test-chat'));self.assertEqual(self.state,before)
