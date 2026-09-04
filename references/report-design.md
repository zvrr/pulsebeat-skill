# 必须交付的 HTML 报告模板

模板资源：assets/report.html、report.css、report.js；渲染器 scripts/report_html.py。不需要构建工具、云服务或外部字体。所有图表是本地生成的 SVG；仅有经过 CSP 哈希约束的打印与图表窗口切换脚本。

## 视觉与信息层次

参考 WHOOP 的深色数据概览、恢复进度与强数字对比，以及 Apple Health 的留白、分项色彩和易读趋势卡片。保持 PulseBeat 自有标识，不使用第三方商标、截图或暗示官方合作。

1. 首屏必须是有依据的分析结论，不是“我的数据报告”等空泛标题；摘要约80–140字，交代来源与样本边界。
2. 三张 insight 卡分别呈现最重要的事实/探索性问题/数据限制，每张含明确证据。
3. 指标展示最近值、有效观测均值和差值。该均值含最近观测，不冒充长期个人基线。默认不使用红绿表示“医学好坏”。
4. 日趋势按实际日期绘图，不跨缺失日连线，不将不同单位放在同一纵轴。图表范围7/30/全部可切换；该控件只过滤图表，不改变AI结论或上方均值。
5. 关联区显示实际配对数、最低展示门槛、平台和统计边界。各平台分开，不能叠加伪造音乐总时长。
6. 两项具体下一步观察；完整解读与方法细节默认折叠。
7. 自动产生精选SVG分享卡与打印/PDF排版；不自动发送、发布或上传。分享卡只保留标题、日期、选定健康数值和配对提示，不嵌入原始记录、身份、文件路径或来源哈希。它仍含个人健康摘要，用户决定是否分享。

## Agent 应提供的结构化结论

在 interpretation.md 之外生成 insights.json（推荐；缺省时仅从实际Markdown抽取，不伪造结论）：

    {
      "headline": "一句有证据的主结论，建议不超过26字",
      "summary": "简洁解释，明确日期或有效样本，避免因果夸大",
      "findings": [
        {"title": "发现标题", "detail": "具体解释", "evidence": "日期 / 指标 / n"},
        {"title": "另一个发现", "detail": "具体解释", "evidence": "来源"},
        {"title": "证据边界", "detail": "具体解释", "evidence": "缺失或样本量"}
      ],
      "next_steps": [
        {"title": "下一步观察", "detail": "用户能执行的记录或核对"},
        {"title": "继续验证什么", "detail": "不要提供未经依据的治疗或训练处方"}
      ]
    }

所有数字必须与 analysis.json 一致；当前近期图表来自 healthDaily / musicDaily。旧版汇总没有这些字段时，先用本地原始文件重新运行 analyze，不要补造时间序列。图表比较不能代替AI解释。

    python3 <skill>/scripts/pulsebeat.py html --analysis <analysis.json> --interpretation <interpretation.md> --insights <insights.json> --out <report-directory>/index.html

缺少或空白的 interpretation.md 会报错；HTML 是任务完成的必要产物。输出 index.html、index-share.svg、index.manifest.json。清晰命名归档，保留 JSON/Markdown 供复查，但首先交付 HTML。在桌面和窄屏检查结论、图表、缺失提示与按钮。保持离线可用，不引入 CDN 或分析脚本。

设计参考：
https://www.whoop.com/us/en/
https://www.apple.com/health/

## Language / 语言

先运行 locale，insights.json 增加 language（en 或 zh-CN），interpretation.md 与结构化解读使用同一语言。analyze 和 html 传入同一个 --lang。渲染器只翻译界面文案，不翻译用户的 AI 解读；切换语言须由 Agent 重写解读。模板为同一套版式，HTML lang 属性及分享卡同步变化。上游原始字段、歌名和艺人名不翻译。


## Rich listening interpretation / 丰富听歌解读

When musicPortraits are available, read [Music stories](music-story.md) and write musicStories in insights.json before generating the required HTML. Include meaningful preference and scene interpretations, source-bounded comparisons, and verified public track context/artwork where available. 使用实际覆盖区间，写出回听、口味与场景线索，不以原始数据或泛泛的音乐人格标签替代解读。
