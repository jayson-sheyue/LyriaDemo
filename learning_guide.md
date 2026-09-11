# Lyria 学习指南

核查日期：2026-09-11。这不是 Google 官方产品。

## 1. 能干什么 / 不能干什么

**Lyria = 作曲模型。** 你写一段描述（可选再给图），它吐出一段音乐。短片大约 30 秒；成曲最多大约 184 秒；配乐是另一代模型的大约 32.8 秒器乐 WAV。

**能干什么：** 短广告、循环垫乐、片头片尾、看着海报出配乐、指定歌词或时间轴、用 seed 冻住一条器乐。

**不能干什么：** 当 TTS 念稿、当 Live 语音助手、实时合奏（那是 Lyria RealTime）、克隆某位歌手、保证普通话流行歌、开一首无限长的电台。生成音频带 SynthID 水印。

---

## 2. 三页分别是谁

| 页 | 模型 | 区域 | 业务直觉 |
| --- | --- | --- | --- |
| 短片 | `lyria-3-clip-preview` | `global` | 先试 30 秒 |
| 成曲 | `lyria-3-pro-preview` | `global` | 要主歌副歌、要人唱 |
| 配乐 | `lyria-002` | `us-central1` | 只要器乐、要排除项、要同一条 |

短片和成曲是 **Interactions API**。配乐是 **predict**。JSON 不能互抄。

Vertex 上 Lyria 3 **不要** 走 `generateContent`。官方 CUJ 是 `client.interactions.create(...)`。

Gemini API Key 那条可以用 `lyria-3.5`。本 Demo 只走 Vertex + ADC，成曲模型 ID 是 `lyria-3-pro-preview`。

---

## 3. 提示词怎么写

官方框架：

`[Genre] + [Mood] + [Instrumentation] + [Tempo] + [Vocal style & language] + [Lyrics]`

- 只要器乐：写 `instrumental`（本页有勾选，会自动拼进去）。
- 自备歌词：`Lyrics:` 或 `[Verse]` / `[Chorus]`。
- 成曲卡点：`[00:15]` 或 `[0:00 - 0:12]`，可写 BPM、Intensity、调性。
- 歌声语言（Lyria 3）：英语、德语、西班牙语、法语、印地语、日语、韩语、葡萄牙语。**没有普通话。**
- Lyria 2 的 prompt 官方要求 **美式英语**。

出处：[提示词指南](https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/music/music-gen-prompt-guide)。

---

## 4. 能撑多久（按页看，对业务）

总对照表只在入门指南页。各工作台只写本页会碰到的情况。

**短片页：** 每条固定大约 **30 秒**。短广告、开屏、循环够用，不能当完整单曲。连点会撞大约每分钟 10 次的配额。

**成曲页：** 最多大约 **184 秒**。片头片尾够用，不是三分钟广播剧。时长写在提示词里，没有滑杆。生成常要等一两分钟。

**配乐页：** 大约 **32.8 秒** 器乐。seed 用来冻版本，不能和一次出几条一起用。

出处：[Lyria 3 模型卡](https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/lyria/lyria-3)、[Lyria 2 API](https://docs.cloud.google.com/gemini-enterprise-agent-platform/reference/models/lyria-music-generation)。

---

## 5. 每个开关的业务价值

短片/成曲第 02 步每个开关下面也写了 **开了会怎样 / 业务价值 / 不要用来**。多开一个不等于更好听。

Lyria 3 **没有** `negative_prompt`。要排除鼓或人声，去配乐页。

---

## 6. 本产品还有、网页 Demo 故意没接的能力

入门页那张表只列 **Lyria 自己有、但网页当场做不了** 的能力：

- **Lyria RealTime**：边弹边听的流式合奏，另一条 WebSocket，不是这一页的「生成」。
- **PDF / GCS 图 / File API**：官方 Interactions 支持；本页只收浏览器 JPEG/PNG 内联（最多 10 张，合计约 100 MB）。

下面这些 **不要** 写进那张表：TTS、Live、Chirp（别的产品）；模型不输出视频（Lyria 做不到，不是没接）。

---

## 7. 出问题看哪份文档

| 现象 | 打开 |
| --- | --- |
| 不知道 Lyria 是什么 | [Lyria 概览](https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/music/overview) |
| 30 秒 / 184 秒 / 没有中文歌声 | [Lyria 3 模型卡](https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/lyria/lyria-3) · 入门页「能撑多久」 |
| 提示词、时间戳、歌词 | [提示词指南](https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/music/music-gen-prompt-guide) |
| Clip/Pro 怎么发请求 | [用 Lyria 生成音乐](https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/music/generate-music) |
| seed / negative_prompt | [Lyria 2 API](https://docs.cloud.google.com/gemini-enterprise-agent-platform/reference/models/lyria-music-generation) |
| 登录失败 | [ADC](https://docs.cloud.google.com/docs/authentication/provide-credentials-adc) |

完整索引见 [docs/official_sources.md](docs/official_sources.md)。
