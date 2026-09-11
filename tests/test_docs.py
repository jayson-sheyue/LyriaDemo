from __future__ import annotations

from pathlib import Path

REQUIRED_URLS = [
    'https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/music/overview',
    'https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/music/generate-music',
    'https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/lyria/lyria-3',
    'https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/music/music-gen-prompt-guide',
    'https://docs.cloud.google.com/gemini-enterprise-agent-platform/reference/models/lyria-music-generation',
    'https://docs.cloud.google.com/gemini-enterprise-agent-platform/reference/models/interactions-api',
    'https://docs.cloud.google.com/docs/authentication/provide-credentials-adc',
    'https://ai.google.dev/gemini-api/docs/music-generation',
]


def test_required_docs_exist():
    root = Path(__file__).resolve().parents[1]
    for name in ('README.md', 'learning_guide.md', 'docs/official_sources.md'):
        assert (root / name).is_file()
        assert len((root / name).read_text(encoding='utf-8')) > 500


def test_official_index_covers_主干入口():
    text = (Path(__file__).resolve().parents[1] / 'docs/official_sources.md').read_text(encoding='utf-8')
    missing = [url for url in REQUIRED_URLS if url not in text]
    assert missing == []


def test_learning_guide_covers_can_and_cannot():
    text = (Path(__file__).resolve().parents[1] / 'learning_guide.md').read_text(encoding='utf-8')
    for needle in (
        '能干什么', '不能干什么', '短片', '成曲', '配乐',
        'lyria-3-clip-preview', 'lyria-3-pro-preview', 'lyria-002',
        'global', 'us-central1', '普通话', '184', '30 秒',
        'negative_prompt', 'Interactions', '能撑多久',
        '开了会怎样', '业务价值', '不要用来',
        '网页 Demo 故意没接', 'RealTime', 'SynthID',
    ):
        assert needle in text, needle
    readme = (Path(__file__).resolve().parents[1] / 'README.md').read_text(encoding='utf-8')
    assert 'GOOGLE_CLOUD_LOCATION=global' in readme
    assert '8004' in readme
    assert (Path(__file__).resolve().parents[1] / 'examples' / 'quickstart.py').is_file()
