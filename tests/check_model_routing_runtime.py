"""Exercise real model dispatch and Telegram model picker with fake providers only."""
import asyncio,copy,json,os,sys,tempfile
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock,AsyncMock
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
os.environ.update(BOT_TOKEN='123456:TEST_ONLY',PROVOD_API_KEY='FAKE_TEST_KEY',DATA_DIR=tempfile.mkdtemp(prefix='rd-routes-'),AI_MODEL='old-flash-config',INTIM_MODEL='')
import app,model_routing as routes


def reply(text='Проверка ответа'):
 return SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content=text),finish_reason='stop')])

async def main():
 assert app.AI_MODEL=='old-flash-config'
 assert app.resolve_model('ai')==app.resolve_model('intim')=='deepseek-v3.2'
 app.client.chat.completions.create=Mock(side_effect=lambda **kwargs:reply())
 app.call_ai(app.AI_MODEL,'ai',messages=[dict(role='user',content='Проверка',reaction='ignored')])
 assert app.client.chat.completions.create.call_args.kwargs['model']=='deepseek-v3.2'
 assert app.client.chat.completions.create.call_args.kwargs['messages']==[dict(role='user',content='Проверка')]
 entries=[SimpleNamespace(id='deepseek-v3.2',canonical_slug='deepseek/deepseek-v3.2',available=True),SimpleNamespace(id='test-scene',canonical_slug='test/scene',available=True)]+[SimpleNamespace(id=f'candidate-{i:02}',available=True) for i in range(12)]
 app.client.models.list=Mock(return_value=SimpleNamespace(data=entries))
 app.client.chat.completions.create.reset_mock()
 message=SimpleNamespace(text='',reply_markup=None,chat=SimpleNamespace(type='private'),answer=AsyncMock(),edit_text=AsyncMock())
 call=SimpleNamespace(from_user=SimpleNamespace(id=app.MAIN_ADMIN_ID),message=message,data='ai_models:open:intim',answer=AsyncMock())
 await app.ai_models_cb(call);assert len(app.AI_MODEL_MENUS)==1
 token,menu=next(iter(app.AI_MODEL_MENUS.items()));assert menu['entries'][0]['id']=='deepseek-v3.2'
 page_text,kb=app.ai_model_menu_page(token,1);assert '2/2' in page_text
 for row in kb.inline_keyboard:
  for button in row:assert len(button.callback_data.encode())<=64
 index=next(i for i,e in enumerate(menu['entries']) if e['id']=='test-scene')
 call.data=f'ai_models:pick:{token}:{index}';await app.ai_models_cb(call)
 app.client.chat.completions.create.assert_not_called()
 assert app.resolve_model('ai')=='deepseek-v3.2';assert app.resolve_model('intim')=='test-scene'
 saved=json.loads(Path(app.DATA_FILE).read_text());assert routes.selected(saved['__settings__'],'intim')=='test-scene'
 app.call_ai(app.INTIM_MODEL,'intim',messages=[dict(role='user',content='Проверка маршрута')])
 assert app.client.chat.completions.create.call_args.kwargs['model']=='test-scene'
 app.call_ai(app.AI_MODEL,'ai',messages=[dict(role='user',content='Проверка чата')])
 assert app.client.chat.completions.create.call_args.kwargs['model']=='deepseek-v3.2'
 # No hidden provider/version fallback on failure of a pinned route.
 class Missing(Exception):status_code=404
 app.client.chat.completions.create=Mock(side_effect=Missing('model not found'))
 catalog_calls=app.client.models.list.call_count
 try:app.call_ai(app.AI_MODEL,'ai',messages=[dict(role='user',content='Проверка')])
 except Missing:pass
 else:raise AssertionError('Missing model silently replaced')
 assert app.client.chat.completions.create.call_count==1
 assert app.client.models.list.call_count==catalog_calls
 # Frozen request model also covers language-repair retries during a live switch.
 used=[]
 def raw(model,key,**kwargs):
  used.append(model)
  if len(used)==1:
   app.apply_ai_model('ai','next-chat-model');return reply('Привет actually, я здесь')
  return reply()
 original=app._call_ai_raw;app._call_ai_raw=raw
 app.call_ai(app.AI_MODEL,'ai',messages=[dict(role='user',content='Проверка')])
 app._call_ai_raw=original
 assert used==['deepseek-v3.2','deepseek-v3.2'],used
 assert app.resolve_model('ai')=='next-chat-model'
 # Stale keyboards and unauthorized callbacks never alter persisted routes.
 before=copy.deepcopy(app.user_data)
 call.data='ai_models:pick:expired:0';await app.ai_models_cb(call);assert app.user_data==before
 call.from_user.id=app.ADMIN_IDS[1];call.data='ai_models:same';await app.ai_models_cb(call);assert app.user_data==before
 call.from_user.id=app.MAIN_ADMIN_ID;call.message.chat.type='supergroup';await app.ai_models_cb(call);assert app.user_data==before
 call.message.chat.type='private';await app.ai_models_cb(call)
 assert app.resolve_model('intim')=='next-chat-model'
 # Returning to the already-selected inheritance setting does not report an edit error.
 message.text=app.ai_model_settings_text();message.reply_markup=app.ai_model_keyboard();message.edit_text.reset_mock()
 await app.ai_models_cb(call);message.edit_text.assert_not_awaited()
 print('Model routing: pinned V3.2 despite old env, independent hot route, persistent live menu, pagination, stale/auth guards, no paid selection, no 404 fallback and frozen retry model passed')
asyncio.run(main())
