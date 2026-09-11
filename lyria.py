"""Lyria adapters. Preview does not call Google."""
from __future__ import annotations

import base64
import os
import re
import traceback
from typing import Any, Literal

from pydantic import BaseModel, Field

from catalog import ENGINE_LOCATIONS, MODEL_CLIP, MODEL_SCORE, MODEL_SONG, MODELS, WORKSPACES

MAX_PROMPT = 8000
MAX_LYRICS = 4000
# Official Lyria prompt guide: up to 10 reference images or PDFs.
MAX_IMAGES = 10
# Interactions inline payload: 100 MB per request (PDFs 50 MB). Demo only accepts JPEG/PNG.
MAX_INLINE_BYTES = 100 * 1024 * 1024
MAX_IMAGE_B64_CHARS = (MAX_INLINE_BYTES * 4) // 3 + 8
ALLOWED_IMAGE_TYPES = {'image/jpeg', 'image/png'}
CJK = re.compile(r'[\u3400-\u9fff]')

WORKSPACE_INDEX = {item['id']: item for item in WORKSPACES}


class UserError(ValueError):
    pass


class ImagePart(BaseModel):
    mime_type: str = Field(max_length=40)
    data: str = Field(min_length=8, max_length=MAX_IMAGE_B64_CHARS)


class Request(BaseModel):
    engine: Literal['clip', 'song', 'score'] = 'clip'
    model: str = MODEL_CLIP
    prompt: str = Field(default='', max_length=MAX_PROMPT)
    lyrics: str = Field(default='', max_length=MAX_LYRICS)
    instrumental: bool = False
    negative_prompt: str = Field(default='', max_length=1000)
    seed: str = Field(default='', max_length=12)
    sample_count: int = Field(default=1, ge=1, le=2)
    images: list[ImagePart] = Field(default_factory=list, max_length=MAX_IMAGES)
    location: str = Field(default='', max_length=32)


def adc_available() -> bool:
    try:
        import google.auth
        credentials, _project = google.auth.default()
        return credentials is not None
    except Exception:
        return False


def require_auth() -> None:
    if not (os.getenv('GOOGLE_CLOUD_PROJECT') or '').strip():
        raise UserError('请在 .env 填写 GOOGLE_CLOUD_PROJECT，并运行：gcloud auth application-default login。预览无需凭据。')
    if not adc_available():
        raise UserError('未检测到 Application Default Credentials。请运行：gcloud auth application-default login，然后 gcloud auth application-default set-quota-project 你的项目ID，并重启服务。')


def workspace_model(engine: str) -> str:
    spec = WORKSPACE_INDEX.get(engine)
    if not spec:
        raise UserError('未知工作台。')
    return spec['model']


def compose_prompt(r: Request) -> str:
    parts = [r.prompt.strip()]
    if not parts[0]:
        raise UserError('请写一段音乐描述。短片和成曲用英文最稳；配乐页官方要求美式英语。')
    if r.instrumental:
        parts.append('Instrumental. No vocals.')
    lyrics = r.lyrics.strip()
    if lyrics:
        if r.engine == 'score':
            raise UserError('配乐页是器乐模型，没有歌词字段。要人声请用短片或成曲页。')
        if lyrics.lower().startswith('lyrics:') or lyrics.startswith('['):
            parts.append(lyrics)
        else:
            parts.append('Lyrics:\n' + lyrics)
    return '\n\n'.join(part for part in parts if part).strip()


def decode_images(r: Request) -> list[dict[str, str]]:
    out = []
    if r.engine == 'score' and r.images:
        raise UserError('Lyria 2 没有看图成曲。请去掉图片，或改用短片 / 成曲页。')
    if len(r.images) > MAX_IMAGES:
        raise UserError(f'最多 {MAX_IMAGES} 张参考图（官方上限）。')
    total = 0
    for item in r.images:
        mime = item.mime_type.lower().split(';')[0].strip()
        if mime == 'image/jpg':
            mime = 'image/jpeg'
        if mime not in ALLOWED_IMAGE_TYPES:
            raise UserError('图片只要 JPEG 或 PNG。PDF 和云上 URI 见入门页「网页故意没接」。')
        try:
            raw = base64.b64decode(item.data, validate=False)
        except Exception:
            raise UserError('图片不是合法的 Base64。') from None
        if not raw:
            raise UserError('图片内容为空。')
        total += len(raw)
        if total > MAX_INLINE_BYTES:
            raise UserError(
                f'参考图合计超过 {MAX_INLINE_BYTES // (1024 * 1024)} MB。'
                '这是 Interactions 内联数据官方上限；更大请用 File API / GCS URI。'
            )
        out.append({'type': 'image', 'mime_type': mime, 'data': item.data})
    return out


def parse_seed(r: Request) -> int | None:
    text = r.seed.strip()
    if not text:
        return None
    if r.engine != 'score':
        raise UserError('seed 只在配乐页（lyria-002）有效。')
    try:
        value = int(text)
    except ValueError:
        raise UserError('seed 必须是整数。') from None
    if value < 0:
        raise UserError('seed 必须是 0 或正整数。')
    return value


def warnings_for(r: Request, prompt: str) -> list[str]:
    notes = []
    if r.engine in {'clip', 'song'} and CJK.search(prompt + '\n' + r.lyrics):
        notes.append('官方歌声语言表没有中文。描述用英文更稳；硬写中文歌词可能被拦或唱成别的语言。')
    if r.engine == 'score' and CJK.search(prompt):
        notes.append('Lyria 2 官方要求 prompt 用美式英语。')
    if r.engine in {'clip', 'song'} and r.negative_prompt.strip():
        notes.append('Lyria 3 官方不支持 negative_prompt，已忽略「不要出现」。要排除元素请用配乐页。')
    if r.instrumental and r.lyrics.strip():
        notes.append('同时勾选了只要器乐又填了歌词。模型可能仍开口唱。只要垫乐请清空歌词。')
    if r.engine == 'song':
        notes.append('成曲可能要等一两分钟。最长大约 184 秒，时长请写在提示词里。')
    if r.engine == 'clip':
        notes.append('短片固定大约 30 秒。要主歌副歌请换成曲页。')
    return notes


def plan(r: Request) -> dict[str, Any]:
    expected = workspace_model(r.engine)
    if r.model != expected:
        raise UserError(f'这一页的模型是 {expected}，不要混用。')
    info = MODELS[expected]
    location = (r.location or '').strip() or ENGINE_LOCATIONS[r.engine]
    if r.engine in {'clip', 'song'} and location != 'global':
        raise UserError('Lyria 3 只支持 global。不要抄配乐页的 us-central1。')
    if r.engine == 'score' and location == 'global':
        raise UserError('lyria-002 是区域 predict 接口。本 Demo 用 us-central1，不要填 global。')
    prompt = compose_prompt(r)
    images = decode_images(r)
    seed = parse_seed(r)
    if r.engine == 'score' and seed is not None and r.sample_count != 1:
        raise UserError('seed 和一次出几条不能一起用。定稿用 seed、条数留 1；试听用条数、不要 seed。')
    if r.engine != 'score' and r.sample_count != 1:
        raise UserError('Lyria 3 每次 1 条。一次出几条只在配乐页。')

    if r.engine == 'score':
        instance: dict[str, Any] = {'prompt': prompt}
        negative = r.negative_prompt.strip()
        if negative:
            instance['negative_prompt'] = negative
        if seed is not None:
            instance['seed'] = seed
        parameters: dict[str, Any] = {}
        if seed is None:
            parameters['sample_count'] = r.sample_count
        body = {'instances': [instance], 'parameters': parameters}
        endpoint = (
            f'https://{location}-aiplatform.googleapis.com/v1/projects/'
            f'$PROJECT/locations/{location}/publishers/google/models/{MODEL_SCORE}:predict'
        )
        api = 'predict'
    else:
        payload: list[dict[str, Any]] = [{'type': 'text', 'text': prompt}, *images]
        body = {'model': expected, 'input': payload}
        endpoint = 'https://aiplatform.googleapis.com/v1beta1/projects/$PROJECT/locations/global/interactions'
        api = 'interactions'

    return {
        'api': api,
        'model': expected,
        'location': location,
        'endpoint': endpoint,
        'request': body,
        'prompt': prompt,
        'warnings': warnings_for(r, prompt),
        'format': 'wav' if r.engine == 'score' else 'mp3',
        'mime': 'audio/wav' if r.engine == 'score' else 'audio/mpeg',
        'card': info,
    }


def genai_client(location: str):
    from google import genai
    from google.genai import types
    require_auth()
    options = types.HttpOptions(timeout=360_000, retry_options=types.HttpRetryOptions(attempts=1))
    return genai.Client(
        vertexai=True,
        project=os.getenv('GOOGLE_CLOUD_PROJECT'),
        location=location,
        http_options=options,
    )


def _b64_bytes(value: Any) -> bytes | None:
    if value is None:
        return None
    if isinstance(value, (bytes, bytearray)):
        return bytes(value)
    if isinstance(value, str):
        return base64.b64decode(value)
    return None


def _collect_from_blocks(blocks: Any) -> tuple[bytes | None, str, list[str]]:
    audio = None
    mime = ''
    texts: list[str] = []
    if not blocks:
        return audio, mime, texts
    for block in blocks:
        if isinstance(block, dict):
            kind = block.get('type')
            if kind == 'audio' or block.get('mime_type') or block.get('data'):
                raw = _b64_bytes(block.get('data') or block.get('audioContent'))
                if raw:
                    audio = raw
                    mime = block.get('mime_type') or mime
            text = block.get('text')
            if text:
                texts.append(str(text))
            continue
        kind = getattr(block, 'type', None)
        data = getattr(block, 'data', None) or getattr(block, 'audio_content', None)
        text = getattr(block, 'text', None)
        if data:
            raw = _b64_bytes(data)
            if raw:
                audio = raw
                mime = getattr(block, 'mime_type', None) or mime
        if text:
            texts.append(str(text))
    return audio, mime, texts


def extract_interaction(result: Any) -> tuple[bytes, str, str]:
    audio = None
    mime = 'audio/mpeg'
    texts: list[str] = []
    try:
        generated = getattr(result, 'output_audio', None)
        if generated is not None:
            raw = _b64_bytes(getattr(generated, 'data', None))
            if raw:
                audio = raw
                mime = getattr(generated, 'mime_type', None) or mime
    except TypeError:
        pass
    try:
        text = getattr(result, 'output_text', None)
        if text:
            texts.append(str(text))
    except TypeError:
        pass

    extra = getattr(result, 'model_extra', None) or {}
    if isinstance(extra, dict):
        found, found_mime, found_text = _collect_from_blocks(extra.get('outputs'))
        if found:
            audio = found
            mime = found_mime or mime
        texts.extend(found_text)

    outputs = getattr(result, 'outputs', None)
    found, found_mime, found_text = _collect_from_blocks(outputs)
    if found:
        audio = found
        mime = found_mime or mime
    texts.extend(found_text)

    steps = getattr(result, 'steps', None) or []
    for step in steps:
        contents = getattr(step, 'contents', None) or getattr(step, 'content', None)
        if contents is None and isinstance(step, dict):
            contents = step.get('contents') or step.get('content') or [step]
        found, found_mime, found_text = _collect_from_blocks(contents if isinstance(contents, list) else [contents])
        if found:
            audio = found
            mime = found_mime or mime
        texts.extend(found_text)

    if not audio:
        raise UserError('没有收到音频。请检查项目、global 区域、模型 ID，以及提示词是否被安全过滤拦住。')
    seen: list[str] = []
    for item in texts:
        if item not in seen:
            seen.append(item)
    return audio, mime or 'audio/mpeg', '\n\n'.join(seen)


def generate_lyria3(r: Request, planned: dict[str, Any]) -> dict[str, Any]:
    client = genai_client(planned['location'])
    body = planned['request']
    result = client.interactions.create(model=body['model'], input=body['input'])
    audio, mime, text = extract_interaction(result)
    return {
        'audio_b64': base64.b64encode(audio).decode(),
        'mime': mime or planned['mime'],
        'text': text,
        'bytes': len(audio),
    }


def generate_lyria2(r: Request, planned: dict[str, Any]) -> dict[str, Any]:
    require_auth()
    import google.auth
    from google.auth.transport.requests import AuthorizedSession

    credentials, _project = google.auth.default(scopes=['https://www.googleapis.com/auth/cloud-platform'])
    session = AuthorizedSession(credentials)
    project = os.getenv('GOOGLE_CLOUD_PROJECT')
    location = planned['location']
    url = (
        f'https://{location}-aiplatform.googleapis.com/v1/projects/{project}'
        f'/locations/{location}/publishers/google/models/{MODEL_SCORE}:predict'
    )
    response = session.post(url, json=planned['request'], timeout=180)
    if response.status_code >= 400:
        raise UserError(f'lyria-002 调用失败（HTTP {response.status_code}）。{response.text[:800]}')
    payload = response.json()
    predictions = payload.get('predictions') or []
    clips = []
    for item in predictions:
        raw = _b64_bytes(item.get('audioContent') or item.get('bytesBase64Encoded'))
        if not raw:
            continue
        clips.append({
            'audio_b64': base64.b64encode(raw).decode(),
            'mime': item.get('mimeType') or 'audio/wav',
            'bytes': len(raw),
        })
    if not clips:
        raise UserError('没有收到 WAV。请检查区域 us-central1、lyria-002 是否开通，以及 prompt 是否用英语。')
    first = clips[0]
    return {
        'audio_b64': first['audio_b64'],
        'mime': first['mime'],
        'text': '',
        'bytes': first['bytes'],
        'clips': clips,
    }


def generate(r: Request) -> dict[str, Any]:
    planned = plan(r)
    require_auth()
    if planned['api'] == 'predict':
        return generate_lyria2(r, planned)
    return generate_lyria3(r, planned)


def error_payload(error: Exception) -> dict[str, str]:
    text = str(error)
    kind = type(error).__name__
    if '429' in text or 'Resource exhausted' in text:
        return {'error_type': kind, 'message': '配额用尽或请求太密。官方大约每分钟 10 次，请稍后再试。', 'detail': text[:2000]}
    if '404' in text or 'NOT_FOUND' in text:
        return {'error_type': kind, 'message': '模型不存在。Lyria 3 必须用 global；lyria-002 不要用 global。', 'detail': text[:2000]}
    if 'safety' in text.lower() or 'blocked' in text.lower() or 'recitation' in text.lower():
        return {'error_type': kind, 'message': '提示词或输出被安全过滤拦住（版权词、模仿歌手、不当内容）。请改提示词。', 'detail': text[:2000]}
    return {'error_type': kind, 'message': text[:400] or '生成失败。', 'detail': traceback.format_exc()[-4000:]}
