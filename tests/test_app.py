from __future__ import annotations

from catalog import MODEL_CLIP, MODEL_SCORE, MODEL_SONG, WORKSPACES


def test_home_and_static(client):
    home = client.get('/')
    assert home.status_code == 200
    assert '配乐实验室' in home.text and 'id="workspaces"' in home.text
    assert 'data-page="clip"' in home.text and 'data-page="song"' in home.text
    assert 'data-page="score"' in home.text
    assert 'id="session-limits"' in home.text
    assert '能撑多久' in home.text
    assert '不是万能' in home.text
    css = client.get('/static/style.css')
    js = client.get('/static/app.js')
    assert css.status_code == 200 and js.status_code == 200
    assert 'sample.engine===active' in js.text
    assert '本页场景样例' in js.text
    assert 'featureBlock' in js.text
    assert '开了会怎样' in js.text
    assert '.limit-impact' in css.text
    assert '/api/generate' in js.text
    assert 'htmlTable(catalog.session_limits)' not in js.text.split('function pageIntro')[1].split('function pageDocs')[0]
    assert 'limit_impact' in js.text.split('function pageIntro')[1].split('function pageDocs')[0]


def test_catalog_and_docs(client):
    catalog = client.get('/api/catalog').json()
    assert catalog['checked'] == '2026-09-11'
    assert catalog['project_configured'] is False
    assert [item['id'] for item in catalog['workspaces']] == ['clip', 'song', 'score']
    assert all(item.get('docs') and item.get('fit') and item.get('surface') and item.get('positioning') for item in catalog['workspaces'])
    clip = next(item for item in catalog['workspaces'] if item['id'] == 'clip')
    assert clip['model'] == MODEL_CLIP
    assert 'image' in clip['features']
    song = next(item for item in catalog['workspaces'] if item['id'] == 'song')
    assert song['model'] == MODEL_SONG
    assert 'timestamps' in song['features']
    score = next(item for item in catalog['workspaces'] if item['id'] == 'score')
    assert score['model'] == MODEL_SCORE
    assert 'negative' in score['features'] and 'seed' in score['features']
    assert catalog['engine_locations']['clip'] == 'global'
    assert catalog['engine_locations']['score'] == 'us-central1'
    assert catalog['session_limits'][0][2] == '对业务意味着什么'
    assert any('打字' not in row[0] for row in catalog['session_limits'][1:])
    assert any('184' in row[1] for row in catalog['session_limits'][1:])
    assert clip.get('limit_impact')
    assert catalog['feature_value'][0][2] == '业务价值'
    assert catalog['api_out_of_demo'][0][1] == '业务价值'
    assert any('RealTime' in row[0] for row in catalog['api_out_of_demo'])
    assert any('PDF' in row[0] or 'GCS' in row[0] for row in catalog['api_out_of_demo'])
    assert not any('最多 3 张' in row[2] for row in catalog['api_out_of_demo'][1:])
    assert not any('一次最多约 10 张' in row[0] for row in catalog['api_out_of_demo'][1:])
    assert not any('TTS' in row[0] or 'Live' in row[0] or 'Chirp' in row[0] for row in catalog['api_out_of_demo'][1:])
    samples = catalog['samples']
    assert len(samples) >= 10
    assert {item['engine'] for item in samples} == {'clip', 'song', 'score'}
    assert WORKSPACES[0]['id'] == 'clip'
    for name in ('readme', 'guide', 'sources'):
        body = client.get(f'/api/doc/{name}').json()['text']
        assert 'Lyria' in body
    assert client.get('/api/doc/missing').status_code == 404


def test_preview_ok_and_validation(client):
    ok = client.post('/api/preview', json={
        'engine': 'clip', 'model': MODEL_CLIP,
        'prompt': 'A short instrumental acoustic guitar piece.',
        'instrumental': True,
    })
    assert ok.status_code == 200
    body = ok.json()
    assert body['api'] == 'interactions'
    assert body['location'] == 'global'
    assert body['request']['model'] == MODEL_CLIP
    assert body['request']['input'][0]['type'] == 'text'
    assert 'Instrumental' in body['prompt']

    song = client.post('/api/preview', json={
        'engine': 'song', 'model': MODEL_SONG,
        'prompt': 'Create a 90-second jazz ballad.',
        'lyrics': '[Chorus]\nHold on tight',
    })
    assert song.status_code == 200
    assert 'Lyrics:' in song.json()['prompt'] or '[Chorus]' in song.json()['prompt']

    score = client.post('/api/preview', json={
        'engine': 'score', 'model': MODEL_SCORE,
        'prompt': 'An uplifting orchestral piece.',
        'negative_prompt': 'vocals',
        'seed': '12',
        'sample_count': 1,
    })
    assert score.status_code == 200
    scored = score.json()
    assert scored['api'] == 'predict'
    assert scored['location'] == 'us-central1'
    assert scored['request']['instances'][0]['seed'] == 12
    assert 'sample_count' not in scored['request']['parameters']

    wrong = client.post('/api/preview', json={
        'engine': 'clip', 'model': MODEL_SONG, 'prompt': 'hello',
    })
    assert wrong.status_code == 400

    both = client.post('/api/preview', json={
        'engine': 'score', 'model': MODEL_SCORE,
        'prompt': 'folk guitar', 'seed': '1', 'sample_count': 2,
    })
    assert both.status_code == 400

    image_on_score = client.post('/api/preview', json={
        'engine': 'score', 'model': MODEL_SCORE,
        'prompt': 'folk guitar',
        'images': [{'mime_type': 'image/jpeg', 'data': 'AAAAAAAA'}],
    })
    assert image_on_score.status_code == 400

    mandarin = client.post('/api/preview', json={
        'engine': 'clip', 'model': MODEL_CLIP, 'prompt': '一首快乐的中文流行歌',
    })
    assert mandarin.status_code == 200
    assert any('中文' in note for note in mandarin.json()['warnings'])

    generate = client.post('/api/generate', json={
        'engine': 'clip', 'model': MODEL_CLIP, 'prompt': 'A short guitar piece.',
    })
    assert generate.status_code == 400
