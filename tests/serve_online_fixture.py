"""Local fixture server with real Telegram HMAC authentication and isolated fake accounts."""
import os
import tempfile
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
os.environ.update(BOT_TOKEN='123456:TEST_ONLY_NOT_A_REAL_TOKEN',PROVOD_API_KEY='test-only',DATA_DIR=tempfile.mkdtemp())
import app
import json
import hmac
import hashlib
import time
from urllib.parse import urlencode
from aiohttp import web

app._BOT_USERNAME['v']='fixture_bot'
tokens={}
for uid in (1,2,3):
    user=app.get_user(uid)
    user.update(verified=True,agreement_accepted=True,personality_ready=True,world='anime',gender='female',style='warm',lang='ru',bucks=1000)
    user['subscription']={'active':True,'level':'super_pro','expires_at':'2099-01-01T00:00:00'}
    fields={'auth_date':str(int(time.time())),'user':json.dumps({'id':uid,'first_name':'Fixture'})}
    secret=hmac.new(b'WebAppData',os.environ['BOT_TOKEN'].encode(),hashlib.sha256).digest()
    fields['hash']=hmac.new(secret,'\n'.join(k+'='+v for k,v in sorted(fields.items())).encode(),hashlib.sha256).hexdigest()
    tokens[str(uid)]=urlencode(fields)
from types import SimpleNamespace
async def prepared_share(**kwargs):return SimpleNamespace(id='prepared_fixture')
app.bot.save_prepared_inline_message=prepared_share
app.save_data(app.user_data)
async def manifest(request):return web.json_response({'tokens':tokens})
async def inspect(request):return web.json_response({'rooms':app.online_store(),'users':{k:v for k,v in app.user_data.items() if k!='__settings__'}})
site=web.Application()
site.router.add_get('/online',app.online_page_handler)
site.router.add_get('/play',app.play_page_handler)
site.router.add_post('/api/online',app.api_online_handler)
site.router.add_post('/api/app/share',app.api_app_share_handler)
site.router.add_get('/api/play/state',app.api_play_state_handler)
site.router.add_post('/api/play/start',app.api_play_start_handler)
site.router.add_get('/sfx.js',app.sfx_js_handler)
site.router.add_get('/theme.css',app.theme_css_handler)
site.router.add_get('/assets/audio/{name}',app.audio_sample_handler)
site.router.add_static('/assets/',app.ASSETS_DIR)
site.router.add_get('/fixture',manifest)
site.router.add_get('/inspect',inspect)
web.run_app(site,host='127.0.0.1',port=8767,print=None)
