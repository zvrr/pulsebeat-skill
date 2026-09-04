# PulseBeat Skill

简体中文 · [English](README.en.md)

在 Codex、WorkBuddy 等 Agent 中分析自己的 WHOOP 健康与音乐数据，生成结论清晰、可离线打开的 HTML 报告。

PulseBeat 提供账号授权和数据读取；本 Skill 在本机保存历史、计算指标，由当前 Agent 撰写解读。使用者无需配置 Cloudflare、部署后端或创建 WHOOP 开发应用。**公开 Skill 不等于开放注册：在线服务目前需要邀请。**

## 安装

需要 Python 3.10+ 和可以执行本地 Python 的 Agent。统计和报告脚本仅使用 Python 标准库。

Codex：

```sh
git clone https://github.com/zvrr/pulsebeat-skill.git ~/.codex/skills/pulsebeat
```

如果该目录已经存在，请先检查其来源与本地修改，不要覆盖已有文件。已从本仓库安装的版本可在该目录运行 `git pull --ff-only` 更新。

WorkBuddy 或其他 Agent：克隆仓库，将包含 `SKILL.md` 的整个文件夹放入平台支持的 Skill 目录，或使用平台的本地 Skill 导入功能。各平台的加载方式以其自身说明为准。

向 Agent 提问：

> 使用 PulseBeat 同步我的健康与音乐数据，分析最近的变化和可能关联，必须生成 HTML 报告。

## 首次使用

1. 获得邀请，在 [PulseBeat](https://pulsebeat.tennisflow.top) 登录并连接自己的 WHOOP。
2. Agent 运行 `scripts/pulsebeat.py auth-start --label "我的 Agent" --open`，你在网页核对账号与确认码，批准个人只读访问；Agent 随后运行 `auth-complete`。
3. Agent 将数据同步到你指定的本地私有目录，计算统计结果，撰写有证据的解读，并使用内置模板生成 HTML。

授权入口为固定的托管服务。读取凭证默认保存在 `~/.config/pulsebeat`，可在 PulseBeat 的 `/agent.html` 页面撤销。多人共用机器时使用独立系统账号，或用 `PULSEBEAT_HOME` 和独立输出目录隔离数据。

## 报告与模板

每次分析必须交付 `index.html`，同时生成精选 `index-share.svg` 分享卡及报告清单。报告采用深色结论首屏、恢复圆环、浅色指标卡、独立刻度的趋势图，支持时间窗口切换、样本说明与指标比较。HTML 不依赖 CDN，可以离线打开、打印或保存为 PDF。

模板在 `assets/`，渲染器在 `scripts/report_html.py`；结构化解读格式见 [报告设计规范](references/report-design.md)。真实报告必须使用真实授权数据，不能用演示数据补齐缺失记录。

无需账号即可生成**完全合成的数据演示**：

```sh
python3 scripts/demo_report.py
```

在浏览器打开 `data/template-demo/en/index.html` 或 `data/template-demo/zh-CN/index.html`（按检测语言生成）。可分别运行 `python3 scripts/demo_report.py --lang en` 和 `--lang zh-CN` 预览两种语言。所有演示数值来自确定性公式，不代表任何人的身体状态。演示输出默认被 Git 忽略。

## 数据来源

| 平台 | 当前能力 | 授权或限制 |
| --- | --- | --- |
| WHOOP | 通过 PulseBeat 获取周期、恢复、睡眠和运动记录 | 邀请加入服务，个人网页授权 |
| 酷狗音乐 | 本机 CLI 同步及已有 PulseBeat 数据；累计本地日历史 | 本机已授权的酷狗 Skill/CLI；接口窗口与限流可能限制覆盖 |
| QQ 音乐 | 官方个人日报适配 | 使用官方 Skill 的个人 API Key；日期时区须确认 |
| 网易云音乐 | 内置官方 CLI/助手/安装 Skill；已有授权的收藏与偏好分析 | 开发配置尚缺时标记不可用或导入，不让普通用户创建应用 |
| Spotify | 官方应用使用指引、官方扩展听歌历史本地导入 | 未找到官方个人听歌源码 Skill；导入按结束日统计，暂不自动计算健康关联系数 |

平台接入细节见 [providers.md](references/providers.md)。可组合 [QQ 音乐官方 Skills](https://github.com/tencentmusic/qqmusic-skills) 和 [网易云音乐官方 Skills](https://github.com/NetEase/skills)。两家的官方 Skill 源码已随包放在 `vendor/`，无需再寻找或下载，固定提交与文件校验值见 `vendor/lock.json`，原始许可证见 [第三方声明](THIRD_PARTY_NOTICES.md)。平台账号授权仍由本人完成，凭证不随包分发。

## 中英文环境

默认跟随电脑的界面语言：macOS 读取 AppleLanguages，Windows 读取 UI Culture，Linux 读取 locale。中文映射为简体中文，其余语言回退英文；检测失败也回退英文。可以使用 `PULSEBEAT_LANG=zh-CN` / `en`，或在任意命令末尾加 `--lang zh-CN` / `--lang en` 手动指定，命令参数优先。

```sh
python3 scripts/pulsebeat.py locale
python3 scripts/demo_report.py --lang en
python3 scripts/demo_report.py --lang zh-CN
```

Agent 回复、分析解读、HTML 界面与分享卡使用同一语言；歌名和艺人名保留原文。切换报告语言时 Agent 需重新生成对应语言的解读。静态 Skill 列表名称使用双语，宿主不支持动态元信息时仍可识别；上游原版 Skill 文件保留原文。界面语言不改变统计时区。

## Spotify 本地导入

使用 Spotify 账号隐私页面导出的扩展听歌历史，无需开发者应用。详见 [Spotify 接入说明](references/spotify.md)。

```sh
python3 scripts/pulsebeat.py spotify-import --files ~/Downloads/Streaming_History_Audio_0.json --timezone Asia/Shanghai --out ~/PulseBeat-private/spotify.json
```

时区须依据本人实际历史确认，不能从系统语言猜测。同步与分析时加入 `--spotify ~/PulseBeat-private/spotify.json`；脚本不会上传这些文件。

## 本地工作流

以下命令在仓库目录执行，输出放在仓库外的个人目录：

```sh
python3 scripts/pulsebeat.py sync --directory ~/PulseBeat-private/library
python3 scripts/pulsebeat.py analyze --input ~/PulseBeat-private/library/current.json --out ~/PulseBeat-private/report
```

Agent 阅读 `analysis.json` 后撰写 `interpretation.md` 和 `insights.json`，再生成报告：

```sh
python3 scripts/pulsebeat.py html --analysis ~/PulseBeat-private/report/analysis.json --interpretation ~/PulseBeat-private/report/interpretation.md --insights ~/PulseBeat-private/report/insights.json --out ~/PulseBeat-private/report/index.html
```

## 数据与分析边界

- 原始记录、历史快照和报告保存在本机；本 Skill 不直接调用 LLM API。Agent 平台本身可能使用云端模型，本地计算不表示模型离线。优先仅向模型提供必要的统计汇总。
- 不提交凭证、个人原始数据或真实报告到 GitHub。分享卡仍包含个人健康摘要，须由用户决定是否分享，不自动上传。
- 缺失数据不填零，收藏不冒充听歌时长；样本与时区不足时不输出关联系数。探索性关联不证明因果，不用于诊断或治疗建议。
- 仓库只包含客户端 Skill、模板、合成演示和测试；后端服务及运营凭证不在此仓库中。

## 验证

```sh
python3 -m unittest discover -s tests -p 'test_*.py'
```

完整使用协议见 [SKILL.md](SKILL.md)，计算口径见 [analysis.md](references/analysis.md)。
