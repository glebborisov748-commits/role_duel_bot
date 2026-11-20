"""Problembo image-gen contract: https://problembo.com/docs/dev ."""
import asyncio
import os
import httpx
import profile_options

BASE_URL = os.getenv('PROBLEMBO_BASE_URL', 'https://problembo.com/apis/v1/client').rstrip('/')
MODEL = 'waifu-studio-2.6'
REAL_MODEL = os.getenv('PROBLEMBO_REAL_MODEL_ID','velvet-render-v5')
MALE_ANIME_MODEL = os.getenv('PROBLEMBO_MALE_ANIME_MODEL_ID','velvet-render-v5-anime')

class ProviderError(RuntimeError):
    def __init__(self,code,phase='generation'):
        self.code=str(code)[:80];self.phase=phase;super().__init__(self.code)

def error_code(exc):
    if isinstance(exc,ProviderError):return exc.code
    if isinstance(exc,(TimeoutError,httpx.TimeoutException)):return 'timeout'
    response=getattr(exc,'response',None)
    if response is not None:
        return {401:'authorization',403:'access_denied',429:'rate_limit',400:'invalid_request'}.get(response.status_code,'http_'+str(response.status_code))
    if isinstance(exc,httpx.RequestError):return 'network'
    if isinstance(exc,(ValueError,KeyError)):return 'invalid_response'
    return 'generation_failed'


def model_for(world=None,gender=None):
    return REAL_MODEL if world=='realism' else MALE_ANIME_MODEL if gender=='male' else MODEL


def token():
    return os.getenv('PROBLEMBO_API_TOKEN') or os.getenv('PROBLEMBO_API_KEY') or os.getenv('PROBLEMBO_TOKEN')


def negative_identity(gender=None,appearance=None,race=None):
    words=['child','minor','low quality','multiple people','two people','couple','split screen','collage','duplicate person','camera device','tripod','camera lens in frame','picture in picture','inset portrait','contact sheet','text','watermark','logo']
    if gender=='male':words+=['woman','girl','female','feminine breasts']
    elif gender=='female':words+=['man','boy','male','beard']
    kind=profile_options.race_kind(race)
    if kind=='mechanical':words+=['human skin','human face','human hair']
    elif kind in ('furry','scaled'):words+=['human face','bare human skin','human wearing animal ears','costume mask','quadruped','pet']
    elif kind=='alien':words+=['ordinary human face','human ears']
    hair=(appearance or {}).get('hair_color') if kind!='mechanical' else None
    colors={'silver':'white silver hair','black':'black hair','brown':'brown hair','red':'red auburn hair','pink':'pink hair','blue':'blue hair','purple':'purple hair','blonde':'blond hair'}
    if hair in colors:words += [value for key,value in colors.items() if key!=hair]
    return ', '.join(words)


async def generate(prompt, *, world=None, gender=None, appearance=None, race=None):
    if not token():
        raise RuntimeError('Problembo token missing')
    if profile_options.race_kind(race)!='humanoid':
        prefix='solo, adult '+profile_options.photo_subject(race,gender)+', age 25+, '+profile_options.RACE_FACTS[race]+'. '
    else:prefix=('solo, 1boy, adult man, ' if gender=='male' else 'solo, 1girl, adult woman, ') if gender else ''
    headers = {'Authorization': 'Bearer ' + token()}
    async with httpx.AsyncClient(timeout=25) as client:
        response = await client.post(BASE_URL + '/image-gen/tasks', headers=headers, json={
            'modelId': model_for(world,gender), 'prompt': prefix+prompt, 'aspectRatio':'VERTICAL', 'negativePrompt': negative_identity(gender,appearance,race), 'imageCount': 1})
        response.raise_for_status()
        task_id = response.json()['taskId']
        for _ in range(80):
            await asyncio.sleep(3)
            response = await client.get(BASE_URL + '/tasks/' + task_id, headers=headers)
            response.raise_for_status()
            task = response.json()
            if task.get('ready'):
                if task.get('status') != 'END_SUCCESS':
                    raise ProviderError((task.get('error') or {}).get('key') or task.get('status') or 'generation_failed')
                url = task['result']['taskResult'][0]['url']
                async with client.stream('GET', url) as image:
                    image.raise_for_status()
                    raw = bytearray()
                    async for part in image.aiter_bytes():
                        raw.extend(part)
                        if len(raw) > 12 * 1024 * 1024:
                            raise RuntimeError('Image too large')
                raw = bytes(raw)
                ext = 'jpg' if raw.startswith(b'\xff\xd8\xff') else 'png' if raw.startswith(b'\x89PNG\r\n\x1a\n') else 'webp' if raw[:4] == b'RIFF' and raw[8:12] == b'WEBP' else None
                if not ext:
                    raise ProviderError('invalid_image','download')
                return raw, ext
        raise TimeoutError('Image generation timed out')


async def edit(prompt, references):
    """Two ordered identity references; the image-edit contract accepts public HTTPS URLs.

    This is deliberately separate from the solo image-gen payload, whose negative
    prompt forbids couples. The default editor is documented as multi-reference.
    """
    if not token():raise RuntimeError('Problembo token missing')
    if len(references)!=2 or any(not isinstance(url,str) or not url.startswith('https://') for url in references):
        raise ValueError('Two HTTPS references required')
    headers={'Authorization':'Bearer '+token()}
    async with httpx.AsyncClient(timeout=25) as client:
        response=await client.post(BASE_URL+'/image-edit/tasks',headers=headers,json={
            'modelId':os.getenv('PROBLEMBO_COUPLE_MODEL_ID','image-gpt-v3.6'),
            'prompt':prompt,'sourceImageFileIds':references,'imageCount':1})
        response.raise_for_status()
        task_id=response.json()['taskId']
        for _ in range(100):
            await asyncio.sleep(3)
            response=await client.get(BASE_URL+'/tasks/'+task_id,headers=headers)
            response.raise_for_status();task=response.json()
            if not task.get('ready'):continue
            if task.get('status')!='END_SUCCESS':raise RuntimeError('Image editing failed')
            url=task['result']['taskResult'][0]['url']
            async with client.stream('GET',url) as image:
                image.raise_for_status();raw=bytearray()
                async for part in image.aiter_bytes():
                    raw.extend(part)
                    if len(raw)>12*1024*1024:raise RuntimeError('Image too large')
            raw=bytes(raw)
            ext='jpg' if raw.startswith(b'\xff\xd8\xff') else 'png' if raw.startswith(b'\x89PNG\r\n\x1a\n') else 'webp' if raw[:4]==b'RIFF' and raw[8:12]==b'WEBP' else None
            if not ext:raise ProviderError('invalid_image','download')
            return raw,ext
        raise TimeoutError('Image editing timed out')
