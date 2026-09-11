# Lyria 官方参考资料索引

核查日期：2026-09-11。检索范围：Google Cloud Documentation · Gemini Enterprise Agent Platform · Gemini API music generation。

本项目不是 Google 官方产品。“全部”指覆盖本 Demo 用到的主干文档，不宣称穷尽历史版本、论坛帖或未来页面。

官方把 Lyria 定位成 **从提示词（和可选图片）生成音乐**，不是 TTS、不是 Live、不是会议系统。顶栏三页对应三种入口，不要指望一个按钮万能。

## 先读这几个

| 官方链接 | 能解决的问题 | 对应项目位置 |
| --- | --- | --- |
| [Lyria 概览](https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/music/overview) | 3 Clip 30 秒；3 Pro 最多约 184 秒带结构与人声；SynthID | 入门页；catalog.py |
| [用 Lyria 生成音乐](https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/music/generate-music) | Interactions（global）vs lyria-002 predict；图的 uri / data | 短片 / 成曲 / 配乐；lyria.py |
| [Lyria 3 模型卡](https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/lyria/lyria-3) | 30 秒 / 184 秒、44.1 kHz MP3、8 种歌声语言、Lyria 3 无 negative_prompt | 入门页「能撑多久」 |
| [提示词指南](https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/music/music-gen-prompt-guide) | 体裁框架、歌词、时间戳、BPM、Intensity、最多约 10 张图或 PDF | 第 02 步开关；样例 |
| [Lyria 2 API](https://docs.cloud.google.com/gemini-enterprise-agent-platform/reference/models/lyria-music-generation) | prompt / negative_prompt / seed / sample_count；约 32.8 秒 WAV | 配乐页 |
| [ADC 配置](https://docs.cloud.google.com/docs/authentication/provide-credentials-adc) | 本地登录 | README 第 1 节 |

## 能力与边界

| 官方链接 | 用途 |
| --- | --- |
| [Interactions API](https://docs.cloud.google.com/gemini-enterprise-agent-platform/reference/models/interactions-api) | Vertex 上 Lyria 3 的正式调用。不要用 generateContent |
| [Gemini API：Lyria 音乐生成](https://ai.google.dev/gemini-api/docs/music-generation) | API Key 路径可用 `lyria-3.5`；本 Demo 不走这条。RealTime 流式合奏见该页说明 |
| [启用 Vertex AI API](https://console.cloud.google.com/flows/enableapi?apiid=aiplatform.googleapis.com) | 403 / API 未启用 |

## 相关但不是本 Demo 的路径

这些页面容易和 Lyria 搜到一起。

| 官方链接 | 为什么不是本页 |
| --- | --- |
| [Cloud TTS](https://docs.cloud.google.com/text-to-speech/docs) | 念稿，不是作曲 |
| [Gemini Live](https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/live-api) | 实时对话，不是出一首 MP3 |
