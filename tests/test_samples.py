from __future__ import annotations

from samples import load_samples


def test_samples_cover_three_engines():
    samples = load_samples()
    engines = {item['engine'] for item in samples}
    assert engines == {'clip', 'song', 'score'}
    assert len(samples) >= 10
    assert all(item['config'].get('prompt') for item in samples)
