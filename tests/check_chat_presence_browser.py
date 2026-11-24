"""Fixed receipt timing, simulated presence, stale poll fencing and stable message layout."""
import time
from playwright.sync_api import sync_playwright
BASE='http://127.0.0.1:8901'
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox']);errors=[]
 for width in (320,390,430):
  p=b.new_page(viewport={'width':width,'height':844});p.on('pageerror',lambda e:errors.append(str(e)));p.request.post(BASE+'/audit/control',data={'mode':'chat','chat_long':True});p.goto(BASE+'/app');p.wait_for_selector('#input');p.wait_for_function("document.querySelector('#h-ava').dataset.presence==='online'")
  old_count=p.locator('#msgs .row.ai[data-message-id]').count();p.evaluate("window.clockOffset=16000;window.realNow=Date.now;Date.now=()=>window.realNow()+window.clockOffset");p.wait_for_function("document.querySelector('#h-ava').dataset.presence==='offline'");assert p.locator('#h-status').inner_text()=='не в сети';p.wait_for_function("getComputedStyle(document.querySelector('#h-ava .dot')).backgroundColor==='rgb(121, 128, 140)'")
  held=[]
  def hold(route):held.append((route,route.fetch()))
  p.route('**/api/app/state',hold);p.locator('#nav [data-tab="chat"]').click();p.wait_for_timeout(100);assert held
  p.evaluate('window.stableRow=document.querySelector("#msgs .row.ai[data-message-id]")');p.locator('#input').fill('Проверяю спокойное прочтение сообщения');start=time.monotonic();p.locator('#send').click();p.wait_for_selector('.read-eye.closed')
  for route,response in held:route.fulfill(response=response)
  p.unroute('**/api/app/state',hold);p.wait_for_timeout(700);assert p.locator('#h-ava').get_attribute('data-presence')=='offline';assert p.locator('.read-eye.closed').count()==1;assert p.locator('.receipt-typing-slot.visible').count()==0
  # The provider has already answered; presentation must keep its own timetable.
  report=p.request.get(BASE+'/audit/report').json();assert report['history'][-1]['role']=='assistant';assert p.locator('#msgs .row.ai[data-message-id]').count()==old_count
  p.evaluate("window.layoutSamples=[];window.sampleUntil=performance.now()+2900;function sample(){let r=Array.from(document.querySelectorAll('#msgs .row.me')).pop().getBoundingClientRect();window.layoutSamples.push([r.y,document.querySelector('#msgs').scrollTop,document.querySelector('#composer').getBoundingClientRect().y]);if(performance.now()<window.sampleUntil)requestAnimationFrame(sample);}requestAnimationFrame(sample)")
  p.wait_for_function("document.querySelector('#h-ava').dataset.presence==='online'",timeout=2300);assert p.locator('.read-eye.closed').count()==1;assert p.locator('.receipt-typing-slot.visible').count()==0
  p.wait_for_selector('.read-eye.open',timeout=2200);assert p.locator('.receipt-typing-slot.visible').count()==0
  p.wait_for_timeout(100);samples=p.evaluate('window.layoutSamples');assert max(x[0] for x in samples)-min(x[0] for x in samples)<2,(width,samples[:2],samples[-2:]);assert max(x[2] for x in samples)-min(x[2] for x in samples)<2
  assert p.evaluate('window.stableRow.isConnected'),width
  p.evaluate("document.querySelector('#msgs').scrollTop-=450;window.readerPosition=document.querySelector('#msgs').scrollTop")
  p.wait_for_selector('.receipt-typing-slot.visible',timeout=1800);assert p.locator('.read-eye.open').count()==1
  p.wait_for_function('count=>document.querySelectorAll("#msgs .row.ai[data-message-id]").length===count+1',arg=old_count,timeout=2500);assert time.monotonic()-start>=4.65;assert p.locator('.read-eye').count()==0
  assert abs(p.evaluate("document.querySelector('#msgs').scrollTop-window.readerPosition"))<2;assert p.evaluate('window.stableRow.isConnected');assert p.locator('#msgs .bub').first.evaluate('(e)=>getComputedStyle(e).animationName')=='none'
  p.evaluate('window.clockOffset+=16000');p.wait_for_function("document.querySelector('#h-ava').dataset.presence==='offline'");assert p.locator('#h-status').inner_text()=='не в сети'
  if width==390:p.screenshot(path='/tmp/chat-presence.png')
  p.close()
 assert not errors,errors;b.close();print('Chat presence: 320/390/430, 15s idle/gray dot, delayed online, long closed-eye/read/typing phases, provider runs immediately, fast answer held only visually, stale poll ignored, existing rows and manual scroll preserved, no composer/message jitter passed')
