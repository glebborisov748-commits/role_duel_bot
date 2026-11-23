"""Exercise the actual chief command, synthetic bot prompts and document delivery, offline."""
import os,sys,tempfile,asyncio,json,copy
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock,Mock
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
os.environ.update(BOT_TOKEN='123456:TEST_ONLY',PROVOD_API_KEY='FAKE_TEST_KEY',DATA_DIR=tempfile.mkdtemp(prefix='rd-bench-runtime-'))
import app,model_benchmark as bench,httpx
calls=[]
def handler(request):
 if request.method=='GET':return httpx.Response(200,json={'data':[dict(id=m.canonical.split('/')[-1],canonical_slug=m.canonical) for m in bench.MODELS]})
 body=json.loads(request.content);calls.append(body)
 assert 'FAKE_TEST_KEY' not in json.dumps(body)
 return httpx.Response(200,json={'model':body['model'],'choices':[{'message':{'content':'ТЕСТ: не реальный ответ модели.'},'finish_reason':'stop'}],'usage':{'prompt_tokens':2000,'completion_tokens':200}})
real_run=bench.run
async def mocked_run(key,**kwargs):
 assert key=='FAKE_TEST_KEY'
 return await real_run(key,transport=httpx.MockTransport(handler),**kwargs)
bench.run=mocked_run
async def main():
 original_state=copy.deepcopy(app.user_data);model=(app.AI_MODEL,app.INTIM_MODEL,dict(app._model_cache))
 app.save_data=Mock(side_effect=AssertionError('Benchmark wrote player state'))
 status=SimpleNamespace(edit_text=AsyncMock())
 message=SimpleNamespace(from_user=SimpleNamespace(id=app.MAIN_ADMIN_ID),chat=SimpleNamespace(id=app.MAIN_ADMIN_ID,type='private'),text='/model_test',answer=AsyncMock(return_value=status),answer_document=AsyncMock())
 await app.model_test_cmd(message);await app.MODEL_TEST_JOB['task']
 assert len(calls)==24,len(calls);assert message.answer_document.await_count==2
 assert app.MODEL_TEST_JOB['status']=='done'
 assert app.user_data==original_state and model==(app.AI_MODEL,app.INTIM_MODEL,dict(app._model_cache))
 app.save_data.assert_not_called()
 result=json.loads((Path(app.MODEL_TEST_JOB['directory'])/'results.json').read_text());assert result['prompt_mode']=='bot_synthetic';assert not result['live_requests'];assert result['complete']
 before=len(calls);message.text='/model_test result';await app.model_test_cmd(message);assert len(calls)==before;assert message.answer_document.await_count==4
 print('Chief command: 24 exact-model mocked calls, real synthetic bot prompts, report delivery, read-only player/model state and free report retrieval passed')
asyncio.run(main())
