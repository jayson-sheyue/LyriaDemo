from __future__ import annotations

from catalog import MODEL_CLIP, MODEL_SCORE
from lyria import Request, UserError, extract_interaction, plan


def test_image_limits_match_official():
    from lyria import MAX_IMAGES, MAX_INLINE_BYTES
    assert MAX_IMAGES == 10
    assert MAX_INLINE_BYTES == 100 * 1024 * 1024


def test_clip_plan_rejects_wrong_region():
    try:
        plan(Request(engine='clip', model=MODEL_CLIP, prompt='guitar', location='us-central1'))
    except UserError as error:
        assert 'global' in str(error)
    else:
        raise AssertionError('expected UserError')


def test_score_plan_rejects_global():
    try:
        plan(Request(engine='score', model=MODEL_SCORE, prompt='orchestra', location='global'))
    except UserError as error:
        assert 'us-central1' in str(error) or 'global' in str(error)
    else:
        raise AssertionError('expected UserError')


class DummyAudio:
    def __init__(self, data, mime_type='audio/mpeg'):
        self.data = data
        self.mime_type = mime_type


class DummyVertex:
    def __init__(self):
        self.output_audio = None
        self.output_text = None
        self.model_extra = {
            'outputs': [
                {'type': 'text', 'text': 'verse one'},
                {'type': 'audio', 'mime_type': 'audio/mpeg', 'data': 'YWJjZA=='},
            ]
        }
        self.outputs = None
        self.steps = None


def test_extract_vertex_outputs_fallback():
    audio, mime, text = extract_interaction(DummyVertex())
    assert audio == b'abcd'
    assert 'mpeg' in mime
    assert 'verse' in text


def test_extract_output_audio_convenience():
    class Ok:
        output_audio = DummyAudio('Zm9v')
        output_text = 'hello'
        model_extra = {}
        outputs = None
        steps = None
    audio, _mime, text = extract_interaction(Ok())
    assert audio == b'foo'
    assert text == 'hello'
