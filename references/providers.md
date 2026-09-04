# 音乐平台接入协议

核对日期 2026-09-04。调用前读取本机对应官方 Skill；上游更新可能改变接口，发生不匹配应停止并重新核对，不猜参数。本包已附酷狗、QQ、网易原版 Skill，固定版本见 vendor/lock.json，许可证及集成边界见 THIRD_PARTY_NOTICES.md。优先按 PulseBeat 的个人授权、密钥保密与本地分析要求使用选定功能。

## 酷狗

先读取随包 `vendor/kugou/SKILL.md`（npm `@kg-ai/kugou-skill@0.0.13` 文档快照，与当前已验证 CLI 版本一致），无需另外下载 Skill 文档。运行时仍使用本机 `kugou-cli`；若未安装，可运行 `npm install -g @kg-ai/kugou-skill@0.0.13`。随后用 `kugou-cli auth status` 检查登录，必要时由用户完成 `kugou-cli auth login`。凭证留在酷狗 CLI 自己的配置目录。上游登录输出可能包含 secret；仅向用户展示二维码、等待/成功状态，不把完整登录响应或凭证写入对话、报告或仓库。

```sh
python3 <pulsebeat-skill>/scripts/kugou_collect.py --days 7 --out <private-output>/kugou.json
```

串行读取 music favorites、music recent（各最多10首）及 music stats --date-type 0 --date YYYYMMDD，时长秒，日时区+08:00。20001 超过可查询30天；30430 限流，有限重试后记缺失。今天尚未结束默认不取。独立导出优先传入 sync --kugou-file，成功日期与本地历史合并，失败不会删除此前成功数据；失败保留在 analysis.json，不填0。此脚本不上传。

## QQ 音乐

官方仓库：https://github.com/tencentmusic/qqmusic-skills （Apache-2.0）
官方配置页：https://y.qq.com/n/ryqq_v2/qqmusic_skills
接口依据：https://github.com/tencentmusic/qqmusic-skills/blob/main/qqmusic/me.md

读取随包 `vendor/qqmusic/qqmusic/SKILL.md` 和 `me.md`，无需另外寻找 Skill。个人 API Key 置于 `QQMUSIC_API_KEY` 环境变量，由用户在本机配置；只检查是否存在，**不要执行 echo 打印密钥**。不把密钥写入对话或命令字面量。包装器固定只向 https://a.y.qq.com 发送 Key，不跟随重定向。

```sh
python3 <pulsebeat-skill>/scripts/pulsebeat.py qq-report --date 2026-09-02 --out <private-output>/qq-2026-09-02.json
```

调用 POST /me/report，params={timeKey:d,startTime:目标日零点Unix秒}，comm.skill_version=0.0.3。仅针对用户要求的个人报告日期，低频串行，限流停止；未验证历史保留范围。默认按+08:00构造请求，但官方文档未明确日报时区。只有用户或提供方确认日报确为北京时间后才加 `--confirm-beijing-day`；否则报告只描述音乐事实、不计算与健康的相关系数。

| 字段 | 口径 |
|---|---|
| dayData.listenTime | 当天实际听歌秒数 |
| dayData.activeHour | 当天活跃小时0–23，不是逐次播放时间 |
| dayData.songListen[].sum | 播放次数 |
| dayData.singerListen[].sum | 听歌秒数 |
| weekData.listenTime | 日均秒数，禁止当周总数 |
| 公共 ts | 响应毫秒时间，禁止当收听时间 |

当前本地数值适配器只纳入日报。周/月数据可由官方 Skill 另作偏好解读，不能拆成伪造的逐日时长。用途限本人音乐查询体验，不做跨用户商业画像或服务端批量采集。无需调用远端 AI assistant 解释健康。

## 网易云音乐

官方仓库：https://github.com/NetEase/skills （各 Skill LICENSE.txt 为 Apache-2.0）
依赖 CLI：https://www.npmjs.com/package/@music163/ncm-cli

读取随包 `vendor/netease/netease-music-cli/SKILL.md`、`vendor/netease/netease-music-assistant/SKILL.md`，组合两者，复用本机官方 CLI 配置，再引导个人账号授权。若缺少官方开发者配置，不要求普通用户注册开发者或填写 appId/privateKey；标记该平台暂不可直接同步，使用本人已有导出或等待服务提供者提供完整官方授权入口。不要把该缺口伪装成已经接通。

```sh
ncm-cli login --background
ncm-cli login --check
ncm-cli commands
```

实际业务命令动态发现，再 `<实际命令> --help`，不能编造 user history 等命令。依官方 Skill 读取本人红心曲目（最多200，近况前20）。非播控业务所需 `--userInput` 只传“读取本人红心音乐偏好用于个人分析”，不包含健康上下文。总量超限即停止。

官方 Skill 导出原始结果留本地；由当前 Agent 按实际响应映射到下列文件，再交给 analyze --netease。未出现的字段留 null，禁止补造。歌曲 id 仅为来源追溯。

```json
{"source":"netease","evidenceType":"favorites","collectedAt":"ISO-8601采集时刻","songs":[{"id":"来源id","name":"原始歌名","artists":["原始艺人"],"tags":["来源songTag"],"addedAtMs":null,"durationMs":null}]}
```

`extMap.addTime`→addedAtMs 是收藏毫秒时间；duration→durationMs 是曲目长度，都不是个人实际收听曝光。`~/.config/ncm/ncm-history.json` 是推荐去重记录，不是收听历史。本版本网易数据参与音乐偏好解读，**不参与每日听歌时长/健康关联**。

源依据：https://github.com/NetEase/skills/blob/master/netease-music-assistant/SKILL.md

## 平台安装

Codex：将 pulsebeat 文件夹置入 ~/.codex/skills/，重新开启任务以加载。WorkBuddy：技能 → 添加技能 → 上传技能 → 导入本地技能包，启用。其他 Agent：导入同一 SKILL.md 文件夹并允许 Python 3.10+ 执行。没有 Python 或没有官方音乐认证，明确报告缺失能力，不声称已接通。

WorkBuddy 官方说明：https://www.codebuddy.cn/docs/workbuddy/From-Beginner-to-Expert-Guide/Function-Description/Skills-Market

## Spotify

见 [Spotify 官方入口与本地导入](spotify.md)。官方 App 与源码 Skill 是两种分发形式，不自动替用户安装不相关的 Spotify Ads 工具。
