"""Real mobile layout checks for the release: menus, tutorial, gifts and quests."""
import copy
import json
from pathlib import Path
from playwright.sync_api import sync_playwright
from ui_fixture import constants, state as initial, ROOT

with sync_playwright() as p:
    browser=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox','--disable-dev-shm-usage'])
    for width,height in [(320,640),(390,844),(430,932)]:
        state=copy.deepcopy(initial)
        state['messages']=[{'id':'a1','role':'assistant','text':'Длинный ответ.\n'*60}]
        calls=[];errors=[]
        page=browser.new_page(viewport={'width':width,'height':height},is_mobile=True,has_touch=True)
        page.on('pageerror',lambda e:errors.append(str(e)))
        def route(r):
            path=r.request.url.split('roleduel.test')[-1].split('?')[0]
            if path=='/app':return r.fulfill(content_type='text/html',body=constants['APP_PAGE_HTML'].replace('<head>','<head><script src="/sfx.js"></script><link rel="stylesheet" href="/theme.css">',1))
            if path=='/sfx.js':return r.fulfill(content_type='application/javascript',body=constants['SFX_JS'])
            if path=='/theme.css':return r.fulfill(content_type='text/css',body=constants['APP_THEME_CSS'])
            if path=='/tg-sdk.js':return r.fulfill(content_type='application/javascript',body='window.Telegram={WebApp:{initData:"fixture",ready(){},expand(){},setHeaderColor(){},setBackgroundColor(){},disableVerticalSwipes(){},BackButton:{hide(){}},showConfirm(t,c){c(true)},HapticFeedback:{impactOccurred(){},selectionChanged(){},notificationOccurred(){}}}};')
            if path.startswith('/assets/'):
                file=ROOT/path.lstrip('/')
                return r.fulfill(path=str(file)) if file.is_file() else r.fulfill(status=404,body='')
            if path.startswith('/api/'):
                body=r.request.post_data_json if r.request.method=='POST' else {}
                calls.append((path,body))
                if path=='/api/app/message':
                    m=next(m for m in state['messages'] if m['id']==body['id'])
                    m['user_reaction']=body['emoji'];m['reaction_animated']=True
                if path=='/api/app/settings':state['settings'].update(body)
                if path=='/api/app/task':
                    q=next(q for q in state['quests']['items'] if q['id']==body['id']);q['claimed']=True
                return r.fulfill(content_type='application/json',body=json.dumps({'ok':True,'state':state},ensure_ascii=False))
            if path=='/guide':return r.fulfill(body='Help')
            return r.fulfill(status=404,body='')
        page.route('**/*',route);page.goto('https://roleduel.test/app')
        assert page.locator('#ebar').count()==0
        page.locator('.bub').dispatch_event('contextmenu',{'clientX':80,'clientY':250})
        menu=page.locator('#message-menu-box');menu.wait_for();page.wait_for_timeout(200)
        box=menu.bounding_box();assert box['y']>=250,(width,box)
        assert box['y']+box['height']<=height+1,(width,box)
        page.get_by_role('button',name='💖 PRO',exact=True).click()
        page.locator('.rd-user-react.rd-premium').wait_for()
        assert page.locator('.bub .rd-user-react').count()==1
        state['messages']=[{'id':'gift','role':'user','text':'gift','card':{'kind':'gift','name':'Шоколадка','emoji':'🍫'}}]
        page.reload();page.locator('.giftcard').dispatch_event('contextmenu')
        assert page.locator('#message-menu').is_hidden()
        page.locator('#nav button').nth(5).click()
        assert page.locator('.rd-quest').count()==2
        page.get_by_role('button',name='Забрать',exact=True).click()
        page.get_by_role('button',name='Получено',exact=True).wait_for()
        claim=next(body for path,body in calls if path=='/api/app/task')
        assert claim=={'id':'courier10','day':'2026-11-14'}
        page.get_by_role('button',name=state['ui']['guide_btn'],exact=True).click()
        page.get_by_role('button',name='Показать, что где находится',exact=True).click()
        for _ in range(7):page.locator('.rd-tour').get_by_role('button',name='Далее',exact=True).click()
        page.wait_for_timeout(300)
        panel=page.locator('.rd-tour-panel').bounding_box()
        target=page.locator('#view-profile .hero .hero-btns').first.bounding_box()
        overlap=max(0,min(panel['y']+panel['height'],target['y']+target['height'])-max(panel['y'],target['y']))
        assert overlap<1,(width,panel,target)
        assert 'Баксы и покупки' not in page.locator('.rd-tour').inner_text()
        page.screenshot(path='/tmp/rd-release-guide-'+str(width)+'.png')
        assert not errors,errors
        print('Mobile release passed:',width,height)
        page.close()
    browser.close()
