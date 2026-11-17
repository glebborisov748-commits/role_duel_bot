"""Problembo image-gen contract: https://problembo.com/docs/dev ."""
import asyncio
import os
import httpx

BASE_URL = os.getenv('PROBLEMBO_BASE_URL', 'https://problembo.com/apis/v1/client').rstrip('/')
MODEL = 'waifu-studio-2.6'
REAL_MODEL = os.getenv('PROBLEMBO_REAL_MODEL_ID','velvet-render-v5')
MALE_ANIME_MODEL = os.getenv('PROBLEMBO_MALE_ANIME_MODEL_ID','velvet-render-v5-anime')

def model_for(world=None,gender=None):
    return REAL_MODEL if world=='realism' else MALE_ANIME_MODEL if gender=='male' else MODEL


def token():
    return os.getenv('PROBLEMBO_API_TOKEN') or os.getenv('PROBLEMBO_API_KEY') or os.getenv('PROBLEMBO_TOKEN')


def negative_identity(gender=None,appearance=None):
    words=['child','minor','low quality','multiple people','two people','couple','split screen','collage','duplicate person']
    if gender=='male':words+=['woman','girl','female','feminine breasts']
    elif gender=='female':words+=['man','boy','male','beard']
    hair=(appearance or {}).get('hair_color')
    colors={'silver':'white silver hair','black':'black hair','brown':'brown hair','red':'red auburn hair','pink':'pink hair','blue':'blue hair','purple':'purple hair','blonde':'blond hair'}
    if hair in colors:words += [value for key,value in colors.items() if key!=hair]
    return ', '.join(words)


async def generate(prompt, *, world=None, gender=None, appearance=None):
    if not token():
        raise RuntimeError('Problembo token missing')
    headers = {'Authorization': 'Bearer ' + token()}
    async with httpx.AsyncClient(timeout=25) as client:
        response = await client.post(BASE_URL + '/image-gen/tasks', headers=headers, json={
            'modelId': model_for(world,gender), 'prompt': (('solo, 1boy, adult man, ' if gender=='male' else 'solo, 1girl, adult woman, ') if gender else '')+prompt, 'aspectRatio':'VERTICAL', 'negativePrompt': negative_identity(gender,appearance), 'imageCount': 1})
        response.raise_for_status()
        task_id = response.json()['taskId']
        for _ in range(80):
            await asyncio.sleep(3)
            response = await client.get(BASE_URL + '/tasks/' + task_id, headers=headers)
            response.raise_for_status()
            task = response.json()
            if task.get('ready'):
                if task.get('status') != 'END_SUCCESS':
                    raise RuntimeError('Image generation failed')
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
                    raise RuntimeError('Invalid image')
                return raw, ext
        raise TimeoutError('Image generation timed out')
