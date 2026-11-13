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
