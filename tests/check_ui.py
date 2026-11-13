"""Offline mobile browser regression checks; Telegram and APIs are fixtures."""
import ast
import copy
import json
from pathlib import Path
from playwright.sync_api import sync_playwright

from ui_fixture import ROOT, constants, ui, state
requests=[]

def route(req):
    url = req.request.url.split('roleduel.test')[-1].split('?')[0]
    if url.startswith('/assets/'):
        file=ROOT/url.lstrip('/')
        if file.is_file(): return req.fulfill(path=str(file))
        return req.fulfill(status=404,body='')
    if url=='/tg-sdk.js':
        return req.fulfill(content_type='application/javascript',body='window.Telegram={WebApp:{initData:"fixture",platform:"web",ready(){},expand(){},setHeaderColor(){},setBackgroundColor(){},disableVerticalSwipes(){},BackButton:{hide(){}},showConfirm(t,cb){cb(true)},HapticFeedback:{selectionChanged(){},notificationOccurred(){},impactOccurred(){}}}};')
    if url=='/sfx.js': return req.fulfill(content_type='application/javascript',body=constants['SFX_JS'])
    if url=='/theme.css': return req.fulfill(content_type='text/css',body=constants['APP_THEME_CSS'])
    if url=='/app': return req.fulfill(content_type='text/html',body=constants['APP_PAGE_HTML'].replace('<head>','<head><script src="/sfx.js"></script>',1))
    if url=='/guide': return req.fulfill(content_type='text/html',body='<h1>Справка</h1>')
    if url.startswith('/api/'):
        body=req.request.post_data_json if req.request.method=='POST' else {}
        requests.append((url,body))
        if url=='/api/app/settings':
            state['settings'].update(body)
            if 'lang' in body: state['ui']=constants['APP_TEXTS'][body['lang']]
        if url=='/api/app/message':
            m=next(m for m in state['messages'] if m['id']==body['id'])
            if body['action']=='edit': m.update(text=body['text'],edited=True)
            if body['action']=='delete': state['messages'].remove(m)
            if body['action']=='react': m['user_reaction']=None if m.get('user_reaction')==body['emoji'] else body['emoji']
        return req.fulfill(content_type='application/json',body=json.dumps({'ok':True,'state':state},ensure_ascii=False))
    return req.fulfill(status=404,body='')

with sync_playwright() as p:
    browser=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox','--no-zygote','--single-process','--disable-dev-shm-usage'])
    page=browser.new_page(viewport={'width':390,'height':844},device_scale_factor=1,has_touch=True,is_mobile=True)
    errors=[];page.on('pageerror',lambda err: errors.append(str(err)))
    page.route('**/*',route)
    page.goto('https://roleduel.test/app');page.get_by_text('Привет, как прошёл твой день?',exact=True).wait_for()
    bubble=page.get_by_text('Привет, как прошёл твой день?',exact=True)
    box=bubble.bounding_box();page.mouse.move(box['x']+10,box['y']+10);page.mouse.down();page.wait_for_timeout(600);page.mouse.up()
    page.get_by_role('button',name='Редактировать',exact=True).click()
    page.locator('#sheet-box textarea').fill('Отредактированное сообщение')
    page.get_by_role('button',name='Сохранить',exact=True).click()
    page.get_by_text('Отредактированное сообщение',exact=True).wait_for()
    page.get_by_text('Привет! Рада тебя видеть.',exact=True).dispatch_event('contextmenu')
    page.locator('#sheet-box').get_by_role('button',name='❤️',exact=True).click()
    page.locator('.rd-user-react').wait_for()
    page.locator('#nav button').nth(5).click()
    page.get_by_text('Пополнить баксы',exact=True).wait_for()
    assert page.locator('#view-profile ul').first.inner_text()
    assert page.get_by_text('Доверие',exact=True).is_visible() or page.get_by_text('Доверие',exact=True).count()
    page.screenshot(path='/tmp/roleduel-profile.png',full_page=True)
    page.get_by_role('button',name=ui['guide_btn'],exact=True).click()
    page.locator('iframe.rd-guide').wait_for()
    page.get_by_role('button',name='Показать, что где находится',exact=True).click()
    for step in range(11):
        assert page.locator('.rd-tour .note').inner_text() == f'{step + 1} / 12'
        page.locator('.rd-tour').get_by_role('button',name='Далее',exact=True).click()
    page.locator('.rd-tour').get_by_role('button',name='Назад',exact=True).click()
    assert page.locator('.rd-tour .note').inner_text() == '11 / 12'
    page.get_by_role('button',name='Пропустить',exact=True).click()
    page.locator('#nav button').nth(5).click()
    page.locator('select').first.select_option('en')
    page.locator('label').filter(has_text='Conversation mode').wait_for()
    page.locator('select').nth(1).select_option('live')
    page.wait_for_timeout(100)
    assert state['settings']['scene']=='live'
    assert not errors,errors
    print('Mobile UI: hold/edit, reactions, profile/perks, currency packs, embedded help, tour and language/mode passed')
    browser.close()
