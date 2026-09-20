"""Lyria demo. Local: uvicorn app:app --host 127.0.0.1 --port 8004. Cloud Run: Procfile / K_SERVICE."""
from __future__ import annotations

import json
import os
import threading
import time
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request as WebRequest
from fastapi.exceptions import RequestValidationError
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.trustedhost import TrustedHostMiddleware

from catalog import (
    API_OUT_OF_DEMO, CHECKED, COMPARE_API, COMPARE_METHODS, COMPARE_MODELS, DOCS,
    FEATURE_BLURBS, FEATURE_VALUE, FIT_GUIDE, MODEL_CARDS, MODEL_RULES, MODELS,
    SESSION_LIMITS, VOCAL_LANGUAGES, WHY_NOT_LYRIA, WORKSPACES, ENGINE_LOCATIONS,
)
from lyria import Request, UserError, adc_available, error_payload, generate, plan, require_auth
from samples import load_samples

ROOT = Path(__file__).resolve().parent
load_dotenv(ROOT / '.env')
SAMPLES = load_samples()


def allowed_hosts() -> list[str]:
    """Local loopback by default; Cloud Run (K_SERVICE) also allows *.run.app; optional ALLOWED_HOSTS."""
    hosts = ['localhost', '127.0.0.1', '[::1]', 'testserver']
    if os.getenv('K_SERVICE'):
        hosts.append('*.run.app')
    for item in os.getenv('ALLOWED_HOSTS', '').split(','):
        host = item.strip()
        if host and host not in hosts:
            hosts.append(host)
    return hosts


def bind_host_port(default_port: str = '8004') -> tuple[str, int]:
    if os.getenv('K_SERVICE'):
        return '0.0.0.0', int(os.getenv('PORT') or '8080')
    return '127.0.0.1', int(os.getenv('DEMO_PORT') or default_port)


def same_origin(origin: str, request: WebRequest) -> bool:
    """Allow same-page POSTs. Cloud Run may rewrite scheme/host vs browser Origin."""
    from urllib.parse import urlparse
    parsed = urlparse(origin)
    if not parsed.netloc:
        return False
    candidates = {
        request.headers.get('x-forwarded-host', '').split(',')[0].strip(),
        request.headers.get('host', '').strip(),
        request.url.hostname or '',
        urlparse(str(request.base_url)).netloc,
    }
    if parsed.netloc in {item for item in candidates if item}:
        return True
    # Cloud Run serves two hostnames per service; Origin/Host can disagree.
    if os.getenv('K_SERVICE'):
        origin_host = (parsed.hostname or '').lower()
        req_host = (request.headers.get('host') or '').split(':')[0].lower()
        if origin_host.endswith('.run.app') and req_host.endswith('.run.app'):
            return True
    return False


app = FastAPI(title='配乐实验室', description='Lyria · 本地教学 Demo')
app.add_middleware(TrustedHostMiddleware, allowed_hosts=allowed_hosts())
app.mount('/static', StaticFiles(directory=ROOT / 'static'), name='static')
generation_lock = threading.Lock()
MAX_BODY = 140_000_000  # Interactions inline ~100 MB raw ≈ ~133 MB base64 JSON + prompt


@app.middleware('http')
async def local_only(request: WebRequest, call_next):
    if request.method == 'POST':
        origin = request.headers.get('origin')
        if origin and not same_origin(origin, request):
            return JSONResponse({'detail': '请从本 Demo 页面发起请求。'}, status_code=403)
        if request.headers.get('content-type', '').split(';')[0] != 'application/json':
            return JSONResponse({'detail': '需要 JSON 请求。'}, status_code=415)
        body = await request.body()
        if len(body) > MAX_BODY:
            return JSONResponse(
                {'detail': '请求过大。Interactions 内联合计大约 100 MB；请减少图片或改用更小的 JPEG。'},
                status_code=413,
            )
    response = await call_next(request)
    response.headers['Cache-Control'] = 'no-store'
    response.headers['X-Content-Type-Options'] = 'nosniff'
    return response


@app.exception_handler(RequestValidationError)
async def invalid_request(request, exc):
    return JSONResponse({'detail': '输入格式或长度不正确，请检查提示词、歌词和图片。'}, status_code=422)


@app.get('/')
def home():
    return FileResponse(ROOT / 'static' / 'index.html')


@app.get('/api/catalog')
def catalog():
    return {
        'models': MODELS,
        'model_cards': MODEL_CARDS,
        'workspaces': WORKSPACES,
        'samples': SAMPLES,
        'compare_models': COMPARE_MODELS,
        'compare_methods': COMPARE_METHODS,
        'compare_api': COMPARE_API,
        'why_not_lyria': WHY_NOT_LYRIA,
        'fit_guide': FIT_GUIDE,
        'session_limits': SESSION_LIMITS,
        'feature_value': FEATURE_VALUE,
        'feature_blurbs': FEATURE_BLURBS,
        'api_out_of_demo': API_OUT_OF_DEMO,
        'model_rules': MODEL_RULES,
        'vocal_languages': VOCAL_LANGUAGES,
        'docs': DOCS,
        'checked': CHECKED,
        'project_configured': bool(os.getenv('GOOGLE_CLOUD_PROJECT')),
        'adc_configured': adc_available(),
        'engine_locations': ENGINE_LOCATIONS,
        'location_raw': os.getenv('GOOGLE_CLOUD_LOCATION', 'global'),
    }


@app.get('/api/doc/{name}')
def document(name: str):
    files = {'readme': 'README.md', 'guide': 'learning_guide.md', 'sources': 'docs/official_sources.md'}
    if name not in files:
        raise HTTPException(404)
    path = ROOT / files[name]
    if not path.is_file():
        raise HTTPException(404)
    return {'text': path.read_text(encoding='utf-8')}


@app.post('/api/preview')
def preview_route(r: Request):
    try:
        return plan(r)
    except UserError as error:
        raise HTTPException(400, str(error)) from None


def event(data):
    return json.dumps(data, ensure_ascii=False) + '\n'


@app.post('/api/generate')
def generate_route(r: Request):
    try:
        planned = plan(r)
        require_auth()
    except UserError as error:
        raise HTTPException(400, str(error)) from None

    def run():
        if not generation_lock.acquire(blocking=False):
            yield event({'type': 'error', 'message': '已有生成任务运行中，请完成或停止后再试。'})
            return
        started = time.monotonic()
        try:
            yield event({
                'type': 'start',
                'api': planned['api'],
                'model': planned['model'],
                'location': planned['location'],
                'format': planned['format'],
                'warnings': planned.get('warnings') or [],
            })
            result = generate(r)
            yield event({
                'type': 'done',
                'seconds': round(time.monotonic() - started, 2),
                'bytes': result['bytes'],
                'mime': result['mime'],
                'text': result.get('text') or '',
                'audio': result['audio_b64'],
                'clips': result.get('clips') or [],
            })
        except UserError as error:
            yield event({'type': 'error', 'message': str(error)})
        except Exception as error:
            payload = error_payload(error)
            print(f'[generate] {payload["error_type"]}: {error}', flush=True)
            yield event({'type': 'error', **payload})
        finally:
            generation_lock.release()

    return StreamingResponse(run(), media_type='application/x-ndjson', headers={'X-Accel-Buffering': 'no'})


if __name__ == '__main__':
    import uvicorn
    host, port = bind_host_port('8004')
    uvicorn.run('app:app', host=host, port=port, reload=False)
