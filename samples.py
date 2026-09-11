"""Load one-click Lyria samples from sample_assets/. No credentials here."""
from __future__ import annotations

import json
from pathlib import Path

from catalog import WORKSPACES

ENGINES = {item['id'] for item in WORKSPACES}
ROOT = Path(__file__).resolve().parent
ASSETS = ROOT / 'sample_assets'
REQUIRED = ('id', 'title', 'group', 'note', 'engine', 'config')


def load_samples() -> list[dict]:
    index = json.loads((ASSETS / 'index.json').read_text(encoding='utf-8'))
    samples = []
    for name in index['samples']:
        path = ASSETS / name
        data = json.loads(path.read_text(encoding='utf-8'))
        missing = [key for key in REQUIRED if key not in data]
        if missing:
            raise ValueError(f'{name} 缺少字段：{missing}')
        if data['engine'] not in ENGINES:
            raise ValueError(f'{name} 的 engine 必须是 {sorted(ENGINES)} 之一')
        data['file'] = name
        samples.append(data)
    return samples
