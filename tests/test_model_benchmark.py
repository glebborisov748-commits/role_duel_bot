import asyncio
import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock,patch
import httpx
import model_benchmark as bench
from test_core import load_functions


def catalog(models=bench.MODELS):
    return [dict(id=m.canonical.split('/')[-1],canonical_slug=m.canonical,available=True) for m in models]

class ModelCatalogTests(unittest.TestCase):
    def test_exact_catalog_ids_and_missing_variant(self):
        resolved,missing=bench.resolve_models(catalog());self.assertEqual(len(resolved),8);self.assertFalse(missing)
        changed=catalog();changed[0].update(id='cydonia-r1-24b-v4.1',canonical_slug='thedrummer/cydonia-r1-24b-v4.1')
        resolved,missing=bench.resolve_models(changed);self.assertEqual(missing[0]['key'],'cydonia')
    def test_ambiguous_catalog_has_no_silent_fallback(self):
        entries=catalog();entries.append(dict(id='another-billed-route',canonical_slug=bench.MODELS[0].canonical))
        resolved,missing=bench.resolve_models(entries);self.assertEqual(missing[0]['status'],'ambiguous');self.assertNotIn(bench.MODELS[0],[m for m,_ in resolved])
    def test_cost_uses_both_token_counts(self):
        model=bench.MODELS[0];self.assertAlmostEqual(bench.cost_rub(model,5_000_000,500_000),287.525)
        for bad in ({},{'prompt_tokens':True,'completion_tokens':4},{'prompt_tokens':-1,'completion_tokens':5}):self.assertIsNone(bench.usage_counts(bad))
    def test_profiles_are_synthetic_and_independent(self):
        a=bench.synthetic_profile(bench.CASES[0]);b=bench.synthetic_profile(bench.CASES[0]);a['history'].clear();self.assertTrue(b['history']);self.assertNotIn('_telegram_id',a)

class BenchmarkTests(unittest.IsolatedAsyncioTestCase):
    async def run_case(self,handler,**opts):
        with tempfile.TemporaryDirectory() as directory:
            report=await bench.run('FAKE_SECRET',output_dir=Path(directory),transport=httpx.MockTransport(handler),seed=3,**opts)
            self.saved_json=(Path(directory)/'results.json').read_text();self.saved_html=(Path(directory)/'comparison.html').read_text()
            self.assertEqual(json.loads(self.saved_json),report)
            return report
    async def test_equal_prompts_actual_usage_and_no_secret_in_report(self):
        requests=[];calls=[]
        def factory(case):calls.append(case.key);return bench.standalone_system(case)
        def handler(request):
            if request.url.path.endswith('/models'):return httpx.Response(200,json={'data':catalog()})
            payload=json.loads(request.content);requests.append(payload)
            return httpx.Response(200,json={'model':payload['model'],'choices':[{'message':{'content':'Тестовый ответ, не результат настоящей модели.'},'finish_reason':'stop'}],'usage':{'prompt_tokens':1000,'completion_tokens':100}})
        report=await self.run_case(handler,system_factory=factory)
        self.assertEqual(len(requests),24);self.assertEqual(len(calls),3);self.assertEqual(len(set(p['model'] for p in requests)),8)
        self.assertTrue(report['complete']);self.assertTrue(all(r['status']=='ok' for r in report['results']))
        for case in bench.CASES[:3]:self.assertEqual(len({r['prompt_sha256'] for r in report['results'] if r['case']==case.key}),1)
        expected=3*sum(bench.cost_rub(m,1000,100) for m in bench.MODELS);self.assertAlmostEqual(report['estimated_spend_rub'],expected,places=5)
        self.assertNotIn('FAKE_SECRET',self.saved_json);self.assertNotIn('FAKE_SECRET',self.saved_html)
    async def test_budget_prevents_any_paid_call(self):
        posted=[]
        def handler(request):
            if request.method=='GET':return httpx.Response(200,json={'data':catalog()})
            posted.append(request);raise AssertionError('Budget allowed a paid call')
        report=await self.run_case(handler,budget_rub=.00001)
        self.assertFalse(posted);self.assertFalse(report['complete']);self.assertTrue(all(r['status']=='budget_limit' for r in report['results']))
    async def test_missing_usage_keeps_reservation(self):
        def handler(request):
            if request.method=='GET':return httpx.Response(200,json={'data':catalog(bench.MODELS[:1])})
            return httpx.Response(200,json={'choices':[{'message':{'content':'Тест'}}]})
        report=await self.run_case(handler,models=bench.MODELS[:1]);self.assertGreater(report['estimated_spend_rub'],0)
        self.assertTrue(all(r['cost_kind']=='reserved_estimate' for r in report['results']))
    async def test_timeout_not_retried_or_refunded_as_free(self):
        posted=[]
        def handler(request):
            if request.method=='GET':return httpx.Response(200,json={'data':catalog(bench.MODELS[:1])})
            posted.append(request);raise httpx.ReadTimeout('FAKE_SECRET',request=request)
        report=await self.run_case(handler,models=bench.MODELS[:1]);self.assertEqual(len(posted),3)
        self.assertTrue(all(r['status']=='error' and r['cost_kind']=='uncertain_charge' for r in report['results']));self.assertNotIn('FAKE_SECRET',self.saved_json)
    async def test_auth_failure_stops_entire_run(self):
        count=[]
        def handler(request):
            if request.method=='GET':return httpx.Response(200,json={'data':catalog()})
            count.append(request);return httpx.Response(401,json={'error':'FAKE_SECRET must never be logged'})
        report=await self.run_case(handler);self.assertEqual(len(count),1);self.assertTrue(report['account_error']);self.assertNotIn('FAKE_SECRET',self.saved_json)
    async def test_cancel_preserves_first_answer_and_stops_dispatch(self):
        stop=asyncio.Event();count=[]
        async def progress(*args):stop.set()
        def handler(request):
            if request.method=='GET':return httpx.Response(200,json={'data':catalog()})
            count.append(request);return httpx.Response(200,json={'choices':[{'message':{'content':'Тест'}}]})
        report=await self.run_case(handler,stop=stop,progress=progress);self.assertEqual(len(count),1);self.assertFalse(report['complete']);self.assertEqual(report['results'][0]['status'],'ok')
    async def test_catalog_failure_saves_error_without_paid_calls(self):
        def handler(request):return httpx.Response(503)
        report=await self.run_case(handler);self.assertEqual(report['error'],'catalog_503');self.assertEqual(report['estimated_spend_rub'],0)
    async def test_provider_substitution_warning_and_html_escaping(self):
        hostile='</script><img src=x onerror="window.pwned=1">'
        def handler(request):
            if request.method=='GET':return httpx.Response(200,json={'data':catalog(bench.MODELS[:1])})
            return httpx.Response(200,json={'model':'different-model','choices':[{'message':{'content':hostile},'finish_reason':'length'}]})
        report=await self.run_case(handler,models=bench.MODELS[:1]);self.assertTrue(report['results'][0]['model_identity_warning']);self.assertEqual(report['results'][0]['finish_reason'],'length')
        self.assertIn('&lt;/script&gt;',self.saved_html);self.assertNotIn(hostile,self.saved_html)
    async def test_no_key_does_not_create_output(self):
        with tempfile.TemporaryDirectory() as root:
            path=Path(root)/'never-written'
            with self.assertRaises(ValueError):await bench.run('',output_dir=path)
            self.assertFalse(path.exists())

    async def test_charge_reservation_saved_before_dispatch(self):
        with tempfile.TemporaryDirectory() as directory:
            count=[]
            def handler(request):
                if request.method=='GET':return httpx.Response(200,json={'data':catalog(bench.MODELS[:1])})
                saved=json.loads((Path(directory)/'results.json').read_text());row=saved['results'][-1]
                self.assertEqual(row['status'],'pending');self.assertEqual(row['cost_kind'],'inflight_reservation');self.assertGreater(saved['estimated_spend_rub'],0)
                count.append(request)
                return httpx.Response(200,json={'choices':[{'message':{'content':'Тест'}}]})
            await bench.run('FAKE',output_dir=Path(directory),transport=httpx.MockTransport(handler),models=bench.MODELS[:1])
            self.assertEqual(len(count),3)

class BenchmarkAdminTests(unittest.IsolatedAsyncioTestCase):
    async def test_only_chief_private_chat_can_start(self):
        ns={'MAIN_ADMIN_ID':7};load_functions({'model_test_cmd'},ns)
        for uid,kind in ((8,'private'),(7,'group')):
            answer=AsyncMock();m=SimpleNamespace(from_user=SimpleNamespace(id=uid),chat=SimpleNamespace(type=kind),answer=answer,text='/model_test')
            await ns['model_test_cmd'](m);answer.assert_awaited_once()
    async def test_cancel_is_cooperative_without_a_second_task(self):
        stop=asyncio.Event();task=SimpleNamespace(done=lambda:False)
        ns={'MAIN_ADMIN_ID':7,'MODEL_TEST_JOB':{'task':task,'stop':stop}};load_functions({'model_test_cmd'},ns)
        m=SimpleNamespace(from_user=SimpleNamespace(id=7),chat=SimpleNamespace(type='private'),answer=AsyncMock(),text='/model_test cancel')
        await ns['model_test_cmd'](m);self.assertTrue(stop.is_set());self.assertIs(ns['MODEL_TEST_JOB']['task'],task)

    async def test_start_is_reserved_before_first_await(self):
        from datetime import datetime
        import os,secrets
        started=asyncio.Event();release=asyncio.Event();finish=asyncio.Event();jobs=[]
        async def run_job(*args):jobs.append(True);await finish.wait()
        async def first_answer(*args,**kwargs):started.set();await release.wait();return SimpleNamespace()
        ns={'MAIN_ADMIN_ID':7,'MODEL_TEST_JOB':{},'DATA_DIR':'/tmp/rd-benchmark-test','os':os,'datetime':datetime,'secrets':secrets,'asyncio':asyncio,'model_test_run':run_job}
        load_functions({'model_test_cmd'},ns)
        first=SimpleNamespace(from_user=SimpleNamespace(id=7),chat=SimpleNamespace(type='private'),answer=first_answer,text='/model_test')
        second=SimpleNamespace(from_user=SimpleNamespace(id=7),chat=SimpleNamespace(type='private'),answer=AsyncMock(),text='/model_test')
        task=asyncio.create_task(ns['model_test_cmd'](first));await started.wait()
        self.assertEqual(ns['MODEL_TEST_JOB']['status'],'starting')
        await ns['model_test_cmd'](second);self.assertIn('уже идёт',second.answer.call_args.args[0])
        release.set();await task;await asyncio.sleep(0);self.assertEqual(len(jobs),1)
        finish.set();await ns['MODEL_TEST_JOB']['task']
