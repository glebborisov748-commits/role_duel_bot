"""Two real browser clients against the real authenticated online endpoint."""
import json
from pathlib import Path
import subprocess
import time
import tempfile
import urllib.request
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
# Access logs must not fill an unread PIPE and block the fixture event loop.
server_log=tempfile.TemporaryFile()
server=subprocess.Popen(['/tmp/roleduel-venv/bin/python',str(ROOT/'tests/serve_online_fixture.py')],stdout=subprocess.DEVNULL,stderr=server_log)
base='http://127.0.0.1:8767'
def get(path):return json.load(urllib.request.urlopen(base+path,timeout=3))
try:
    for _ in range(200):
        try:manifest=get('/fixture');break
        except Exception:time.sleep(.1)
    else:raise AssertionError('fixture server did not start')
    with sync_playwright() as p:
        browser=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox','--disable-dev-shm-usage'])
        errors=[];contexts=[];pages=[]
        for uid in ('1','2'):
            context=browser.new_context(viewport={'width':390,'height':844},is_mobile=True,has_touch=True)
            sdk='window.__tgSdkSettled=true;window.Telegram={WebApp:{initData:'+json.dumps(manifest['tokens'][uid])+',ready(){},expand(){},setHeaderColor(){},setBackgroundColor(){},showConfirm(t,c){c(true)},HapticFeedback:{impactOccurred(){},selectionChanged(){},notificationOccurred(){}},BackButton:{show(){},hide(){},onClick(){}},openTelegramLink(url){window.__shared=url},shareMessage(id){window.__shared=id},isVersionAtLeast(){return true}}};'
            context.route('**/telegram.org/js/**',lambda r,request,sdk=sdk:r.fulfill(content_type='application/javascript',body=sdk))
            context.route('**/tg-sdk.js',lambda r,request,sdk=sdk:r.fulfill(content_type='application/javascript',body=sdk))
            page=context.new_page();page.on('pageerror',lambda exc:errors.append(str(exc)))
            page.goto(base+'/online?game=connect4');page.locator('#game-select').wait_for()
            assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1')
            contexts.append(context);pages.append(page)
        first,second=pages
        first.locator('#bet').select_option('100');first.get_by_role('button',name='Позвать друга',exact=True).click()
        first.get_by_text('Ждём второго игрока',exact=True).wait_for()
        room=next(iter(get('/inspect')['rooms'].values()));code=room['id']
        assert room['bet']==100
        first.get_by_role('button',name='Отправить приглашение',exact=True).click();first.wait_for_function("window.__shared==='prepared_fixture'")
        first.evaluate('window.Telegram.WebApp.shareMessage=null');first.get_by_role('button',name='Отправить приглашение',exact=True).click();first.wait_for_function("window.__shared.startsWith('https://t.me/share/url?')")
        assert 'match_'+code in first.evaluate('decodeURIComponent(window.__shared)')
        second.locator('#invite').fill(code);second.get_by_role('button',name='Посмотреть комнату',exact=True).click()
        second.locator('.board.c4').wait_for();first.locator('.board.c4').wait_for()
        for col in (0,1,0,1,0,1,0):
            room=get('/inspect')['rooms'][code];turn=room['turn']
            active=pages[turn]
            active.get_by_text('Твой ход',exact=True).wait_for()
            active.locator('.board.c4 button').nth(35+col).click()
            active.wait_for_function('s=>document.querySelectorAll(".cell.red,.cell.yellow").length>=s',arg=sum(bool(x) for row in room['board'] for x in row)+1)
            time.sleep(.15)
        winner=get('/inspect')['rooms'][code]['winner'];pages[winner].get_by_text('Победа!',exact=True).wait_for()
        data=get('/inspect');assert data['users'][str(winner+1)]['bucks']==1100
        assert data['users'][str(2-winner)]['bucks']==900
        # A reload resumes the settled result, without paying the pot again.
        pages[winner].reload();pages[winner].get_by_text('Победа!',exact=True).wait_for()
        assert get('/inspect')['users'][str(winner+1)]['bucks']==1100
        # A third authenticated account cannot issue moves in another player's room.
        body=json.dumps({'action':'move','room':code,'seq':0,'move':{'column':2}}).encode()
        request=urllib.request.Request(base+'/api/online',data=body,headers={'Content-Type':'application/json','X-Telegram-Init-Data':manifest['tokens']['3']})
        assert json.load(urllib.request.urlopen(request))['error']=='not_member'
        for page in pages:page.get_by_role('button',name='В меню',exact=True).click();page.locator('#game-select').wait_for()
        # Random matchmaking, RPS hidden simultaneous choices, and active reload recovery.
        for page in pages:
            page.locator('#game-select').select_option('rps');page.get_by_role('button',name='Найти соперника',exact=True).click()
        first.get_by_text('Сделай тайный выбор',exact=True).wait_for();second.get_by_text('Сделай тайный выбор',exact=True).wait_for()
        first.get_by_role('button',name='🪨',exact=True).click();first.get_by_text('Выбор принят. Ждём соперника.',exact=True).wait_for()
        first.reload();first.get_by_text('Выбор принят. Ждём соперника.',exact=True).wait_for()
        assert second.get_by_text('Сделай тайный выбор',exact=True).is_visible()
        second.get_by_role('button',name='✌️',exact=True).click();first.get_by_text('Счёт 1 : 0',exact=True).wait_for()
        first.screenshot(path='/tmp/rd-online-rps.png');second.screenshot(path='/tmp/rd-online-opponent.png')
        assert not errors,errors
        # Chess renders legal moves and a computer response; dice renders a private hand.
        first.get_by_role('button',name='Сдаться и выйти',exact=True).click()
        try:first.locator('#game-select').wait_for(timeout=5000)
        except Exception:
            print('LEAVE DEBUG:',first.locator('body').inner_text(),'ERRORS',errors,'USER',get('/inspect')['users']['1'].get('online_room'),flush=True);raise
        first.locator('#game-select').select_option('chess')
        first.get_by_role('button',name='С персонажем · легко · бесплатно',exact=True).click()
        first.locator('.board.chess').wait_for()
        assert first.locator('.square').count()==64
        first.get_by_role('button',name='e2 P',exact=True).click()
        first.get_by_role('button',name='e4',exact=True).click()
        first.get_by_role('button',name='e4 P',exact=True).wait_for()
        first.screenshot(path='/tmp/rd-online-chess.png')
        first.get_by_role('button',name='Сдаться и выйти',exact=True).click()
        first.locator('#game-select').select_option('dice')
        first.get_by_role('button',name='С персонажем · легко · бесплатно',exact=True).click()
        first.locator('.dice').wait_for()
        assert len(first.locator('.dice').inner_text())==5
        first.screenshot(path='/tmp/rd-online-dice.png')
        # Removed blackjack is absent and rejected server-side.
        first.goto(base+'/play');
        try:first.get_by_role('heading',name='🎲 Liar’s Dice').wait_for(timeout=8000)
        except Exception:
            print('PLAY BODY:',first.locator('body').inner_text(),'ERRORS',errors);raise
        assert first.get_by_text('Блэкджек',exact=False).count()==0
        body=json.dumps({'mode':'bj','bet':100}).encode()
        request=urllib.request.Request(base+'/api/play/start',data=body,headers={'Content-Type':'application/json','X-Telegram-Init-Data':manifest['tokens']['1']})
        assert not json.load(urllib.request.urlopen(request))['ok']
        print('Two authenticated browser clients: invite, escrow, Connect Four victory, restart, random RPS, hidden choices and blackjack retirement passed')
        browser.close()
finally:
    server.terminate()
    try:server.wait(timeout=5)
    except subprocess.TimeoutExpired:server.kill()
    server_log.seek(0);log=server_log.read().decode();server_log.close()
    if 'Traceback' in log:print(log[-4000:])
