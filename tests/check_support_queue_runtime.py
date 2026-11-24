"""Signed support API: real queue ordering, subscription changes and delivery lifecycle."""
import asyncio,hashlib,hmac,json,os,sys,tempfile,time
from datetime import datetime,timedelta
from pathlib import Path
from types import SimpleNamespace
from urllib.parse import urlencode
from unittest.mock import AsyncMock
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
os.environ.update(BOT_TOKEN='123456:TEST_ONLY',PROVOD_API_KEY='FAKE',DATA_DIR=tempfile.mkdtemp(prefix='rd-support-'))
import app
app.bot.send_message=AsyncMock(return_value=SimpleNamespace(message_id=123))
FREE=5255398251;PAID=5255398252;ADMIN=app.SUPPORT_ADMIN_IDS[0]
def setup(uid,paid=False):
 u=app.get_user(uid);u.update(lang='ru',verified=True,agreement_accepted=True,personality_ready=True,gender='female',world='anime',char_name='Аля',style='warm',subscription={'active':paid,'level':'super_pro' if paid else None,'expires_at':(datetime.now()+timedelta(days=7)).isoformat()})
 app.save_data(app.user_data);return u

def request(uid,text):
 fields=dict(auth_date=str(int(time.time())),user=json.dumps(dict(id=uid,first_name='Test')))
 secret=hmac.new(b'WebAppData',os.environ['BOT_TOKEN'].encode(),hashlib.sha256).digest();fields['hash']=hmac.new(secret,'\n'.join(k+'='+v for k,v in sorted(fields.items())).encode(),hashlib.sha256).hexdigest()
 return SimpleNamespace(headers={'X-Telegram-Init-Data':urlencode(fields)},json=AsyncMock(return_value={'text':text}))
async def main():
 free=setup(FREE);paid=setup(PAID,True)
 async def send(uid,text):return json.loads((await app.api_app_support_handler(request(uid,text))).text)
 first=await send(FREE,'Нужна помощь');assert first['ok'] and first['support']['position']==1
 second=await send(PAID,'Помогите с подпиской');assert second['ok'] and second['support']['position']==1
 assert app.serialize_app_state(app.get_user(FREE))['support']['position']==2
 paid=app.get_user(PAID);paid['subscription']['expires_at']=(datetime.now()-timedelta(seconds=1)).isoformat();app.save_data(app.user_data)
 assert app.support_snapshot(FREE)['position']==1
 free=app.get_user(FREE);free['subscription'].update(active=True,level='super_pro',expires_at=(datetime.now()+timedelta(days=7)).isoformat());app.save_data(app.user_data)
 assert app.support_snapshot(FREE)['priority']
 repeat=await send(FREE,'Дополнение');assert repeat['support']['id']==first['support']['id']
 saved=json.loads(Path(app.DATA_FILE).read_text());assert len(saved['__settings__']['support_tickets_v1'])==2
 message=SimpleNamespace(from_user=SimpleNamespace(id=ADMIN),reply_to_message=SimpleNamespace(message_id=123),text='Ответ поддержки',answer=AsyncMock())
 key=f'{ADMIN}:123';app._support_threads()[key]=FREE;app._support_settings()['support_ticket_refs'][key]=first['support']['id']
 app.bot.send_message.reset_mock();await app.support_admin_reply(message);assert app.support_snapshot(FREE) is None;assert app.support_snapshot(PAID)['position']==1
 calls=app.bot.send_message.await_count;await app.support_admin_reply(message);assert app.bot.send_message.await_count==calls
 # Delivered replies have a real reopen button; ownership and replay are enforced.
 markup=app.bot.send_message.await_args.kwargs['reply_markup'];assert markup.inline_keyboard[0][0].callback_data=='support_reopen:'+first['support']['id']
 callback=SimpleNamespace(from_user=SimpleNamespace(id=PAID),data='support_reopen:'+first['support']['id'],answer=AsyncMock(),message=SimpleNamespace(answer=AsyncMock(),edit_reply_markup=AsyncMock()))
 await app.support_reopen_callback(callback);assert app.support_snapshot(FREE) is None
 callback.from_user.id=FREE;await app.support_reopen_callback(callback);reopened=app.support_snapshot(FREE);assert reopened and reopened['id']!=first['support']['id']
 count=len(app.support_queue.active(app._support_settings()));await app.support_reopen_callback(callback);assert len(app.support_queue.active(app._support_settings()))==count
 assert callback.message.edit_reply_markup.await_count==1
 saved=json.loads(Path(app.DATA_FILE).read_text());assert saved['__settings__']['support_tickets_v1'][first['support']['id']]['reopened_as']==reopened['id']
 print('Support API: authenticated submit, current subscription priority, FIFO, merged follow-ups, durable queue, real reply lifecycle and replay prevention passed')
asyncio.run(main())
