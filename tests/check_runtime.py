"""Import the real app with temporary data and fake credentials. Never runs polling."""
import asyncio
import os
from pathlib import Path
import sys
import tempfile
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
for key in list(os.environ):
    if key.lower().endswith('_proxy'):
        os.environ.pop(key)
os.environ.update(BOT_TOKEN='123456:TEST_ONLY_NOT_A_REAL_TOKEN', PROVOD_API_KEY='test-only', DATA_DIR=tempfile.mkdtemp())
import app

u = app.get_user(123456)
u.update(lang='ru', verified=True, agreement_accepted=True, personality_ready=True,
         world='realism', gender='female', style='warm', scene='phone',
         history=[{'role':'user','content':'Привет, как прошёл день?'}])
state = app.serialize_app_state(u)
assert state['messages'][0]['id']
assert [pack['stars'] for pack in state['bucks_packs']] == [10, 18, 35]
assert state['settings']['lang'] == 'ru'
assert isinstance(app.build_prompt(u), str)

class Message:
    from_user = type('User', (), {'id':123456})()
    chat = type('Chat', (), {'id':123456})()
    successful_payment = type('Payment', (), {
        'invoice_payload':'bucks_5000', 'telegram_payment_charge_id':'test-charge-1',
        'currency':'XTR', 'total_amount':10,
    })()
    async def answer(self, *args, **kwargs):
        pass

u['first_purchase_done'] = True
start = u['bucks']
async def check():
    await app.payment_success(Message())
    await app.payment_success(Message())
    assert u['bucks'] == start + 5000
    await app.bot.session.close()

asyncio.run(check())
print('Real import, state serialization and duplicate Stars delivery passed; no network requests')

fresh = app.get_user(99887766)
assert fresh['subscription'] == {'active': False, 'expires_at': None, 'level': None}
assert app.get_subscription_level(fresh) is None
u['lang'] = 'de'
assert app.serialize_app_state(u)['ui']['tab_spin'] == 'Glücksrad'
assert app.at(u, 'sub_none') == 'Kein Abonnement'
assert app.serialize_onboarding(u)['scenes'][0]['label'] == 'Nachrichten'
print('Fresh accounts have no subscription; German state and onboarding passed')

u['scene']='phone'
prompt=app.build_prompt(u)
assert 'Каждое действие в *звёздочках*' not in prompt
assert app.conversation_mode_rule(u) in prompt
u['custom_character']='A friendly neighbour who enjoys books.'
assert app.build_prompt(u).endswith(app.conversation_mode_rule(u))
assert app.clean_chat_reply('2*3*5',u)=='2*3*5'
print('Phone mode is applied to ordinary and custom companions')
