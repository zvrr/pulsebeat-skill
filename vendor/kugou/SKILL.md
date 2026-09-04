---
name: kugou-skill
description: |
  酷狗，酷狗音乐，酷狗skill，酷狗音乐skill，酷狗音乐助手
  提供歌曲搜索、每日推荐、相似推荐、收藏管理、听歌统计、酷狗榜单等功能。
  
  **触发场景**（满足任一即使用本技能）：
  - 用户要求推荐歌曲、听歌建议
  - 用户要求搜索歌曲、查找歌手作品
  - 用户要求查看音乐榜单（飙升榜、TOP500、抖音热歌等）
  - 用户要求查看收藏、最近播放、听歌统计
  - 用户提到"酷狗"、"kugou"、"每日推荐"、"相似歌曲"
  
  **与其他音乐技能的区别**：酷狗音乐以推荐算法见长，榜单数据实时更新，适合获取热门歌曲和个性化推荐。
  
  安装方式：npm install -g @kg-ai/kugou-skill
---

# kugou-skill

## AI 使用工作流（优先阅读）

使用本工具时的标准流程：

```
1. 检查安装 → npm install -g @kg-ai/kugou-skill
2. 检查登录 → kugou-cli auth status
3. 未登录 → 引导用户执行 kugou-cli auth login，等待 status: success
4. 执行用户请求的音乐命令
5. 解析 JSON 输出，格式化展示给用户
```

### 关键注意事项

- **登录是阻塞操作**：`kugou-cli auth login` 会持续轮询直到用户扫码确认。必须等到输出 `"status":"success"` 才能继续后续音乐操作。默认模式会自动打开系统图片查看器供扫码。`file` 模式只保存文件不打开。`base64` 模式适合 Web 前端场景。
- **音乐命令依赖登录**：除了 `auth`、`install`、`version`、`--help` 以外，所有 `music` 子命令都需要先登录。如果收到 `"not logged in"` 错误，引导用户执行 `kugou-cli auth login`。
- **输出均为 JSON**：所有命令输出原始 JSON 到 stdout，错误输出到 stderr。解析 `errcode` 字段判断成功与否（`0` 为成功）。
- **链接展示**：输出中的 `play_link` 字段，展示给用户时转为可点击格式：
  - Markdown: `[歌曲名](https://www.kugou.com/...)`
  - HTML: `<a href="https://www.kugou.com/...">歌曲名</a>`

---

## 基础信息

- **npm 包**: @kg-ai/kugou-skill
- **二进制命令**: kugou-cli
- **API 域名**: https://agentgateway.kugou.com（固定，无需配置）
- **安装方式**: `npm install -g @kg-ai/kugou-skill`

### 登录

使用前需要扫码登录。登录采用轮询机制，需等待用户扫码确认。

```bash
kugou-cli auth login                    # 默认，保存二维码图片并打开图片查看器
kugou-cli auth login --output file    # 只保存二维码图片，不打开
kugou-cli auth login --output base64  # 输出 base64 图片数据（含 data:image/png;base64, 前缀）
```

**登录轮询流程**（`kugou-cli auth login` 内部自动处理）：

```
1. 输出 {"qrcode": "...", "qrcode_img_path": "...", "status": "waiting"}
2. 每 2 秒轮询一次，持续等待用户扫码
3. 用户扫码后输出 {"status": "scanned", ...}  → 继续等待确认
4. 用户确认后输出 {"status": "success", "nickname": "...", ...} → 登录完成
5. 若超时/二维码过期输出 {"status": "failed", "message": "..."}
```

> **输出模式选择建议**：默认模式会自动打开图片查看器弹出二维码，用户直接扫码即可，适合桌面端 Agent 使用。`file` 模式只保存到临时文件，需手动打开。`base64` 模式适合需要内嵌二维码图片展示的场景。

---

## 命令列表

> 🔐 = 需要先登录

### 认证命令 (auth)

| 命令 | 说明 | 需要登录 |
|------|------|---------|
| `kugou-cli auth login` | 扫码登录（轮询等待确认） | 否 |
| `kugou-cli auth status` | 查看登录状态 | 否 |
| `kugou-cli auth logout` | 登出 | 否 |

### 音乐命令 (music)

| 命令 | 说明 | 需要登录 |
|------|------|---------|
| `kugou-cli music search <keyword>` | 搜索歌曲 | 🔐 |
| `kugou-cli music recommend daily` | 每日推荐 | 🔐 |
| `kugou-cli music recommend similar -s <song>` | 相似歌曲推荐 | 🔐 |
| `kugou-cli music favorites` | 我的收藏 | 🔐 |
| `kugou-cli music recent` | 最近播放 | 🔐 |
| `kugou-cli music stats` | 听歌统计 | 🔐 |
| `kugou-cli music charts <rank_id>` | 榜单 | 🔐 |

### 安装命令 (install)

| 命令 | 说明 | 需要登录 |
|------|------|---------|
| `kugou-cli install` | 显示平台选择提示 | 否 |
| `kugou-cli install --all` | 安装 SKILL.md 到所有平台 | 否 |
| `kugou-cli install --claude` | 安装到 Claude skills 目录 | 否 |
| `kugou-cli install --hermes` | 安装到 Hermes skills 目录 | 否 |
| `kugou-cli install --openclaw` | 安装到 Openclaw skills 目录 | 否 |
| `kugou-cli install --codex` | 安装到 Codex skills 目录 | 否 |

### 通用命令

| 命令 | 说明 |
|------|------|
| `kugou-cli --version` / `kugou-cli version` | 输出版本号 |
| `kugou-cli --help` | 显示帮助信息 |
| `kugou-cli <子命令> --help` | 显示子命令帮助（如 `kugou-cli music search --help`）|

---

## 详细用法

### 1. 扫码登录

```bash
kugou-cli auth login
kugou-cli auth login --output file    # 只保存二维码图片，不打开
kugou-cli auth login --output base64  # 输出 base64 编码的图片数据（含 data:image/png;base64, 前缀）
```

**参数**:
- `-o, --output`: 输出模式
  - (默认): 保存二维码图片到临时目录并打开图片查看器，供扫码
  - `file`: 只保存二维码图片到临时目录，不打开
  - `base64`: 输出 base64 编码的图片数据（含 `data:image/png;base64,` 前缀）

**输出示例** (默认模式 - 保存并打开):
```json
{"qrcode": "xxx", "qrcode_img_path": "C:\\Users\\xxx\\AppData\\Local\\Temp\\kugou-qrcode.png", "status": "waiting"}
```

**输出示例** (file 模式):
```json
{"qrcode": "xxx", "qrcode_img_path": "/tmp/kugou-qrcode.png", "status": "waiting"}
```

**输出示例** (base64 模式):
```json
{"qrcode": "xxx", "qrcode_base64": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAA...", "status": "waiting"}
```

> **base64 二维码展示指导**：`qrcode_base64` 已包含 `data:image/png;base64,` 前缀，可直接作为 `<img>` 标签的 `src` 属性，或通过 Markdown `![QR](data:image/png;base64,...)` 展示。

**轮询过程中的状态输出**:
- `{"status": "waiting", ...}` — 等待扫码
- `{"status": "scanned", "nickname": "...", ...}` — 已扫码，等待用户在手机上确认
- `{"status": "success", "nickname": "...", "secret": "..."}` — 登录成功，token 已持久化
- `{"status": "failed", "message": "QR code expired or login failed"}` — 登录失败（二维码过期），需重新执行

---

### 2. 查看登录状态

```bash
kugou-cli auth status
```

**输出示例**:
```json
{"logged_in": true, "nickname": "沙墨", "login_time": "2024-01-01 12:00:00"}
```

---

### 3. 搜索歌曲 🔐

```bash
kugou-cli music search "周杰伦"
kugou-cli music search "周杰伦" --page 1 --size 20
```

**参数**:
- `<keyword>`: 搜索关键词（必填）
- `--page`: 页码，默认 1
- `--size`: 每页数量，默认 20

**输出示例**:
```json
{
  "errcode": 0,
  "data": {
    "list": [
      {
        "song_name": "晴天",
        "mix_song_id": "32100650",
        "artist_name": "周杰伦",
        "play_link": "https://www.kugou.com/mixsong/agent_gateway/j410q78a01f.html"
      }
    ],
    "total": 480,
    "page": 1,
    "size": 20
  },
  "status": 1
}
```

---

### 4. 每日推荐 🔐

```bash
kugou-cli music recommend daily
kugou-cli music recommend daily --num 10
kugou-cli music recommend daily --text "轻快的中文歌" --num 5
```

**参数**:
- `--num`: 推荐数量，默认 10
- `--text`: 描述文本（可选），用于个性化推荐偏好。例如 `"轻快的"` / `"安静的"` / `"粤语歌"` 等，来影响推荐结果。

---

### 5. 相似推荐 🔐

```bash
kugou-cli music recommend similar -s "晴天"
kugou-cli music recommend similar --song "晴天" -n 5
kugou-cli music recommend similar --song "晴天" --text "风格相似的" -n 5
```

**参数**:
- `-s, --song`: 歌曲名称（必填）
- `-n, --num`: 推荐数量，默认 10
- `-t, --text`: 描述文本（可选），用于进一步细化相似方向。

---

### 6. 我的收藏 🔐

```bash
kugou-cli music favorites
```

> 注意：固定返回最近 10 首收藏，查看更多请前往酷狗App

**输出示例**:
```json
{
  "errcode": 0,
  "data": {
    "list": [
      {
        "song_name": "晴天",
        "mix_song_id": "32100650",
        "artist_name": "周杰伦",
        "play_link": "https://www.kugou.com/mixsong/agent_gateway/j410q78a01f.html"
      }
    ],
    "total": 50,
    "msg": "当前仅显示最近的10首收藏，查看更多内容，请前往酷狗App"
  },
  "status": 1
}
```

---

### 7. 最近播放 🔐

```bash
kugou-cli music recent
```

> 注意：固定返回最近 10 首播放记录，查看更多请前往酷狗App

**输出示例**:
```json
{
  "errcode": 0,
  "data": {
    "list": [
      {
        "song_name": "七里香",
        "mix_song_id": "32100651",
        "artist_name": "周杰伦",
        "play_link": "https://www.kugou.com/mixsong/agent_gateway/j410q78a01f.html"
      }
    ],
    "total": 100,
    "msg": "当前仅显示最近的10首最近播放，查看更多内容，请前往酷狗App"
  },
  "status": 1
}
```

---

### 8. 听歌统计 🔐

```bash
kugou-cli music stats                    # 默认查当月
kugou-cli music stats --date-type 1 --date 20260501  # 指定周查询
```

**参数**:
- `--date-type`: 日期类型，0=日、1=周、2=月，默认 2（月）
- `--date`: 查询日期，YYYYMMDD 格式，如 "20260501"（不填默认当月第一天）
  - 日类型：每天日期，如 "20260501"
  - 周类型：必须是周一日期，如 "20260505"（周一）
  - 月类型：必须是月份第一天，如 "20260501"（5月1日）

**输出示例**:
```json
{
  "errcode": 0,
  "data": {
    "server_time": 1779977674,
    "listen_duration": 80776,
    "accumulate_listen_days": 30,
    "continue_listen_days": 7,
    "listen_total": 342,
    "last_listen_total": 387,
    "top_clocks": [
      "今日08:00-10:00听歌30分钟",
      "今日14:00-16:00听歌25分钟",
      "今日20:00-22:00听歌20分钟"
    ],
    "rank_song": [
      {
        "song_info": {"song_name": "晴天", "mix_song_id": "8888", "artist_name": "周杰伦", "play_link": "https://www.kugou.com/..."},
        "count": 50
      }
    ],
    "rank_singer": [
      {"singer_id": 123, "name": "周杰伦", "avatar": "https://xxx.jpg", "total": 120}
    ],
    "rank_style": [
      {"style": "流行", "total": 200, "count": 80}
    ],
    "rank_language": [
      {"language": "华语", "total": 400, "count": 150}
    ]
  },
  "status": 1
}
```

**关键字段**:
- `listen_duration`: 今日/周/月听歌时长（秒）
- `top_clocks`: 听歌时长最长的 Top3 时段描述（日类型格式如"今日08:00-10:00听歌30分钟"，周/月类型格式如"近7天平均08:00-10:00听歌119分钟"）
- `accumulate_listen_days`: 累计听歌天数
- `continue_listen_days`: 连续听歌天数
- `listen_total`: 累计听歌次数
- `last_listen_total`: 昨日/上周/上月听歌次数
- `rank_song`: 播放最多的歌曲排行（`count` 为播放次数）
- `rank_singer`: 播放最多的歌手排行
- `rank_style`: 曲风分布统计
- `rank_language`: 语言分布统计

---

### 9. 榜单 🔐

```bash
kugou-cli music charts 6666
kugou-cli music charts 52144 --page 1 --size 20
```

**可用榜单 ID**:

| rank_id | 榜单名称 |
|---------|----------|
| 8888 | TOP500榜 |
| 90379 | 星耀星光榜 |
| 6666 | 飙升榜 |
| 85432 | 百万收藏榜 |
| 74534 | 新歌榜 |
| 52144 | 抖音热歌酷狗榜 |

**参数**:
- `<rank_id>`: 榜单 ID（必填）
- `--page`: 页码，默认 1
- `--size`: 每页数量，默认 20

---

### 10. 安装 SKILL.md

```bash
kugou-cli install                    # 显示平台选择提示
kugou-cli install --all              # 安装到所有平台
kugou-cli install --claude           # 仅安装到 Claude
kugou-cli install --hermes --claude # 安装到 Hermes 和 Claude
```

**参数**:
- `--claude`: 安装到 `~/.claude/skills/kugou-skill/`
- `--hermes`: 安装到 `~/.hermes/skills/kugou-skill/`
- `--openclaw`: 安装到 `~/.openclaw/skills/kugou-skill/`
- `--codex`: 安装到 `~/.codex/skills/kugou-skill/`
- `--all`: 安装到以上所有平台

**行为说明**:
- 无参数时输出"平台选择提示"，列出可用平台选项，不会进行任何安装操作
- 只会在目标平台的 skills 父目录存在时才安装（不自动创建父目录）
- npm 安装时会自动调用 install.js 安装 SKILL.md
- `kugou-cli install` 命令用于手动重新安装或更新 SKILL.md

---

## 全局参数

所有命令支持以下隐藏参数：

- `--proxy`: HTTP 代理地址，用于网络受限环境
  ```bash
  kugou-cli music search "周杰伦" --proxy "http://127.0.0.1:7890"
  ```

## 输出格式与展示规范

### 通用响应结构

所有 API 命令输出标准 JSON 结构：

```json
{
  "errcode": 0,
  "errmsg": "",
  "data": { ... },
  "status": 1
}
```

**响应状态**:
- `errcode: 0` 表示成功
- `data` 包含实际业务数据
- `status: 1` 表示接口调用成功

### 展示规范

向用户展示结果时：

1. **歌曲列表**：整理为表格或列表，包含歌曲名、歌手、播放链接
2. **播放链接**：将 `play_link` 转为可点击的超链接
   - Markdown: `[歌曲名 - 歌手名](https://www.kugou.com/...)`
3. **统计数据**：提取关键字段并以结构化方式呈现（如"累计听歌 342 首，时长 22.4 小时"）
4. **二维码**（base64 输出）：`qrcode_base64` 已含 `data:image/png;base64,` 前缀，可直接作为 `<img>` 的 `src`

---

## 错误处理

错误信息输出到 stderr，程序 exit code 为 1：

```bash
kugou-cli music search "xxx" 2>&1
echo $?  # 非 0 表示出错
```

**常见错误及处理**:

| 错误信息 | 原因 | 处理方式 |
|---------|------|---------|
| `not logged in` / `auth file not found` | 未登录 | 引导用户执行 `kugou-cli auth login` |
| `HTTP error: 400` | 请求参数有误 | 检查命令参数是否正确 |
| `HTTP error: 500` | 服务端错误 | 稍后重试，或告知用户 |
| `API error: ...` | 业务错误（errcode 非 0） | 根据 errmsg 提示用户 |
| `network error: ...` | 网络连接问题 | 检查网络，可尝试 `--proxy` |
| `failed to get device info` | 设备信息获取失败 | 运行时环境异常，检查权限 |

---

## 使用示例

### 完整使用流程

```bash
# 1. 登录
kugou-cli auth login

# 2. 查看登录状态
kugou-cli auth status

# 3. 搜索歌曲
kugou-cli music search "周杰伦"

# 4. 获取每日推荐
kugou-cli music recommend daily --num 5

# 5. 查看我的收藏
kugou-cli music favorites

# 6. 查看最近播放
kugou-cli music recent

# 7. 查看听歌统计
kugou-cli music stats

# 8. 查看抖音热歌榜
kugou-cli music charts 52144
```

### 在脚本中使用

```bash
#!/bin/bash

# 搜索并提取歌曲名
result=$(kugou-cli music search "周杰伦" --size 1)
echo "$result" | jq -r '.data.list[0].song_name'

# 获取榜单第一首
kugou-cli music charts 6666 --size 1 | jq -r '.data.list[0].song_name'
```
