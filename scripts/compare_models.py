"""Local entrypoint: --plan is free; --run makes billed synthetic requests."""
import argparse,asyncio,json,os,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from dotenv import load_dotenv
import httpx
import model_benchmark as bench

async def main():
    parser=argparse.ArgumentParser(description=__doc__)
    action=parser.add_mutually_exclusive_group(required=True)
    action.add_argument('--plan',action='store_true');action.add_argument('--run',action='store_true')
    parser.add_argument('--full',action='store_true');parser.add_argument('--budget',type=float,default=15)
    parser.add_argument('--bot-prompts',action='store_true',help='Import bot prompt builder; requires BOT_TOKEN and PROVOD_API_KEY configuration')
    parser.add_argument('--output',type=Path)
    opts=parser.parse_args()
    if opts.output is None:
        from datetime import datetime
        opts.output=Path('data/model-tests')/('local-'+datetime.now().strftime('%Y%m%d-%H%M%S-%f'))
    load_dotenv(os.getenv('RD_ENV_FILE') or None)
    factory=bench.standalone_system
    if opts.bot_prompts:
        import app
        factory=app.model_test_system
    if opts.plan:
        async with httpx.AsyncClient(timeout=20) as client:
            response=await client.get(bench.BASE_URL+'/models');response.raise_for_status();catalog=response.json()['data']
        found,missing=bench.resolve_models(catalog)
        cases=bench.CASES if opts.full else bench.CASES[:3]
        total=0
        for model,model_id in found:
            estimate=0
            for case in cases:
                messages=[dict(role='system',content=factory(case))]+[dict(role=r,content=c) for r,c in case.history]+[dict(role='user',content=case.request)]
                estimate+=bench.cost_rub(model,bench.estimate_input(messages),bench.MAX_OUTPUT_TOKENS)
            total+=estimate
            print(f'{model.name}: {model_id} · запасная оценка до {estimate:.2f} ₽')
        print(f'План: {len(found)} моделей × {len(cases)} примера; запасная оценка {total:.2f} ₽; лимит {opts.budget:.2f} ₽.')
        print('Это расчёт по длине текста и каталожным ценам, не точная токенизация или гарантия списания. При исчерпании бюджета часть примеров будет пропущена.')
        if missing:print('Пропущены:',', '.join(m['name'] for m in missing))
        print('Платных запросов не было. Для запуска добавь --run вместо --plan.')
        return
    key=os.getenv('PROVOD_API_KEY')
    if not key:raise SystemExit('PROVOD_API_KEY не настроен. Добавь его через переменные окружения или .env, не в командную строку.')
    async def progress(done,total,report):print(f'{done}/{total} · расчётно {report["estimated_spend_rub"]:.2f} ₽',flush=True)
    report=await bench.run(key,output_dir=opts.output,system_factory=factory,full=opts.full,budget_rub=opts.budget,progress=progress)
    print(bench.summary(report));print('Отчёт:',opts.output/'comparison.html')

if __name__=='__main__':
    try:asyncio.run(main())
    except KeyboardInterrupt:raise SystemExit('Тест прерван; проверь частичный отчёт. Текущий запрос уже мог быть оплачен.')
