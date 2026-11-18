"""Actual browser walkthrough after Telegram consent; local providers and invoices are fake."""
import json,sys
from pathlib import Path
from playwright.sync_api import sync_playwright
BASE='http://127.0.0.1:8769'
OUT=Path('/workspace/role_duel_bot/audit');OUT.mkdir(exist_ok=True)
with sync_playwright() as p:
 browser=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox','--disable-dev-shm-usage'])
 for width in (390,320):
  browser_context=browser.new_context(viewport={'width':width,'height':844},is_mobile=True,has_touch=True)
  browser_context.request.post(BASE+'/__audit__/reset')
  page=browser_context.new_page();errors=[];responses=[];page.on('pageerror',lambda e:errors.append(str(e)));page.on('response',lambda r:responses.append((r.status,r.url)))
  page.goto(BASE+'/app');page.wait_for_selector('#view-onb.on');page.screenshot(path=str(OUT/f'new-{width}-01-world.png'))
  # Five actual onboarding screens: world, gender, appearance/name, personality, mode.
  for step in range(5):
   buttons=page.locator('#view-onb .opt:not(.locked)')
   if buttons.count():buttons.first.click()
   nxt=page.locator('#view-onb').get_by_role('button',name='Дальше',exact=True)
   if nxt.count():nxt.click()
   else:
    done=page.locator('#view-onb').get_by_role('button',name='Создать',exact=False)
    if done.count():done.last.click()
    else:raise AssertionError('No onboarding action: '+page.locator('#view-onb').inner_text())
  page.wait_for_selector('#view-chat.on');page.wait_for_timeout(800)
  # Dismiss the real first-launch tour through its own controls.
  if page.locator('.rd-tour').count():
   skip=page.locator('.rd-tour').get_by_role('button',name='Пропустить',exact=False)
   if skip.count():skip.click()
  page.screenshot(path=str(OUT/f'new-{width}-02-chat.png'))
  page.locator('#input').fill('Привет! Сегодня гулял в парке. Люблю музыку и кофе, а ты?');page.locator('#send').click()
  page.locator('.row.ai .bub').filter(has_text='Рада познакомиться').wait_for();page.wait_for_timeout(450)
  assert not page.locator('#full-screen-msg').is_visible() if page.locator('#full-screen-msg').count() else True
  assert page.locator('#input').is_visible()
  page.screenshot(path=str(OUT/f'new-{width}-03-conversation.png'))
  page.locator('#photo-action').click();page.wait_for_selector('.bub img',timeout=20000)
  page.locator('.bub img').last.click();page.wait_for_selector('.photo-viewer');page.locator('.photo-viewer button').click()
  # All main destinations, actual iframe pages and real backend serializers.
  labels=['Игры','Магазин','Колесо','Работа','Гардероб','Профиль']
  for i,label in enumerate(labels):
   page.locator('#nav button').filter(has_text=label).click();page.wait_for_timeout(900)
   page.screenshot(path=str(OUT/f'new-{width}-{i+4:02d}-{label}.png'))
   assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
  page.get_by_role('button',name='Подписки и покупки',exact=True).click();page.wait_for_selector('#sheet.on .photo-pack')
  page.screenshot(path=str(OUT/f'new-{width}-10-purchases.png'))
  assert page.locator('.photo-pack').count()==3
  assert 'Без подписки' not in page.locator('#sheet-box').inner_text()
  page.goto(BASE+'/work?game=clicker');page.wait_for_selector('#tabs');page.wait_for_timeout(400)
  if page.locator('#tab-clicker').is_visible():
   page.evaluate('Math.random=()=>0.4');page.locator('#tab-clicker').click();page.wait_for_timeout(250)
   assert 'Соедини одинаковые контакты' in page.locator('#hacker-mode').inner_text()
   colors=page.locator('.hacker-wire-end').evaluate_all('(xs)=>xs.map(x=>getComputedStyle(x).backgroundColor)');assert len(set(colors))==4,colors
   for index,color in enumerate(colors):
    page.locator('.hacker-wire-end').nth(index).click()
    sockets=page.locator('.hacker-wire-socket').evaluate_all('(xs)=>xs.map(x=>getComputedStyle(x).backgroundColor)')
    page.locator('.hacker-wire-socket').nth(sockets.index(color)).click()
   page.wait_for_timeout(350);page.screenshot(path=str(OUT/f'new-{width}-11-wires.png'))
  assert not errors,errors
  bad=[(code,url) for code,url in responses if code>=400 and '/api/' in url]
  assert not bad,bad
  print('New-user walkthrough passed',width,'requests',len(responses))
  browser_context.close()
 browser.close()
