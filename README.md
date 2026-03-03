# 🎬 Ultimate AI Image & Video Generator

**CyberBara API v1 的代理友好型多媒体生成 Skill。**  
面向 Codex/Claude Code 等终端代理场景，支持图片与视频生成、积分预估确认闸门、自动落盘与自动打开。

[🚀 Quick Start](#-quick-start) | [✨ Key Features](#-key-features) | [🏗️ Architecture](#️-architecture) | [📖 Reference](#-reference)

---

## ✨ Key Features

- **🤖 Agent-Native CLI**：统一命令接口，稳定 JSON 输出，便于 Agent 编排与链式调用。
- **🛡️ Credit Guardrail**：正式发起 image/video 任务前，先 `quote` 积分并要求确认。
- **📊 Batch Credit Summary**：批量请求自动逐条估算并汇总总积分。
- **💾 Auto Save & Open**：任务成功后自动保存输出文件并尝试直接打开。
- **🔐 API Key Auto-Persist**：首次提供 API key 后自动缓存，后续无需重复输入。
- **🌐 Fixed Base URL**：内置 `https://cyberbara.com`，无需用户手动传 base URL。

---

## 🏗️ Architecture

采用分层 Python 架构，保持“CLI 薄、策略清晰、网关可复用”：

- `scripts/cyberbara_api.py`：薄入口（bootstrap + 调用 CLI）
- `src/cyberbara_cli/cli.py`：命令解析与路由
- `src/cyberbara_cli/usecases/`：流程编排（提交、轮询、落盘）
- `src/cyberbara_cli/policies/`：策略规则（积分预估与确认）
- `src/cyberbara_cli/gateways/`：CyberBara API 访问封装
- `src/cyberbara_cli/config.py`：API key 解析与本地缓存
- `src/cyberbara_cli/constants.py`：常量配置

---

## 🚀 Quick Start

### 1. API Key（首次）

如果缺少 key，CLI 会立即提示你前往：

```text
https://cyberbara.com/settings/apikeys
```

API key 解析顺序：

1. `--api-key`
2. `CYBERBARA_API_KEY`
3. `~/.config/cyberbara/api_key`
4. 交互输入（终端模式）

缓存位置：

```text
~/.config/cyberbara/api_key
```

### 2. 基础可用性检查

```bash
python3 scripts/cyberbara_api.py models --media-type image
python3 scripts/cyberbara_api.py balance
```

### 3. 生图（默认：quote -> confirm -> submit -> wait -> save/open）

```bash
python3 scripts/cyberbara_api.py generate-image --json '{
  "model":"nano-banana-pro",
  "prompt":"A cinematic portrait under neon rain",
  "scene":"text-to-image",
  "options":{"resolution":"1k"}
}'
```

### 4. 生视频（默认：quote -> confirm -> submit -> wait -> save/open）

```bash
python3 scripts/cyberbara_api.py generate-video --json '{
  "model":"sora-2",
  "prompt":"A calm drone shot over snowy mountains at sunrise",
  "scene":"text-to-video",
  "options":{"duration":"10","resolution":"standard"}
}'
```

### 5. 仅提交不等待

```bash
python3 scripts/cyberbara_api.py generate-video --json '{...}' --yes --async
```

### 6. 自定义输出行为

```bash
# 保存但不自动打开
python3 scripts/cyberbara_api.py generate-image --file ./image-requests.json --yes --no-open

# 自定义保存目录
python3 scripts/cyberbara_api.py wait --task-id <TASK_ID> --output-dir ./downloads
```

---

## 🧭 Command Matrix

- `models`：列出可用模型（可按 `image|video` 过滤）
- `upload-images`：上传本地参考图并返回 URL
- `quote`：估算积分
- `generate-image`：图片生成（内置积分确认闸门）
- `generate-video`：视频生成（内置积分确认闸门）
- `task`：查询任务快照
- `wait`：轮询到终态并保存/打开输出
- `balance`：余额查询
- `usage`：积分消耗记录
- `raw`：自定义调用任意 API path

---

## 📖 Reference

- API 文档（本地引用）：`references/cyberbara-api-reference.mdx`
- Skill 行为规范：`SKILL.md`

---

## 🔧 Compatibility

- Codex CLI / Claude Code / 其他可执行本地脚本的代理环境
- Python 3.10+

