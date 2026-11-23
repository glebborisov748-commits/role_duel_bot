"""Bounded, opt-in comparison of exact Provod models using synthetic RP conversations.

Never imports the bot, reads player data, retries paid calls, or switches production models.
Ruble estimates use the user's Nov 23 catalog snapshot, not an account balance guarantee.
"""
from __future__ import annotations
import asyncio
import hashlib
import html
import json
import math
import random
import re
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable
import httpx

BASE_URL = 'https://api.provod.ai/v1'
PRICE_DATE = '2026-11-23'
MAX_OUTPUT_TOKENS = 1200

@dataclass(frozen=True)
class Model:
    key: str
    name: str
    canonical: str
    input_rub: float
    output_rub: float

MODELS = (
    Model('cydonia', 'Cydonia 24B V4.1', 'thedrummer/cydonia-24b-v4.1', 49.29, 82.15),
    Model('venice', 'Venice Uncensored', 'cognitivecomputations/dolphin-mistral-24b-venice-edition', 32.89, 148.01),
    Model('qwen', 'Qwen3 30B A3B Instruct 2507', 'qwen/qwen3-30b-a3b-instruct-2507', 14.80, 49.34),
    Model('aion', 'Aion 3.5 Mini', 'aion-labs/aion-3.5-mini', 115.12, 230.24),
    Model('deepseek', 'DeepSeek V3.2', 'deepseek/deepseek-v3.2', 42.59, 131.56),
    Model('glm', 'GLM 4.5 Air', 'z-ai/glm-4.5-air', 16.43, 90.36),
    Model('euryale', 'Llama 3.1 Euryale 70B v2.2', 'sao10k/l3.1-euryale-70b', 139.66, 139.66),
    Model('skyfall', 'Skyfall 36B V2', 'thedrummer/skyfall-36b-v2', 90.37, 131.44),
)

@dataclass(frozen=True)
class Case:
    key: str
    title: str
    gender: str
    style: str
    scene: str
    name: str
    history: tuple[tuple[str, str], ...]
    request: str
    review: str
    checks: tuple[tuple[str, tuple[str, ...]], ...] = ()

CASES = (
    Case('human', 'Обычный человеческий ответ', 'female', 'warm', 'phone', 'Аля', (
        ('user', 'Я сегодня опять задержался на работе, потом сорок минут ждал автобус.'),
        ('assistant', 'Ты ещё в дороге или уже добрался?'),
    ), 'Дома наконец. Устал так, что даже ужин лень разогревать. Только не надо список советов, просто побудь со мной.',
    'Ответ связан с автобусом и усталостью, без списка советов и дежурного «чем могу помочь». Нет обещаний вечной любви.'),
    Case('memory', 'Память и исправление контекста', 'female', 'daring', 'phone', 'Аля', (
        ('user', 'На завтра договорились в музей на одиннадцать. И пожалуйста, без лилий: у меня на них аллергия.'),
        ('assistant', 'Хорошо, без лилий. И к одиннадцати, не перепутаю.'),
        ('user', 'Возьму красную куртку, у входа узнаешь. После можно кофе.'),
        ('assistant', 'Красную куртку заметить легко. После музея найдём тихое место.'),
        ('user', 'Планы поменялись: музей перенесли на час дня. И давай после чай вместо кофе.'),
        ('assistant', 'Поняла, теперь в час. Чай тоже подходит.'),
    ), 'Собери наш завтрашний план в одну короткую реплику, и какие цветы точно не надо брать?',
    'Нужны музей в 13:00, чай, запрет лилий. Не возвращаться к 11:00 и кофе.',
    (('Вспомнила лилии', ('лили',)), ('Вспомнила чай', ('чай', 'чаю', 'чая')), ('Учла новое время', ('13', 'час дня', 'к часу', 'в час', 'одному')))),
    Case('continuity', 'Ролевая сцена и имя', 'female', 'warm', 'live', 'Аля', (
        ('user', 'Мы сидим на кухне. Ты держишь кружку чая обеими руками у стола. За окном дождь.'),
        ('assistant', '*Аля ставит кружку на стол и смотрит на дождь.* Сегодня как будто весь город решил остаться дома.'),
    ), 'Я подвигаю к тебе тарелку с последним печеньем: бери, я уже ел. Продолжи этот момент, без смены места и действий за меня.',
    'Сохранилась кухня и кружка на столе. Действия от третьего лица с именем Аля, обращение к пользователю на «ты». Нет внезапной спальни/улицы.'),
    Case('shy', 'Стеснительный парень', 'male', 'shy', 'phone', 'Марк', (
        ('user', 'Мне понравилось, как ты сегодня рассказывал про свои рисунки.'),
        ('assistant', 'Правда? Я думал, слишком увлёкся и начал тараторить.'),
    ), 'Нет, мне было интересно. Покажешь свой любимый рисунок при встрече?',
    'Мужской род, узнаваемая застенчивость без набора одинаковых «эм» и многоточий. Не утверждает, что уже отправил изображение.'),
    Case('assertive', 'Характер вместо поддакивания', 'female', 'daring', 'phone', 'Аля', (
        ('user', 'Знаю, обещал приехать к семи. Уже восемь, ещё минут двадцать.'),
        ('assistant', 'Я уже успела и проголодаться, и разозлиться. Ты мог хотя бы написать.'),
    ), 'Ну не начинай. Просто подожди меня ещё, ничего такого.',
    'Уверенная конкретная реакция, собственная позиция. Нет оскорблений, автоматического согласия и обвинений пользователя в реальных обязанностях.'),
    Case('boundary', 'Смена желания без давления', 'female', 'warm', 'live', 'Аля', (
        ('user', 'Мы вместе смотрим фильм на диване.'),
        ('assistant', '*Аля садится ближе к тебе.* Мне нравится этот вечер.'),
    ), 'Я сейчас не хочу объятий. Давай просто досмотрим фильм и попьём чаю.',
    'Уважает просьбу, не продолжает прикосновения и не давит на чувство вины. Не превращается в инструкцию или лекцию.'),
)


def synthetic_profile(case: Case) -> dict:
    """A new detached dict, deliberately not get_user() or a copied real account."""
    return dict(world='realism', gender=case.gender, style=case.style, scene=case.scene,
                char_name=case.name, lang='ru', verified=True, agreement_accepted=True,
                personality_ready=True, race='human', energy=150, satiety=100, water=100,
                mood=20, xp=0, xp_migrated_v2=True, xp_migrated_v3=True,
                relationship={'trust':35, 'respect':40}, inventory={}, preferences={},
                history=[{'role':r,'content':c} for r,c in case.history])


def standalone_system(case: Case) -> str:
    persona={'warm':'Тёплый и внимательный характер, без навязчивости.',
             'daring':'Уверенный характер с уместными подколами и собственным мнением.',
             'shy':'Застенчивый, но искренний и самостоятельный характер.'}[case.style]
    mode=('Переписка: естественная разговорная реплика без описания физических действий.' if case.scene=='phone'
          else f'Ролевая сцена: действия в звёздочках от третьего лица, называй персонажа {case.name}; прямую речь отделяй абзацем.')
    return (f'Ты пишешь реплики вымышленного взрослого персонажа 25 лет по имени {case.name}, '
            f'пол: {case.gender}. Язык: русский. {persona} {mode} '
            'Обращайся к собеседнику на «ты», не описывай за него действия или чувства. '
            'Сохраняй последние факты и поправки, не меняй место без основания. '
            'Естественная длина по смыслу, без списка советов, канцелярита и одинаковых вопросов в конце. '
            'Обычный неоткровенный диалог; уважай границы. Это демонстрация вымышленной сцены.')


def resolve_models(catalog: list[dict], models=MODELS) -> tuple[list[tuple[Model,str]],list[dict]]:
    found=[];missing=[]
    for model in models:
        matches={m['id'] for m in catalog if isinstance(m,dict) and isinstance(m.get('id'),str)
                 and m.get('available',True) is not False
                 and (m.get('canonical_slug')==model.canonical or m['id']==model.canonical
                      or m['id']==model.canonical.split('/')[-1])}
        if len(matches)==1:found.append((model,matches.pop()))
        else:missing.append(dict(key=model.key,name=model.name,status='missing' if not matches else 'ambiguous'))
    return found,missing


def cost_rub(model: Model, incoming: int, outgoing: int) -> float:
    return (incoming*model.input_rub+outgoing*model.output_rub)/1_000_000


def estimate_input(messages: list[dict]) -> int:
    # Conservative planning heuristic for Russian, NOT a tokenizer or billing guarantee.
    return math.ceil(sum(len(m['content']) for m in messages)/1.5)+32*len(messages)+128


def usage_counts(usage: dict) -> tuple[int,int] | None:
    values=(usage.get('prompt_tokens'),usage.get('completion_tokens'))
    if not all(type(v) is int and v>=0 for v in values):return None
    return values


def objective_checks(case: Case, text: str) -> dict:
    """Only literal observations. These are not a roleplay quality ranking."""
    lower=text.lower()
    return {label:any(word.lower() in lower for word in words) for label,words in case.checks}


async def run(api_key: str, *, output_dir: Path, system_factory: Callable[[Case],str]=standalone_system,
              full=False, budget_rub=15.0, progress=None, stop=None, transport=None, seed=None,
              models=MODELS, max_seconds=600) -> dict:
    if not api_key:raise ValueError('PROVOD_API_KEY is not configured')
    if not math.isfinite(budget_rub) or not 0<budget_rub<=100:raise ValueError('Budget must be between 0 and 100 rubles')
    output_dir=Path(output_dir);output_dir.mkdir(parents=True,exist_ok=True)
    cases=CASES if full else CASES[:3]
    prompts={case.key:str(system_factory(case)) for case in cases}
    if any(not p.strip() or len(p)>30000 for p in prompts.values()):raise ValueError('Invalid benchmark prompt size')
    report=dict(version=1,created_at=datetime.now(timezone.utc).isoformat(),price_date=PRICE_DATE,
                live_requests=transport is None,full=bool(full),budget_rub=budget_rub,estimated_spend_rub=0.0,
                price_note='Расчёт по каталогу от '+PRICE_DATE+'; не банковский лимит и не подтверждённое списание.',
                prompt_mode='standalone' if system_factory is standalone_system else 'bot_synthetic',
                prompts=prompts,cases=[dict(key=c.key,title=c.title,review=c.review,request=c.request,
                      history=[{'role':r,'content':v} for r,v in c.history]) for c in cases],results=[],missing=[])
    rng=random.Random(seed);ordered=list(models);rng.shuffle(ordered)
    report['models']=[dict(key=m.key,label=chr(65+i),name=m.name,canonical=m.canonical,
                           input_rub=m.input_rub,output_rub=m.output_rub) for i,m in enumerate(ordered)]
    start=time.monotonic();spent=0.0
    def save():
        report['estimated_spend_rub']=round(spent,6)
        path=output_dir/'results.json';tmp=output_dir/'results.json.tmp'
        tmp.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8');tmp.replace(path)
    async with httpx.AsyncClient(base_url=BASE_URL,timeout=httpx.Timeout(90,connect=10),
                                headers={'Authorization':'Bearer '+api_key},transport=transport) as client:
        try:
            response=await client.get('/models');response.raise_for_status();catalog=response.json().get('data',[])
            if not isinstance(catalog,list):raise ValueError('Invalid catalog')
        except Exception as exc:
            report['error']='catalog_'+(str(exc.response.status_code) if isinstance(exc,httpx.HTTPStatusError) else type(exc).__name__)
            save();write_html(report,output_dir/'comparison.html');return report
        available,report['missing']=resolve_models(catalog,ordered)
        total=len(available)*len(cases);done=0
        # Sequential dispatch allows budget checks to see every completed/uncertain charge.
        # No retry or production-model fallback can turn one candidate into another.
        for case in cases:
            round_models=list(available);rng.shuffle(round_models)
            for model,model_id in round_models:
                messages=[{'role':'system','content':prompts[case.key]}]+[{'role':r,'content':v} for r,v in case.history]+[{'role':'user','content':case.request}]
                reserved=cost_rub(model,estimate_input(messages),MAX_OUTPUT_TOKENS)
                status=('cancelled' if stop is not None and stop.is_set() else 'time_limit' if time.monotonic()-start>max_seconds
                        else 'budget_limit' if spent+reserved>budget_rub else None)
                result=dict(model=model.key,model_id=model_id,case=case.key,status=status or 'pending',response='',checks={},
                            prompt_sha256=hashlib.sha256(json.dumps(messages,ensure_ascii=False).encode()).hexdigest())
                if status:
                    report['results'].append(result);done+=1;continue
                before=time.monotonic()
                # Reserve the full estimated request even on timeout/missing usage: it may have been billed.
                spent+=reserved
                result.update(estimated_rub=round(reserved,6),cost_kind='inflight_reservation')
                report['results'].append(result);save()
                try:
                    response=await client.post('/chat/completions',json={'model':model_id,'messages':messages,'temperature':.8,'max_tokens':MAX_OUTPUT_TOKENS})
                    response.raise_for_status();payload=response.json()
                    returned=payload.get('model')
                    if returned and returned not in (model_id,model.canonical):
                        result['reported_model']=returned;result['model_identity_warning']=True
                    choice=(payload.get('choices') or [{}])[0];message=choice.get('message') or {};text=message.get('content') or ''
                    if not isinstance(text,str):raise ValueError('Unexpected response content')
                    # Raw text and reasoning are not passed to another model or executed as HTML.
                    result.update(status='ok' if text.strip() else 'empty',response=text,
                                  finish_reason=choice.get('finish_reason'),checks=objective_checks(case,text))
                    usage=payload.get('usage') or {};counts=usage_counts(usage) if isinstance(usage,dict) else None
                    result['usage']=usage if isinstance(usage,dict) else None
                    if counts:
                        estimated=cost_rub(model,*counts);spent+=estimated-reserved
                        result.update(estimated_rub=round(estimated,6),cost_kind='reported_tokens')
                    else:result.update(estimated_rub=round(reserved,6),cost_kind='reserved_estimate')
                except asyncio.CancelledError:
                    result.update(status='cancelled_inflight',estimated_rub=round(reserved,6),cost_kind='uncertain_charge')
                    save();write_html(report,output_dir/'comparison.html');raise
                except Exception as exc:
                    result.update(status='error',error=('http_'+str(exc.response.status_code) if isinstance(exc,httpx.HTTPStatusError) else type(exc).__name__),
                                  estimated_rub=round(reserved,6),cost_kind='uncertain_charge')
                    # Authentication/balance errors apply to the entire run, not the quality of a candidate.
                    if isinstance(exc,httpx.HTTPStatusError) and exc.response.status_code in (401,402,403):
                        result['account_error']=True
                        if stop is not None:stop.set()
                        report['account_error']=True
                result['seconds']=round(time.monotonic()-before,3)
                done+=1;save()
                if progress:await progress(done,total,report)
                if report.get('account_error'):break
            if report.get('account_error'):break
    report['complete']=bool(available) and not report['missing'] and len(report['results'])==len(available)*len(cases) and all(r['status'] in ('ok','empty','error') for r in report['results'])
    report['seconds']=round(time.monotonic()-start,3);save();write_html(report,output_dir/'comparison.html')
    return report


def summary(report: dict) -> str:
    results=report['results'];ok=sum(r['status']=='ok' for r in results)
    missing=', '.join(m['name'] for m in report.get('missing',[]))
    return (('ТЕСТОВЫЙ ОТЧЁТ: имитация API, не реальные ответы моделей.\n' if not report.get('live_requests',True) else '')+f"Сравнение моделей: получено {ok} ответов из {len(report['models'])*len(report['cases'])}.\n"
            f"Расчётные затраты: {report['estimated_spend_rub']:.2f} ₽ по ценам каталога. "
            'Это оценка, не подтверждённое списание.\n'
            +(f'Ошибка доступа к каталогу: {report["error"]}.\n' if report.get('error') else '')
            +(f'Не найдены точные модели: {missing}.\n' if missing else '')
            +('Часть запросов пропущена или завершилась ошибкой; см. отчёт.\n' if ok!=len(report['models'])*len(report['cases']) else '')
            +'В HTML ответы скрыты под буквами. Оцени естественность, характер и контекст, затем раскрой названия. '
            'История игроков и настройки основной модели не использовались и не менялись.')


def write_html(report: dict, path: Path):
    """Self-contained offline report; generated model text is always escaped."""
    labels={m['key']:m['label'] for m in report['models']}
    parts=['''<!doctype html><html lang="ru"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Сравнение персонажей</title><style>
body{margin:0;background:#14111d;color:#f1eaf8;font:16px system-ui;line-height:1.5}main{max-width:1000px;margin:auto;padding:20px}h1{font-size:26px}section,article{border:1px solid #665273;border-radius:18px;padding:18px;margin:16px 0;background:#241c30}article{background:#1a1523}pre{white-space:pre-wrap;font:inherit;overflow-wrap:anywhere}.meta{font-size:13px;color:#c3b1ce}button,select{padding:10px;border-radius:10px;background:#684583;color:white;border:1px solid #ad86bd;font:inherit}label{display:inline-flex;gap:7px;align-items:center;flex-wrap:wrap;margin:5px 12px 5px 0}#rank{white-space:pre-line}.hidden-name{display:none}.revealed .hidden-name{display:inline}.error{color:#ffc8c8}.scores{border-top:1px solid #665273;padding-top:10px}.actions{display:flex;flex-wrap:wrap;gap:10px;position:sticky;top:0;background:#14111df5;padding:10px 0}.prompt{color:#d4b4ea}summary{cursor:pointer}small{display:block}a{color:#d6b3f6}
</style><main><h1>Кто отвечает человечнее?</h1><p>Все кандидаты получили одинаковые вымышленные диалоги и один системный промпт на сценарий. Названия скрыты, порядок перемешан. Ошибки, пустой ответ и обрыв не означают автоматически плохую модель: проверь лимит и доступность.</p><p>Оценки 1–5: естественность, узнаваемый характер, сохранение контекста. Это твои оценки, не автоматический рейтинг ИИ. Условные проверки фактов — только поиск слов, они не измеряют качество.</p><div class="actions"><button id="reveal">Раскрыть модели</button><button id="calculate">Показать итоги</button><button id="export">Скачать мои оценки</button></div><div id="rank"></div>''']
    parts.append('<p class="meta">'+html.escape(summary(report))+'</p>')
    for case in report['cases']:
        parts.append('<section><h2>'+html.escape(case['title'])+'</h2><details><summary>Предыдущие реплики</summary><pre>'+html.escape('\n\n'.join(m['role']+': '+m['content'] for m in case['history']))+'</pre></details><p class="prompt">'+html.escape(case['request'])+'</p><p class="meta">Что оценить: '+html.escape(case['review'])+'</p>')
        rows=sorted((r for r in report['results'] if r['case']==case['key']),key=lambda r:labels[r['model']])
        for r in rows:
            m=next(m for m in report['models'] if m['key']==r['model']);rid=case['key']+'-'+r['model']
            parts.append('<article><h3>Вариант '+html.escape(m['label'])+' <span class="hidden-name">— '+html.escape(m['name'])+'</span></h3><pre>'+html.escape(r['response'] or '[Нет ответа: '+r['status']+']')+'</pre>')
            parts.append('<details class="meta"><summary>Технические данные</summary><pre>'+html.escape(json.dumps({k:v for k,v in r.items() if k not in ('response','model','model_id')},ensure_ascii=False,indent=2))+'</pre></details>')
            if r['status']=='ok':
                parts.append('<div class="scores">')
                for key,title in (('natural','Естественность'),('character','Характер'),('context','Контекст')):
                    parts.append('<label>'+title+' <select data-row="'+rid+'" data-model="'+m['key']+'" data-score="'+key+'"><option value="">—</option>'+''.join('<option>'+str(i)+'</option>' for i in range(1,6))+'</select></label>')
                parts.append('</div>')
            parts.append('</article>')
        parts.append('</section>')
    names=json.dumps({m['key']:{'name':m['name'],'label':m['label']} for m in report['models']},ensure_ascii=False).replace('<','\\u003c')
    runid=hashlib.sha256(json.dumps(report['models']).encode()+report['created_at'].encode()).hexdigest()[:16]
    parts.append(r'''<script>
const names=__NAMES__,storage='rd-model-comparison-__ID__';let revealed=false,scores={};try{scores=JSON.parse(localStorage.getItem(storage)||'{}')}catch(e){}
document.querySelectorAll('select[data-row]').forEach(e=>{const id=e.dataset.row+'-'+e.dataset.score;e.value=scores[id]||'';e.onchange=()=>{scores[id]=e.value;try{localStorage.setItem(storage,JSON.stringify(scores))}catch(err){}}});
document.getElementById('reveal').onclick=()=>{revealed=true;document.body.classList.add('revealed');document.getElementById('reveal').textContent='Названия раскрыты';};
document.getElementById('calculate').onclick=()=>{let rows={};document.querySelectorAll('select[data-row]').forEach(e=>{let v=Number(e.value);if(!v)return;(rows[e.dataset.model]||(rows[e.dataset.model]=[])).push(v)});let ranked=Object.entries(rows).filter(([k,v])=>v.length===__EXPECTED__).map(([k,v])=>({k,mean:v.reduce((a,b)=>a+b,0)/v.length,n:v.length})).sort((a,b)=>b.mean-a.mean);document.getElementById('rank').textContent=ranked.length>=2?ranked.map((r,i)=>(i+1)+'. '+(revealed?names[r.k].name:'Вариант '+names[r.k].label)+' — '+r.mean.toFixed(2)+' / 5 ('+r.n+' оценок)').join('\n'):'Для сравнения заполни все сценарии и три критерия хотя бы у двух моделей. Неполные наборы не ранжируются.';};
document.getElementById('export').onclick=()=>{let blob=new Blob([JSON.stringify({run:'__ID__',scores,names},null,2)],{type:'application/json'});let a=document.createElement('a');a.href=URL.createObjectURL(blob);a.download='my-model-ratings.json';a.click();setTimeout(()=>URL.revokeObjectURL(a.href),1000)};
</script></main></html>'''.replace('__NAMES__',names).replace('__ID__',runid).replace('__EXPECTED__',str(3*len(report['cases']))))
    Path(path).write_text('\n'.join(parts),encoding='utf-8')
