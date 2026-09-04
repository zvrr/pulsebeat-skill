# Kugou CLI

酷狗音乐 API CLI 工具，用于搜索、推荐、收藏、统计、榜单等功能。

## 安装

### npm 安装（推荐）

```bash
npm install -g @kg-ai/kugou-skill
```

安装后使用 `kugou-cli` 命令。npm 安装时会自动安装 SKILL.md 到各平台的 skills 目录。

## 前置条件

使用前需要扫码登录：

```bash
kugou-cli auth login
```

登录后 token 会自动持久化存储。

## 命令

### 认证

```bash
# 扫码登录（默认保存并打开二维码图片）
kugou-cli auth login

# 只保存二维码图片，不打开
kugou-cli auth login --output file

# 输出 base64 编码的二维码图片
kugou-cli auth login --output base64

# 查看登录状态
kugou-cli auth status

# 登出
kugou-cli auth logout
```

### 音乐

```bash
# 搜索歌曲
kugou-cli music search "周杰伦"
kugou-cli music search "周杰伦" --page 1 --size 20

# 每日推荐
kugou-cli music recommend daily
kugou-cli music recommend daily --num 10

# 相似推荐（需要指定歌曲）
kugou-cli music recommend similar --song "晴天"
kugou-cli music recommend similar -s "晴天" -n 5

# 我的收藏
kugou-cli music favorites
kugou-cli music favorites --page 1 --size 20

# 最近播放
kugou-cli music recent
kugou-cli music recent --page 1 --size 20

# 听歌统计
kugou-cli music stats

# 酷狗榜单
kugou-cli music charts 6666    # 飙升榜
kugou-cli music charts 8888    # TOP500榜
kugou-cli music charts 52144  # 抖音热歌酷狗榜
kugou-cli music charts 90379  # 星耀星光榜
kugou-cli music charts 85432  # 百万收藏榜
kugou-cli music charts 74534  # 新歌榜
```

### 安装 SKILL.md

```bash
# 安装到所有平台
kugou-cli install --all

# 安装到指定平台
kugou-cli install --claude
kugou-cli install --hermes --openclaw --codex
```

### 全局

```bash
kugou-cli --version
kugou-cli --help
```

## 输出格式

所有命令输出 JSON 格式，方便其他程序调用：

```json
{
  "errcode": 0,
  "data": {
    "list": [
      {
        "song_name": "晴天",
        "mix_song_id": "32100650",
        "artist_name": "周杰伦",
        "play_link": "https://www.kugou.com/mixsong/agent_gateway/xxx.html"
      }
    ],
    "total": 480,
    "page": 1,
    "size": 20
  },
  "status": 1
}
```

## 错误处理

错误信息输出到 stderr，程序 exit code 为 1：

```bash
kugou-cli music search "xxx" 2>&1
echo $?  # 非 0 表示出错
```
