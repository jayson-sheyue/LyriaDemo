# 配乐实验室 · Lyria

本地教学 Demo：用浏览器试 **Vertex / Agent Platform 上的 Lyria 音乐生成**。Python FastAPI，没有 Node 前端。

这不是 Google 官方产品。资料核查日期：**2026-09-11**。

它也不是 Cloud TTS，不是 Gemini Live。Lyria 是作曲，不是念稿，也不是实时对话。

## 你能在页面上试什么

| 顶栏 | 模型 | 区域 | 做什么 |
| --- | --- | --- | --- |
| 短片 | `lyria-3-clip-preview`（Preview） | `global` | 大约 30 秒 MP3；可人声、可器乐、可看图 |
| 成曲 | `lyria-3-pro-preview`（Preview） | `global` | 最多大约 184 秒；时间戳、歌词、结构写进提示词 |
| 配乐 | `lyria-002` | `us-central1` | 大约 32.8 秒 48 kHz WAV 器乐；`negative_prompt` / `seed` |

预览请求**不会**调用 Google。点「生成」才会请求 Vertex，并可能产生费用。成曲常要等一两分钟。

Lyria **不是万能接口**。官方定位是 **从提示词（和可选图片）生成音乐**。顶栏三页对应三条官方入口，不要混用。

## 1. 准备 Cloud 项目

```bash
gcloud auth application-default login
gcloud auth application-default set-quota-project YOUR_PROJECT_ID
gcloud services enable aiplatform.googleapis.com --project YOUR_PROJECT_ID
```

复制环境变量：

```bash
cp .env.example .env
# 填写 GOOGLE_CLOUD_PROJECT
# GOOGLE_CLOUD_LOCATION=global
```

不要把 `us-central1` 当成短片/成曲的区域。Lyria 3 只支持 **global**。配乐页 `lyria-002` 会**自动改成 us-central1**。

## 2. 安装并启动

需要 Python 3.11+。

```bash
cd LyriaDemo
python3 -m venv .venv
.venv/bin/pip install -r requirements-dev.txt
.venv/bin/python -m uvicorn app:app --host 127.0.0.1 --port 8004
```

浏览器打开 http://127.0.0.1:8004

本机若已有 TTS（8001）、ASR（8002）、Live（8003），不要抢端口。Lyria 默认 **8004**。

## 3. 建议的点击顺序

1. **短片**页 → 样例「器乐吉他」→ 预览 → 生成 → 试听大约 30 秒  
2. 同一页 → 样例「日语短片」：歌声语言写进提示词，官方表**没有普通话**  
3. **成曲**页 → 样例「时间轴」：时长和卡点写在提示词里，没有滑杆  
4. **配乐**页 → 样例「排除」看 `negative_prompt`；样例「可复现」看 seed（不能和一次出几条一起用）

## 4. 输入输出格式

| 方向 | 格式 |
| --- | --- |
| 浏览器 → Lyria 3 | 文本提示词；可选 JPEG/PNG |
| Lyria 3 → 浏览器 | MP3 44.1 kHz 192 kbps；可能附带歌词/结构文本 |
| 浏览器 → Lyria 2 | 美式英语 `prompt`；可选 `negative_prompt` / `seed` |
| Lyria 2 → 浏览器 | WAV 48 kHz，大约 32.8 秒器乐 |
| 连接 | 短片/成曲：Interactions；配乐：`lyria-002:predict` |

## 5. 命令行最小示例

```bash
.venv/bin/python examples/quickstart.py
```

这会发起一次真实的 Lyria 3 Clip 调用，可能计费。

## 6. 离线测试

```bash
.venv/bin/python -m pytest -q
```

测试不访问 Google。

## 7. 常见失败

| 现象 | 先查 |
| --- | --- |
| 预览可以、生成失败 | ADC、项目 ID、`aiplatform.googleapis.com`、账单 |
| 404 模型不存在 | 短片/成曲是否误用了 `us-central1`；配乐页是否误用了 `global` |
| 被安全过滤 | 版权歌词、模仿某歌手、不当内容。换提示词 |
| 429 | 官方大约每分钟 10 次 |
| 成曲很久 | 正常。Pro 常要一两分钟，最多约 184 秒 |
| 中文歌不像中文 | 官方歌声语言没有普通话 |

## 本 Demo 明确不做

Lyria RealTime 流式合奏、PDF / GCS / File API 大文件、TTS、Live。看图：本页 JPEG/PNG 最多 10 张、内联合计约 100 MB。详见「入门指南」。

## 架构

浏览器只连你的本机后端。ADC 留在服务器，不会进前端。

```
浏览器  --HTTP-->  FastAPI (127.0.0.1:8004)  --HTTPS-->  Vertex Interactions / predict
```
