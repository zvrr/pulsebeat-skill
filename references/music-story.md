# Music stories / 音乐叙事

Use `analysis.json.musicPortraits` to write a distinct listening chapter in the user's selected language. Never substitute a chart dump for interpretation. In `insights.json`, add `musicStories` keyed by provider (`kugou`, `qqmusic`, `netease`, `spotify`):

```json
{"musicStories":{"kugou":{"title":"A concrete finding","lede":"Scope and main interpretation","chapters":[{"kind":"Observation","title":"A pattern","body":"Explain its meaning and limitations","evidence":"Dates, counts, source"}],"rhythmNote":"Explain weekday averages and outliers","scenes":[{"status":"Hypothesis — confirm with user","title":"A question","body":"Plausible context, explicitly unconfirmed","evidence":"Actual time bins"}],"trackNotes":{"track-id":"Interpret repeated days versus same-day replay"}}}}
```

Write up to three chapters and three scene interpretations; annotate representative tracks. Use actual date coverage, recurring tracks/artists, concentration, source tags, language and time bins where available. Compare frequent short sessions with rare long days. Test whether a weekday pattern is dominated by one outlier. A monthly window may use annual-recap storytelling, but must not claim a year of listening, peer percentiles, a personality diagnosis or a listening age without the needed evidence.

Kugou and QQ daily song lists are partial; counts are visible lower bounds, not full favorites rankings. Latest successful snapshot wins per day. Category appearances overlap: never convert into duration shares. Returned zero differs from a missing day/bin. Spotify covers supplied export events; NetEase favorites are preference snapshots, not listening history. Unavailable dimensions stay unavailable. No BPM, mood, activity or health effect inferred from titles. A scene must be labeled observation, user-confirmed context, or hypothesis. Song themes are not the listener's psychological state.

## Public artwork and track context

Use provider-supplied cover URLs. For public track descriptions, verify title, artist and version against an official artist/label/music catalog page, paraphrase briefly, and preserve the source URL and checked date. Do not reproduce lyrics. Artist biography alone does not establish the track's release date. Never include health data or listening metrics in external searches.

Create a private `music-catalog.json` keyed by `provider:track-id` with `title`, `artist`, `context`, `contextSource`, `contextSourceTitle`, `checkedAt`. Cache artwork:

```sh
python3 <skill>/scripts/music_media.py --analysis <private>/report/analysis.json --catalog <private>/report/music-catalog.json --out <private>/report/music-media.json
python3 <skill>/scripts/pulsebeat.py html --analysis <private>/report/analysis.json --interpretation <private>/report/interpretation.md --insights <private>/report/insights.json --media <private>/report/music-media.json --out <private>/report/index.html --lang en
```

`--catalog` is optional; `--media` embeds locally cached artwork and verified context into the offline HTML. The built-in downloader currently accepts only known Kugou image hosts, limits file size, validates raster type, and rejects redirects. Other sources use clearly labeled decorative artwork until a supported source is implemented. Inspect failure counts; never pretend a fallback illustration is the album cover. Artwork rights remain with their owners; local caching does not grant redistribution rights. Personal reports, media caches and catalogs must stay out of public Git repositories. Public demo tracks are synthetic.

中文：必须写清“为什么值得注意”，而非复述数值。用跨日回听、单日集中、曲风/语言纹理与时段变化组织故事。场景解释必须标注证据等级；年度总结的叙事风格不意味着拥有全年记录。作品背景与个人感受分开展示；封面离线嵌入，缺图使用明确标记的唱片意象，不能冒充原封面。


Integrated narrative: write one headline and summary for the shared life window, not separate music and health introductions. Add `rhythmNotes` to insights.json, keyed by `provider:health-date`, explaining each verified prior-day-music / next-day-health pair. Only use associations.paired_dates; do not invent overlaps or imply causation. The main report combines music minutes, visible tracks, next-day recovery, sleep and HRV in each date card. Full music portraits and metric trends remain expandable evidence. 中文报告同样以共同时间线组织综合解读，音乐画像与健康趋势作为可展开的支持证据。
