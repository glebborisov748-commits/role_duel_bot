"""Signed requests to the isolated localhost audit server. No real provider/payments."""
import json,time,hmac,hashlib
from urllib.request import Request,urlopen
from urllib.parse import urlencode
BASE='http://127.0.0.1:8901';UID=7287815074

def call(path,body=None):
 fields={'auth_date':str(int(time.time())),'user':json.dumps({'id':UID})};secret=hmac.new(b'WebAppData',b'123456:TEST_ONLY',hashlib.sha256).digest();fields['hash']=hmac.new(secret,'\n'.join(k+'='+v for k,v in sorted(fields.items())).encode(),hashlib.sha256).hexdigest()
 request=Request(BASE+path,data=json.dumps(body).encode() if body is not None else None,headers={'Content-Type':'application/json','X-Telegram-Init-Data':urlencode(fields)})
 with urlopen(request,timeout=25) as response:return json.load(response)

def create(custom,**extra):return call('/api/app/create',dict(world='anime',gender='female',style='warm',scene='live',custom=custom,**extra))
for tier in (None,'pro'):
 call('/audit/control',{'mode':'onboarding','tier':tier});result=create('Ада Вонг из Resident Evil, самостоятельная оперативница.')
 assert result['ok'];report=call('/audit/report');assert not report['custom_character'] and not report['character_template']
call('/audit/control',{'mode':'onboarding','tier':'super_pro'});result=create('Ада Вонг из Resident Evil, самостоятельная оперативница.')
assert result['ok'];assert call('/audit/report')['character_template']=='ada_wong'

call('/audit/control',{'mode':'onboarding','tier':'super_pro'});result=create('Астарион из Baldurs Gate 3, эльф с серебристыми волосами.')
assert result['ok'];report=call('/audit/report');assert report['custom_character'] and report['app']['character']['gender']=='male'
assert report['app']['character']['appearance']['hair_color']=='silver'
assert not (report['app']['character'].get('avatar_url'))
assert report['photos']==1
result=call('/api/app/send',{'text':'Привет, давай поговорим о приключениях.'});assert result['ok']
for _ in range(40):
 time.sleep(.05)
 if not call('/api/app/state')['state']['pending']:break
result=call('/api/app/photo',{'text':'Фото по последней беседе'});assert result['ok']
for _ in range(40):
 time.sleep(.05)
 if not call('/api/app/state')['state']['photo_pending']:break
report=call('/audit/report');prompt=report['prompts'][-1]
assert 'Astarion' in prompt and 'Gate 3' in prompt and 'portrait' not in prompt.lower(),prompt
assert report['photos']==0
# Own avatars are an icon only and can be uploaded without a subscription.
call('/audit/control',{'mode':'onboarding','tier':None})
png='data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+aJKsAAAAASUVORK5CYII='
result=create('',avatar=png);assert result['ok'] and result['state']['character']['custom_photo']
assert result['state']['photos']['total']==1
assert not call('/api/app/avatar',{'preset':'female_1'})['ok']
print('Signed APIs: SUPER PRO custom gate, known and resolved fiction, source-aware photo prompt, shared photo spending and free own-avatar upload passed')
