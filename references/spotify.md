# Spotify / 官方入口与本地数据

Verified / 核对：2026-09-04.

No official personal-listening SKILL.md distribution was identified. Spotify's official ChatGPT app supports personal music discovery; its available tools and account connection depend on the host platform. The official spotify/ads-agentic-tools repository manages advertising, not personal listening history. Do not relabel community repositories as official or install the Ads plugin for this task.

未找到官方个人听歌源码 Skill。已找到官方 ChatGPT 音乐应用；宿主支持时使用它的个人授权与实际可用工具，不承诺它可以导出完整播放历史，也不将广告投放 Skill 用于个人音乐分析。

- Official app / 官方应用：https://newsroom.spotify.com/2025-10-06/spotify-personalized-prompts-chatgpt/
- Official data export / 官方数据说明：https://support.spotify.com/us/article/understanding-your-data/
- Ads plugin (different purpose) / 广告工具：https://github.com/spotify/ads-agentic-tools

## Local history / 本地历史

Ask the user to download their **Extended Streaming History** from Spotify's account privacy controls and select the extracted music JSON files. Read the included Read Me to confirm the schema. PulseBeat supports ts (UTC stream end), ms_played (actual played milliseconds), spotify_track_uri and master_metadata track/artist fields. It does not collect account credentials, audio, IP addresses, user agents or usernames into the normalized output.

由用户在 Spotify 账号隐私页面下载扩展听歌历史，解压并指定音乐 JSON。解析 ts、ms_played 等真实字段；不会把 IP、用户名和设备信息带入分析文件。原始文件仍由用户保存在其私有目录。

```sh
python3 <skill>/scripts/pulsebeat.py spotify-import --files <Streaming_History_Audio_0.json> <Streaming_History_Audio_1.json> --timezone Asia/Shanghai --out <private-output>/spotify.json
python3 <skill>/scripts/pulsebeat.py sync --directory <private-output>/library --spotify <private-output>/spotify.json
python3 <skill>/scripts/pulsebeat.py analyze --input <private-output>/library/current.json --spotify <private-output>/spotify.json --out <private-output>/report
```

Use the person's actual historical IANA timezone, confirmed separately from interface language. Travel or timezone changes require separate interpretation; do not infer timezone from country, language or the current PC clock. Import all relevant files together. Repeated identical events across files are deduplicated; the latest complete normalized import replaces the previous Spotify snapshot, with earlier versions retained in snapshots.

时区必须单独确认；语言不决定时区。每次合并导入该账号所需的全部文件，相同事件去重。最新完整导入替代当前快照，旧快照仍在本地。

Daily totals are attributed to **stream end date**. They are not evidence of a continuous session or complete daily coverage, so Spotify currently appears in music coverage, trends and descriptive preferences but is excluded from automatic health correlations. Missing days remain missing; non-music/unknown media are excluded and counted. This is a PulseBeat local adapter for official user exports, not an official Spotify Skill or automatic Spotify cloud synchronization.

每日按播放结束日统计，不据此推断连续播放、跨午夜的准确分配或完整日覆盖。当前参与听歌趋势与偏好描述，不自动参与健康关联系数；缺失日不补零。这是 PulseBeat 的本地适配器，并非 Spotify 官方 Skill 或已上线的自动云同步。
