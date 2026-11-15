"""Mobile pin lock: torque, binding pin, recovery and completion."""
import json
from pathlib import Path
from playwright.sync_api import sync_playwright
from ui_fixture import constants,ROOT
state=json.loads(Path('/tmp/rd-work.json').read_text())
with sync_playwright() as p:
    browser=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox','--disable-dev-shm-usage'])
    for width in (320,390,430):
        page=browser.new_page(viewport={'width':width,'height':844},is_mobile=True,has_touch=True)
        errors=[];hits=[]
        page.on('pageerror',lambda e:errors.append(str(e)))
        def route(r):
            path=r.request.url.split('roleduel.test')[-1].split('?')[0]
            if path=='/work':
                html=constants['WORK_PAGE_HTML'].replace('var lockState=null;',"var lockState=null;window.__lockFixture={get:function(){return lockState;},begin:function(){hackerMode='lock';document.getElementById('hacker-mode').textContent=state.ui.hack_mode_lock;document.getElementById('hacker-wires').classList.remove('active');document.getElementById('hacker-keyboard').style.display='none';document.getElementById('hacker-code').style.display='none';startLockpick();}};")
                return r.fulfill(content_type='text/html',body=html.replace('<head>','<head><link rel="stylesheet" href="/theme.css"><script src="/sfx.js"></script>',1))
            if path=='/sfx.js':return r.fulfill(content_type='application/javascript',body=constants['SFX_JS'])
            if path=='/theme.css':return r.fulfill(content_type='text/css',body=constants['APP_THEME_CSS'])
            if path=='/tg-sdk.js':return r.fulfill(content_type='application/javascript',body='window.__tgSdkSettled=true;window.Telegram={WebApp:{initData:"fixture",ready(){},expand(){},HapticFeedback:{impactOccurred(){},selectionChanged(){},notificationOccurred(){}}}};')
            if path.startswith('/assets/audio/'):return r.fulfill(path=str(ROOT/path.lstrip('/')))
            if path=='/api/work/hit':hits.append(r.request.post_data_json)
            if path.startswith('/api/'):return r.fulfill(content_type='application/json',body=json.dumps({'ok':True,'state':state,'awarded':110,'lost':40,'seconds':1}))
            return r.fulfill(status=404,body='')
        page.route('**/*',route);page.goto('https://roleduel.test/work');page.locator('#tab-clicker').click()
        page.evaluate('window.__lockFixture.begin();window.__played=[];RDSFX.game=function(k){window.__played.push(k)};')
        def slider(selector,value):
            page.locator(selector).evaluate('(n,v)=>{n.value=v;n.dispatchEvent(new Event("input",{bubbles:true}));}',value)
        target=page.evaluate('(()=>{let s=__lockFixture.get();return {pin:s.order[0],height:s.targets[s.order[0]]};})()')
        page.locator('.lock-pin').nth(target['pin']).click();slider('#lock-lift',target['height']);page.locator('#hacker-lock-btn').click()
        assert page.evaluate('__lockFixture.get().set.length')==0
        slider('#lock-tension',35);page.locator('#hacker-lock-btn').click()
        assert page.evaluate('__lockFixture.get().set.length')==1
        target=page.evaluate('__lockFixture.get().order[1]')
        page.locator('.lock-pin').nth(target).click();slider('#lock-tension',80);page.locator('#hacker-lock-btn').click()
        assert page.evaluate('__lockFixture.get().health')==2
        slider('#lock-tension',0);assert page.evaluate('__lockFixture.get().set.length')==0
        slider('#lock-tension',35)
        assert page.locator('#hacker-lock-btn').inner_text()=='Проверить пин'
        pins=page.evaluate('__lockFixture.get().pins')
        for _ in range(pins):
            target=page.evaluate('(()=>{let s=__lockFixture.get(),p=s.order[s.set.length];return {pin:p,height:s.targets[p]};})()')
            page.locator('.lock-pin').nth(target['pin']).click();slider('#lock-lift',target['height']);page.locator('#hacker-lock-btn').click()
        page.wait_for_timeout(350);assert len(hits)==1,hits
        assert hits[0]['game']=='hacker_combo'
        assert 'unlock' in page.evaluate('__played')
        assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1')
        page.screenshot(path=f'/tmp/rd-lock-{width}.png')
        assert not errors,errors
        page.close();print('Pin lock passed:',width)
    browser.close()
