"""Problembo image-gen contract: https://problembo.com/docs/dev ."""
import asyncio
import os
import httpx

BASE_URL = os.getenv('PROBLEMBO_BASE_URL', 'https://problembo.com/apis/v1/client').rstrip('/')
MODEL = 'waifu-studio-2.6'


def token():
    return os.getenv('PROBLEMBO_API_TOKEN') or os.getenv('PROBLEMBO_API_KEY') or os.getenv('PROBLEMBO_TOKEN')


async def generate(prompt):
    if not token():
        raise RuntimeError('Problembo token missing')
    headers = {'Authorization': 'Bearer ' + token()}
    async with httpx.AsyncClient(timeout=25) as client:
        response = await client.post(BASE_URL + '/image-gen/tasks', headers=headers, json={
            'modelId': MODEL, 'prompt': prompt, 'negativePrompt': 'nsfw, nude, naked, explicit, child, minor, low quality', 'imageCount': 1})
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
