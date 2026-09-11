"""Official Lyria snapshot, checked 2026-09-11. No credentials here.

Lyria 3 Clip / Pro use Vertex Interactions API at location=global.
Lyria 2 (lyria-002) uses publisher predict, typically us-central1.
This is Agent Platform music generation, not Cloud TTS and not Gemini Live.
"""
from __future__ import annotations


def _doc(title, url, why):
    return {'title': title, 'url': url, 'why': why}


CHECKED = '2026-09-11'

MODEL_CLIP = 'lyria-3-clip-preview'
MODEL_SONG = 'lyria-3-pro-preview'
MODEL_SCORE = 'lyria-002'

ENGINE_LOCATIONS = {
    'clip': 'global',
    'song': 'global',
    'score': 'us-central1',
}

VOCAL_LANGUAGES = [
    {'code': 'en', 'label': 'English'},
    {'code': 'de', 'label': 'German'},
    {'code': 'es', 'label': 'Spanish'},
    {'code': 'fr', 'label': 'French'},
    {'code': 'hi', 'label': 'Hindi'},
    {'code': 'ja', 'label': 'Japanese'},
    {'code': 'ko', 'label': 'Korean'},
    {'code': 'pt', 'label': 'Portuguese'},
]

DOC_OVERVIEW = _doc(
    'Lyria 概览',
    'https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/music/overview',
    'Lyria 3 出 30 秒短片；Lyria 3 Pro 出最多约 184 秒、带结构和人声的成曲。',
)
DOC_GENERATE = _doc(
    '用 Lyria 生成音乐',
    'https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/music/generate-music',
    'Lyria 3 走 Interactions（global）；Lyria 2 走 lyria-002:predict。',
)
DOC_MODELS = _doc(
    'Lyria 3 模型卡',
    'https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/lyria/lyria-3',
    'Clip 30 秒 / Pro 184 秒；44.1 kHz MP3；歌声 8 种语言；Lyria 3 没有 negative_prompt。',
)
DOC_PROMPT = _doc(
    'Lyria 提示词指南',
    'https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/music/music-gen-prompt-guide',
    '体裁+情绪+乐器+速度+人声+歌词。时间戳、BPM、Intensity 写进提示词。',
)
DOC_LYRIA2 = _doc(
    'Lyria 2 API（predict）',
    'https://docs.cloud.google.com/gemini-enterprise-agent-platform/reference/models/lyria-music-generation',
    'lyria-002：约 32.8 秒 48 kHz WAV 器乐。prompt 用美式英语。有 negative_prompt 和 seed。',
)
DOC_INTERACTIONS = _doc(
    'Interactions API',
    'https://docs.cloud.google.com/gemini-enterprise-agent-platform/reference/models/interactions-api',
    'Vertex 上 Lyria 3 的正式调用方式。不要用 generateContent。',
)
DOC_ADC = _doc(
    'ADC 配置',
    'https://docs.cloud.google.com/docs/authentication/provide-credentials-adc',
    '本地登录，不要把密钥写进前端。',
)
DOC_GEMINI_MUSIC = _doc(
    'Gemini API 上的 Lyria（对照，不是本 Demo）',
    'https://ai.google.dev/gemini-api/docs/music-generation',
    'API Key 那条可以用 lyria-3.5。本 Demo 只走 Vertex + ADC，模型 ID 是 lyria-3-pro-preview。',
)

MODELS = {
    MODEL_CLIP: {
        'label': 'Lyria 3 Clip · Preview',
        'api': 'interactions',
        'location': 'global',
        'duration': '固定大约 30 秒',
        'format': 'MP3 · 44.1 kHz · 192 kbps',
        'vocals': True,
    },
    MODEL_SONG: {
        'label': 'Lyria 3 Pro · Preview',
        'api': 'interactions',
        'location': 'global',
        'duration': '最多大约 184 秒，用提示词控制',
        'format': 'MP3 · 44.1 kHz · 192 kbps',
        'vocals': True,
    },
    MODEL_SCORE: {
        'label': 'Lyria 2 · lyria-002',
        'api': 'predict',
        'location': 'us-central1',
        'duration': '大约 32.8 秒',
        'format': 'WAV · 48 kHz · 器乐',
        'vocals': False,
    },
}

MODEL_CARDS = {
    MODEL_CLIP: '短广告、循环垫乐、先试提示词。每次固定大约 30 秒，不要指望它拉成完整单曲。',
    MODEL_SONG: '要主歌副歌、要人唱、要按时间轴配画面。最多大约 184 秒。生成比短片慢。',
    MODEL_SCORE: '只要器乐、要可复现（seed）、要 negative_prompt。没有人声，也没有看图成曲。',
}

MODEL_RULES = [
    ['能力', '短片 Clip', '成曲 Pro', '配乐 Lyria 2'],
    ['模型 ID', MODEL_CLIP, MODEL_SONG, MODEL_SCORE],
    ['调用', 'Interactions · location=global', 'Interactions · location=global', 'predict · 区域接口，本 Demo 用 us-central1'],
    ['时长', '固定约 30 秒', '最多约 184 秒，写进提示词', '约 32.8 秒'],
    ['格式', 'MP3 44.1 kHz', 'MP3 44.1 kHz', 'WAV 48 kHz'],
    ['人声 / 歌词', '有。8 种语言，没有普通话', '有。可自备歌词、时间戳', '没有。只要器乐'],
    ['看图成曲', '有。JPEG / PNG', '有。官方最多约 10 张图或 PDF', '没有'],
    ['negative_prompt / seed', '官方不支持', '官方不支持', '支持。seed 和 sample_count 不能一起用'],
    ['水印', 'SynthID；C2PA', 'SynthID；C2PA', 'SynthID'],
]

COMPARE_MODELS = [
    ['你的业务更像…', '优先试', '不要先试'],
    ['15–30 秒广告、循环 BGM、先试听提示词', '短片页', '一上来生成三分钟成曲'],
    ['要主歌副歌、要人唱、要按镜头卡点', '成曲页', '拿 Clip 硬凑完整单曲'],
    ['游戏垫乐、器乐可复现、不要人声', '配乐页', '用 Pro 再在提示词里写 instrumental'],
    ['念稿、客服电话、SSML', 'TTS Demo（另一个项目）', '让 Lyria 唱歌来当旁白'],
    ['实时对话、打断', 'Live Demo（另一个项目）', '把 Lyria 当语音助手'],
]

COMPARE_METHODS = [
    ['', '短片', '成曲', '配乐'],
    ['适合', '试听、循环、短广告', '发行级短单、片头片尾、带唱', '垫乐、可复现器乐'],
    ['输入', '英文描述 + 可选图 + 可选歌词', '描述 + 时间戳 + 歌词 + 可选图', '美式英语 prompt + 可选 negative / seed'],
    ['输出', '1 条 MP3', '1 条 MP3 + 歌词/结构文本', '1 条 WAV（或 sample_count 多条）'],
    ['等多久', '通常几十秒', '常要一两分钟', '通常几十秒'],
]

COMPARE_API = [
    ['路径', '本 Demo', '不要当成同一个按钮'],
    ['Vertex Interactions + ADC', '短片 / 成曲', 'Gemini API Key 的 lyria-3.5'],
    ['Vertex predict + ADC', '配乐 lyria-002', '把 Clip 的 Interactions 请求抄过来'],
    ['Lyria RealTime 流式合奏', '入门页「网页故意没接」', '用生成按钮冒充实时编曲'],
    ['Cloud TTS / Gemini Live', '另外两个 Demo', '让 Lyria 说话或听写'],
]

WHY_NOT_LYRIA = [
    ['场景', '为什么不是 Lyria', '该用什么'],
    ['客服电话、有声书、SSML 多角色', 'Lyria 是作曲，不是念稿', 'Cloud TTS / Gemini TTS'],
    ['门店接待、可打断对话', '没有 Live 会话，也没有 VAD', 'Gemini Live'],
    ['整场电影配乐、无限循环电台', 'Pro 最多约 184 秒；Clip / 002 大约半分钟', '分段生成再剪，或传统曲库'],
    ['克隆某位歌手、唱受版权保护的词', '有 vocal likeness / recitation 过滤，会被拦', '拿授权音色和词，不要对抗过滤器'],
    ['普通话流行歌当产品卖', '官方歌声语言表没有中文', '用 8 种支持语言，或只要器乐'],
]

FIT_GUIDE = [
    ['你的业务更像…', '优先试', '不要先试', '听哪条样例'],
    ['先证明「项目、ADC、global 能出声」', '短片页', '一上来生成完整单曲', '短片 · 器乐吉他'],
    ['短视频垫乐、循环', '短片页勾选只要器乐', '用配乐页再抱怨没有人声', '短片 · 学习垫乐'],
    ['片头要按秒卡点、要合唱进拍', '成曲页用时间戳样例', '指望 Clip 听懂 [02:10]', '成曲 · 时间轴'],
    ['品牌要固定一首器乐，每次一样', '配乐页填 seed', 'seed 和条数一起开', '配乐 · 可复现'],
    ['看着海报出配乐', '短片或成曲页上传图片', '配乐页找上传按钮', '短片 · 看着图'],
]

SESSION_LIMITS = [
    ['发生在哪', '大概多久会出事', '对业务意味着什么', '产品上怎么接', '官方文档'],
    [
        '短片页',
        '每条固定大约 30 秒；每次 1 条',
        '短广告、App 开屏、循环垫乐够用。不能当「一首完整单曲」。连点会撞大约 10 次/分钟的配额。',
        '先在这一页试提示词。要主歌副歌再换成曲页。',
        'Lyria 3 模型卡\nhttps://docs.cloud.google.com/gemini-enterprise-agent-platform/models/lyria/lyria-3',
    ],
    [
        '成曲页',
        '最多大约 184 秒；生成常要等一两分钟',
        '片头片尾、短宣传曲够用。不是三分钟广播剧，也不是无限电台。时长写在提示词里，没有滑杆。',
        '提示词写 create a 90-second song，或用 [mm:ss] 时间轴。先短片试风格再生成成曲。',
        '用 Lyria 生成音乐\nhttps://docs.cloud.google.com/gemini-enterprise-agent-platform/models/music/generate-music',
    ],
    [
        '配乐页',
        '大约 32.8 秒 WAV',
        '游戏垫乐、可复现器乐。没有人声。seed 和一次出几条不能一起用。',
        '要固定版本就填 seed、条数留 1。要排除人声用 negative_prompt，不要抄到 Clip/Pro。',
        'Lyria 2 API\nhttps://docs.cloud.google.com/gemini-enterprise-agent-platform/reference/models/lyria-music-generation',
    ],
    [
        '三页都有 · 配额与审核',
        '大约 10 次/分钟；违规提示会被拦',
        '现场连点会 429。涉版权歌词、模仿某歌手，过滤器会直接拒。',
        '排队、重试、换提示词。不要对抗 recitation / vocal likeness。',
        'Lyria 概览\nhttps://docs.cloud.google.com/gemini-enterprise-agent-platform/models/music/overview',
    ],
]

LIMIT_CLIP = {
    'title': '这一页能撑多久（对业务）',
    'lede': '短片是试听台，不是发行台。对照总表只在入门指南。',
    'items': [
        {
            'when': '做 15–30 秒广告或循环垫乐',
            'impact': '每条固定大约 30 秒，够短视频和开屏。不能拉成完整单曲。',
            'do': '风格不定时先在这一页试。要主歌副歌去成曲页。',
        },
        {
            'when': '展台连点「生成」',
            'impact': '配额大约每分钟 10 次，连点会失败。生成要几十秒，不是即时播放器。',
            'do': '先预览请求。一次一条。',
        },
    ],
}
LIMIT_SONG = {
    'title': '这一页能撑多久（对业务）',
    'lede': '成曲有上限。对照总表只在入门指南。',
    'items': [
        {
            'when': '要一首能播的短单、片头片尾',
            'impact': '最多大约 184 秒。三分钟广播、整场电影配乐不够。生成常要等一两分钟。',
            'do': '在提示词里写时长或时间戳。先用短片页定风格。',
        },
        {
            'when': '要普通话歌词',
            'impact': '官方歌声语言没有中文。硬写中文词可能被拦或唱成别的语言。',
            'do': '用人声时选 8 种支持语言之一。只要气氛可以改器乐。',
        },
    ],
}
LIMIT_SCORE = {
    'title': '这一页能撑多久（对业务）',
    'lede': '只要器乐。对照总表只在入门指南。',
    'items': [
        {
            'when': '游戏、应用要可复现的垫乐',
            'impact': '大约 32.8 秒。填了 seed，同提示词会尽量同一条。不能和「一次出几条」一起用。',
            'do': '定稿用 seed。试听用条数、不要 seed。',
        },
        {
            'when': '想排除鼓或人声',
            'impact': '只有这一页有 negative_prompt。抄到 Clip/Pro 会被忽略或报错。',
            'do': '排除项写在「不要出现」。提示词本身用美式英语。',
        },
    ],
}

FEATURE_VALUE = [
    ['功能 / 特性', '开了会怎样', '业务价值', '不要用来', '哪一页'],
    ['文本生成音乐', '一段描述变成 MP3 或 WAV', '广告、短视频、游戏垫乐的草稿', '当 TTS 念稿或当 Live 对话', '三页都有'],
    ['只要器乐', '提示词加上 instrumental，减少人声', '垫乐、循环、不要唱词的场合', '代替 Lyria 2 的 negative_prompt', '短片 / 成曲'],
    ['自备歌词', '在提示词里写 Lyrics: 或 [Verse]/[Chorus]', '品牌口号、指定唱词', '塞受版权保护的词去对抗过滤', '短片 / 成曲'],
    ['看图成曲', 'JPEG/PNG 和文字一起发给模型', '海报、分镜、包装图定情绪', '当视频配乐引擎；官方没有视频输入', '短片 / 成曲'],
    ['时间戳结构', '[mm:ss] 指定哪一秒进鼓、进合唱', '片头卡点、多场景短片', 'Clip 只有 30 秒，细时间轴请用成曲页', '成曲'],
    ['BPM / Intensity', '写在提示词里，例如 120 BPM、Intensity: 3/10', '和画面节奏对齐', '以为有独立 API 滑杆', '短片 / 成曲'],
    ['negative_prompt', '请求字段排除不想要的元素', '学习垫乐不要突然很吵', '用在 Lyria 3（官方不支持）', '配乐'],
    ['seed', '同一 prompt+seed，尽量吐出完全同一条 WAV（不是同音色换新旋律）', '版本冻结、评审反复听同一条', '和 sample_count 同时开；也不是绝对哈希', '配乐'],
    ['SynthID / C2PA', '生成音频带水印和凭证', '标明 AI 生成、合规留痕', '当「没有水印的发行母带」', '三页都有'],
]

FEATURE_BLURBS = {
    'instrumental': {
        'effect': '在提示词末尾加上 Instrumental. No vocals. 降低开口唱歌的概率。',
        'value': '短视频垫乐、游戏循环、不要唱词的品牌氛围。',
        'caution': '这不是 Lyria 2 的 negative_prompt。Lyria 3 官方没有排除字段。',
    },
    'lyrics': {
        'effect': '你写的词会拼进提示词。官方写法是 Lyrics: 或 [Verse]/[Chorus]。也可以只写主题让模型填词。',
        'value': '品牌口号、指定副歌、多语言对唱。',
        'caution': '官方歌声语言没有普通话。受保护歌词会被 recitation 过滤拦住。',
    },
    'image': {
        'effect': '把 JPEG/PNG 和文字一起放进 Interactions 的 input。模型按画面情绪作曲。不回传图片。',
        'value': '看着海报、分镜、包装出配乐。',
        'caution': '不是给视频配音。官方最多约 10 张图或 PDF；本页 JPEG/PNG 最多 10 张，内联合计约 100 MB。配乐页没有这个能力。',
    },
    'timestamps': {
        'effect': '用 [00:00] 或 [0:00 - 0:12] 规定哪一段进什么乐器、什么强度。',
        'value': '片头卡点、多场景短片、要副歌在某一秒进来。',
        'caution': 'Clip 固定约 30 秒，细时间轴请用成曲页。没有独立的 duration 请求字段。',
    },
    'negative': {
        'effect': 'Lyria 2 请求里的 negative_prompt，用来排除人声、过响镲片等。',
        'value': '学习垫乐、要干净器乐。',
        'caution': 'Lyria 3 官方不支持。不要抄到短片/成曲页。',
    },
    'seed': {
        'effect': '同一个 prompt + seed，模型会尽量复现完全同一条 WAV（旋律、编配、音色一起冻住）。不是「保留吉他音色但换一段新旋律」。不能和一次出几条一起用。',
        'value': '版本冻结、评审时反复听同一条，避免每次听感都飘。',
        'caution': '官方写的是 attempt（尽量），不是密码学保证。模型或服务一变，同一 seed 也可能变。',
    },
}

API_OUT_OF_DEMO = [
    ['能力', '业务价值', '为什么网页 Demo 不做', '客户接入文档'],
    [
        'Lyria RealTime 流式合奏',
        '边弹边听、实时改风格，像合奏而不是等一条 MP3',
        '那是另一条 WebSocket 产品，不是 Interactions 一次出一首。本页按钮会让人以为生成就是实时编曲。',
        'Gemini API：实时音乐生成\nhttps://ai.google.dev/gemini-api/docs/music-generation',
    ],
    [
        'PDF / GCS 图 / File API 大文件',
        '分镜 PDF、云上海报、超过内联约 100 MB 的素材直接定情绪',
        '本页只收浏览器里的 JPEG/PNG 内联。官方还支持 PDF、image.uri（GCS）和更大文件走 File API。',
        '用 Lyria 生成音乐\nhttps://docs.cloud.google.com/gemini-enterprise-agent-platform/models/music/generate-music',
    ],
]

WORKSPACES = [
    {
        'id': 'clip', 'nav': '短片',
        'eyebrow': 'LYRIA 3 CLIP · PREVIEW',
        'title': '先做出 30 秒，再决定要不要成曲。',
        'lead': '这一页是 lyria-3-clip-preview。Vertex Interactions，区域 global。每次固定大约 30 秒 MP3。可看图、可人声、可只要器乐。提示词用英文最稳。官方歌声语言没有普通话。',
        'positioning': {
            'official': '官方定位：Lyria 3 Clip。低延迟短片，适合试听、循环和精确节奏，不是完整单曲。',
            'this_page': '本页：一段描述（可选图）→ 一条大约 30 秒的 MP3。区域必须是 global。',
            'not_this': '不要用本页做：三分钟成曲、TTS 念稿、实时合奏、Lyria 2 的 negative_prompt。',
        },
        'model': MODEL_CLIP,
        'features': ['prompt', 'instrumental', 'lyrics', 'image'],
        'advantages': [
            '先在 30 秒里试风格，再花钱生成完整单曲。',
            '和成曲页同一套 Interactions，只是模型 ID 和时长不同。',
        ],
        'limit_impact': LIMIT_CLIP,
        'limit_note': '每次 1 条，大约 30 秒。Lyria 3 没有 negative_prompt。歌声语言没有普通话。生成音频带 SynthID。',
        'fit': [
            {'title': '适合', 'body': '短广告、循环垫乐、先试提示词、看着一张海报出 30 秒。'},
            {'title': '不适合', 'body': '完整单曲、器乐 seed 复现、实时编曲、普通话歌词产品。'},
        ],
        'coverage': '语言芯片是官方歌声 8 种语言，写进提示词，不是请求字段。',
        'surface': [
            'POST .../locations/global/interactions',
            'model=lyria-3-clip-preview',
            'input[].type=text',
            '可选 input[].type=image（JPEG/PNG）',
            '输出 audio/mpeg + 歌词/结构文本',
        ],
        'docs': [DOC_GENERATE, DOC_MODELS, DOC_PROMPT],
        'language_hint': '歌声语言写进提示词，例如 singing in Japanese。官方表：英语、德语、西班牙语、法语、印地语、日语、韩语、葡萄牙语。没有普通话。',
    },
    {
        'id': 'song', 'nav': '成曲',
        'eyebrow': 'LYRIA 3 PRO · PREVIEW',
        'title': '要主歌副歌、要人唱，用这一页。',
        'lead': '这一页是 lyria-3-pro-preview。同一条 Interactions，区域仍然是 global。最多大约 184 秒。时长、BPM、Intensity、时间戳都写进提示词，没有滑杆。生成常要等一两分钟。',
        'positioning': {
            'official': '官方定位：Lyria 3 Pro。完整短单，理解主歌/副歌/桥段，适合结构和人声。',
            'this_page': '本页：描述 + 可选歌词/时间轴/图片 → 一条最长约 184 秒的 MP3。',
            'not_this': '不要用本页做：30 秒循环试听（用短片页）、器乐 seed、TTS、三分钟广播剧。',
        },
        'model': MODEL_SONG,
        'features': ['prompt', 'instrumental', 'lyrics', 'image', 'timestamps'],
        'advantages': [
            '官方允许用提示词控制时长，并用 [mm:ss] 卡点。',
            '可自备歌词，或只写主题让模型填词。',
        ],
        'limit_impact': LIMIT_SONG,
        'limit_note': '最多大约 184 秒。没有 duration 请求字段。Lyria 3 没有 negative_prompt。歌声语言没有普通话。',
        'fit': [
            {'title': '适合', 'body': '短宣传曲、片头片尾、要人唱、要按镜头卡点。'},
            {'title': '不适合', 'body': '先试听（用短片）、可复现器乐（用配乐页）、整场电影。'},
        ],
        'coverage': '时间戳样例按官方 [mm:ss] / [0:00 - 0:12] 写法。',
        'surface': [
            'POST .../locations/global/interactions',
            'model=lyria-3-pro-preview',
            '提示词里的 duration / BPM / Intensity / [mm:ss]',
            'Lyrics: 或 [Verse]/[Chorus]',
            '可选图片',
        ],
        'docs': [DOC_GENERATE, DOC_MODELS, DOC_PROMPT],
        'language_hint': '和短片页同一张歌声语言表。没有普通话。多语言对唱写进提示词，例如 a vocal duet in English and French。',
    },
    {
        'id': 'score', 'nav': '配乐',
        'eyebrow': 'LYRIA 2 · PREDICT',
        'title': '只要器乐垫底，走另一条 API。',
        'lead': '这一页是 lyria-002 的 predict，不是 Interactions。默认区域 us-central1，不要抄短片页的 global。输出大约 32.8 秒 48 kHz WAV。提示词用美式英语。有 negative_prompt 和 seed。没有人声，也没有看图。',
        'positioning': {
            'official': '官方定位：Lyria 2。从文本生成器乐，30 秒量级 WAV。seed 与 sample_count 互斥。',
            'this_page': '本页：prompt + 可选排除项/seed → WAV。区域 us-central1。',
            'not_this': '不要用本页做：人声、看图成曲、完整单曲、把 Interactions 的 JSON 贴过来。',
        },
        'model': MODEL_SCORE,
        'features': ['prompt', 'negative', 'seed'],
        'advantages': [
            '要排除鼓、要同一条反复出现，只有这一页有请求字段。',
            '和 Lyria 3 不是同一条路：predict vs Interactions，WAV vs MP3，区域 vs global。',
        ],
        'limit_impact': LIMIT_SCORE,
        'limit_note': '大约 32.8 秒器乐。prompt 官方要求美式英语。seed 和一次出几条不能一起用。',
        'fit': [
            {'title': '适合', 'body': '游戏垫乐、可复现器乐、要用 negative_prompt。'},
            {'title': '不适合', 'body': '唱歌、看图、主歌副歌、实时合奏。'},
        ],
        'coverage': '这一页没有语言下拉：Lyria 2 不唱歌。',
        'surface': [
            'POST .../publishers/google/models/lyria-002:predict',
            'instances[].prompt',
            '可选 instances[].negative_prompt',
            '可选 instances[].seed 或 parameters.sample_count（互斥）',
            'predictions[].audioContent audio/wav',
        ],
        'docs': [DOC_LYRIA2, DOC_GENERATE, DOC_PROMPT],
        'language_hint': '官方要求 prompt 用 US English。不要在这一页找歌声语言。',
    },
]

DOCS = [DOC_OVERVIEW, DOC_GENERATE, DOC_MODELS, DOC_PROMPT, DOC_LYRIA2, DOC_INTERACTIONS, DOC_ADC, DOC_GEMINI_MUSIC]
