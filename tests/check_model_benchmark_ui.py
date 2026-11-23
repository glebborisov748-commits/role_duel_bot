"""Offline report UI and script-injection regression. All model replies are mocked."""
import sys,asyncio,json,re,tempfile
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import httpx,model_benchmark as bench
from playwright.sync_api import sync_playwright
ROOT=Path(tempfile.mkdtemp(prefix='rd-bench-ui-'))

def handler(request):
 if request.method=='GET':return httpx.Response(200,json={'data':[dict(id=m.canonical.split('/')[-1],canonical_slug=m.canonical) for m in bench.MODELS]})
 body=json.loads(request.content)
 return httpx.Response(200,json={'model':body['model'],'choices':[{'message':{'content':'ТЕСТОВЫЙ ОБРАЗЕЦ, НЕ ОТВЕТ МОДЕЛИ. </script><img src=x onerror="window.pwned=1">'},'finish_reason':'stop'}],'usage':{'prompt_tokens':1000,'completion_tokens':100}})
async def create():return await bench.run('FAKE_TEST',output_dir=ROOT,transport=httpx.MockTransport(handler),seed=1)
report=asyncio.run(create());assert not report['live_requests']
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox']);page=b.new_page(viewport={'width':390,'height':844});errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
 page.route('http://benchmark.test/**',lambda route:route.fulfill(status=200,content_type='text/html',body=(ROOT/'comparison.html').read_text()))
 page.goto('http://benchmark.test/comparison.html');assert page.locator('article').count()==24
 assert page.locator('.hidden-name:visible').count()==0
 assert page.evaluate('window.pwned===undefined');assert page.locator('article img').count()==0
 assert 'имитация API' in page.locator('body').inner_text()
 models=[m['key'] for m in report['models'][:2]]
 for i,key in enumerate(models):
  for select in page.locator('select[data-model="'+key+'"]').all():select.select_option('5' if i==0 else '3')
 page.locator('#calculate').click();ranking=page.locator('#rank').inner_text();assert '5.00' in ranking and '3.00' in ranking and '\n' in ranking,ranking
 for m in report['models']:assert m['name'] not in ranking
 page.reload();assert page.locator('select[data-model="'+models[0]+'"]').first.input_value()=='5'
 page.locator('#reveal').click();page.locator('#calculate').click();assert report['models'][0]['name'] in page.locator('#rank').inner_text()
 with page.expect_download() as event:page.locator('#export').click()
 path=event.value.path();ratings=json.loads(Path(path).read_text());assert len(ratings['scores'])==18
 assert not errors,errors
 page.screenshot(path='/tmp/model-benchmark-report-ui.png');b.close()
print('Offline blind report: script escaping, hidden names, complete-score ranking, persisted scores and ratings export passed')
