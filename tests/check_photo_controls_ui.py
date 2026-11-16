"""Mobile UI: compact photo hint, awake energizer, paired subscription terms and scene portrait polling."""
import copy
import json
from playwright.sync_api import sync_playwright
from ui_fixture import constants,state as initial,ROOT

with sync_playwright() as p:
    browser=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox','--disable-dev-shm-usage'])
    for width in (320,390,430):
        state=copy.deepcopy(initial);state['subscription']={'level':None,'title':None,'until':None}
        state['stats'].update(energy=150,energy_max=150,energizers=2,energizer_restore=78)
        state['offers']=[]
        for payload,name,price,week in [('subscribe_pro','PRO',220,75),('subscribe_super','SUPER PRO',500,170),('subscribe_elite','ELITE',1000,340)]:
            base={'payload':payload,'title':name,'perks':['Test benefit'],'stars':price,'stars_label':str(price),'rub':None,'emoji':'✨'}
            state['offers'].extend([base,{**base,'payload':payload+'_week','title':name+' · 7 дней','stars':week,'stars_label':str(week)}])
        state['hot']={'available':2,'allowed':True,'sick':False,'pending':False,'photo_pending':False,'photo_option':{'enabled':True,'can_afford':True,'cost':40},'last':None,'price':'60','types':[{'key':'test','label':'Спокойный вечер'}],'locations':{'test':[{'key':'any','label':'Любое место'}]},'dominants':[{'key':'any','label':'Любой'}]}
        calls=[];errors=[];ready=[False]
        page=browser.new_page(viewport={'width':width,'height':844},is_mobile=True,has_touch=True)
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
                if path=='/api/app/wake':state['stats']['energy']=min(150,state['stats']['energy']+78);state['stats']['energizers']-=1
                if path=='/api/app/hot/start':
                    state['stats']['energy']-=40;state['hot']['photo_pending']=True
                    state['hot']['last']={'text':'Тихий вечер в кафе.','parts':1,'footer':'Кафе','photo_status':'pending','photo':None}
                if path=='/api/app/state' and ready[0]:
                    state['hot']['photo_pending']=False;state['hot']['last'].update(photo='/assets/avatar_real_f1.jpg',photo_status='ready')
                return r.fulfill(content_type='application/json',body=json.dumps({'ok':True,'state':state}))
            return r.fulfill(status=404,body='')
        page.route('**/*',route);page.goto('https://roleduel.test/app')
        page.locator('#photo-action').wait_for()
        assert page.locator('#photo-request').count()==0
        assert page.locator('#energy-action').is_disabled()
        state['stats']['energy']=90;page.reload();page.locator('#photo-action').wait_for()
        page.locator('#energy-action').click()
        page.wait_for_function("document.querySelector('#h-en').textContent.includes('150')")
        assert state['stats']['energizers']==1
        page.locator('#nav button').nth(5).click()
        assert page.locator('#view-profile .tier').count()==3
        rows=page.locator('.rd-sub-terms');assert rows.count()==3
        for i in range(3):
            assert rows.nth(i).locator('button').nth(0).get_attribute('data-payload').endswith('_week')
            assert not rows.nth(i).locator('button').nth(1).get_attribute('data-payload').endswith('_week')
        assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1')
        page.locator('#h-hot').click()
        page.get_by_role('button',name='Спокойный вечер',exact=True).click()
        page.get_by_role('button',name=state['ui']['hot_go'],exact=True).click()
        page.get_by_text('Тихий вечер в кафе.',exact=True).wait_for()
        assert page.locator('.rd-scene-photo').count()==0
        assert page.get_by_role('button',name=state['ui']['hot_continue'],exact=True).is_disabled()
        start=[body for path,body in calls if path=='/api/app/hot/start']
        assert len(start)==1 and start[0]['photo'] is True
        ready[0]=True
        page.locator('.rd-scene-photo').wait_for(timeout=6000)
        assert page.locator('.rd-scene-photo').count()==1
        page.wait_for_timeout(350)
        page.screenshot(path=f'/tmp/rd-scene-photo-{width}.png')
        assert not errors,errors
        page.close();print('Photo and subscription controls passed:',width)
    browser.close()
