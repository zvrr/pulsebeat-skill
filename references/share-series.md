# Local share-image series / 本地分享图集

The required HTML report now creates an accompanying `<report-name>-share-series/index.html` with six 1080 × 1440 editorial cards. The report's share link opens this series. The original single SVG remains as a lightweight compatibility artifact.

Cards cover: shared conclusion and coverage; verified listening / next-day health pairs; source-tag preferences; representative tracks; observed versus hypothetical context; next observations. Each image includes its source boundary. Use the chosen English/Chinese language. Never invent missing records, peer percentiles or health effects. Review the Agent-written copy at this larger type size; shorten overflowing text rather than silently shrinking it.

For a standalone series:

```sh
python3 <skill>/scripts/share_cards.py --analysis <private>/report/analysis.json --insights <private>/report/insights.json --media <private>/report/music-media.json --out <private>/report/index-share-series --lang zh-CN
```

`--media` is optional. Pictures use the already-local cover cache; missing artwork is clearly labeled. A multi-provider report currently selects the first available music portrait for the series and labels that provider; it does not merge listening totals. To feature another provider, use a separately scoped analysis.

Export PNGs with an installed Playwright Node runtime and Chrome:

```sh
NODE_PATH=<existing-playwright-node_modules> node <skill>/scripts/export_share.cjs <private>/report/index-share-series
```

If Playwright is unavailable, install it in a private tool directory with `npm install --prefix <private>/render-tools playwright` and use that directory's `node_modules` as NODE_PATH. Use the operating system's environment-variable syntax on Windows. `PULSEBEAT_BROWSER_CHANNEL` defaults to `chrome`; `PULSEBEAT_PYTHON` defaults to `python3`. Use an available browser/runtime rather than pretending export succeeded. The HTML remains reviewable if PNG rendering is unavailable.

The exporter blocks HTTP(S) requests, waits for fonts/images, rejects vertical text overflow, renders six PNGs and packages `share-images.zip`. A successful `manifest.json` has `rendered: true` and six filenames. Review all six images for clipping and legibility; share only local paths with the user. Updating the HTML resets rendered status and requires a fresh PNG export before delivery; old files must not be claimed as current. These are personal health/listening summaries: no automatic social publishing, repository upload, identity details or credentials. Artwork rights remain with their owners.

中文：用户要求分享图时，必须实际导出 PNG 图组和 ZIP，不能仅交付 HTML 或旧版单张 SVG。每张一个主题，保留关键日期、样本与事实/假设标记；确认内容没有溢出后再交付。生成本地图片不等于授权发布到小红书。
