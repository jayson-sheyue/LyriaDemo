"""最小可运行的 Vertex Lyria 3 Clip 示例：一段提示词，收下 MP3。

用法（在项目根目录）：
    .venv/bin/python examples/quickstart.py

需要：
    gcloud auth application-default login
    gcloud auth application-default set-quota-project YOUR_PROJECT_ID
    .env 里的 GOOGLE_CLOUD_PROJECT
    已启用 aiplatform.googleapis.com

这会发起一次真实的付费/配额调用。
对照：https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/music/generate-music
"""
from __future__ import annotations

import base64
import os
from pathlib import Path

from dotenv import load_dotenv
from google import genai

from lyria import extract_interaction

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / '.env')

OUT = ROOT / 'outputs' / 'quickstart.mp3'
MODEL = 'lyria-3-clip-preview'
LOCATION = 'global'
PROMPT = 'A short instrumental acoustic guitar piece, warm and intimate.'


def main() -> None:
    project = (os.getenv('GOOGLE_CLOUD_PROJECT') or '').strip()
    if not project:
        raise SystemExit('请在 .env 填写 GOOGLE_CLOUD_PROJECT')
    client = genai.Client(vertexai=True, project=project, location=LOCATION)
    interaction = client.interactions.create(model=MODEL, input=PROMPT)
    audio, _mime, text = extract_interaction(interaction)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_bytes(audio)
    print(f'wrote {OUT} ({len(audio)} bytes)')
    if text:
        print(text[:500])


if __name__ == '__main__':
    main()
