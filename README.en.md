# PulseBeat Skill

[简体中文](README.md) · English

Analyze your WHOOP health and music data in Codex, WorkBuddy or another local-capable Agent. Keep records locally and generate an offline HTML report that leads with findings, visual comparisons and evidence.

PulseBeat hosts WHOOP authorization and data access. Users do **not** deploy Cloudflare or register a developer application. The hosted service currently requires an invitation. Public availability of this Skill does not imply open registration.

## Install

Requires Python 3.10+ and an Agent that can execute local Python. Core scripts use the standard library only. Spotify imports also need an installed IANA timezone database; the command reports if one is unavailable.

### Install with npx (recommended)

Install Node.js, which includes npm/npx. The command is `npx skills add` — **skills is plural**.

```sh
npx skills add zvrr/pulsebeat-skill --skill pulsebeat
```

Follow the prompts to choose an Agent and installation scope. To install globally for Codex:

```sh
npx skills add zvrr/pulsebeat-skill --skill pulsebeat --agent codex --global
```

`--skill pulsebeat` selects the main Skill, including its bundled music Skills and report templates. Without `--global`, installation is scoped to the current project. Start a new Agent task after installation. For WorkBuddy, select it if offered by the installer; otherwise use the local import workflow below.

Command reference: [official Skills CLI documentation](https://github.com/vercel-labs/skills#install-a-skill).

### Manual installation

```sh
git clone https://github.com/zvrr/pulsebeat-skill.git ~/.codex/skills/pulsebeat
```

Check an existing directory before installing; do not overwrite local modifications. For an existing clone of this repository, update with git pull --ff-only. In WorkBuddy or other platforms, import the entire folder containing SKILL.md using the host's supported local Skill workflow.

Ask the Agent:

> Use PulseBeat to sync my health and music records, explain the strongest supported patterns, and generate an HTML report.

## Four music providers

| Provider | Included | Personal access |
| --- | --- | --- |
| Kugou Music | Bundled Skill document, collector and local history archive | Authorized kugou-cli or data already in PulseBeat |
| QQ Music | Official source Skill plus daily-report adapter | Personal QQMUSIC_API_KEY configured locally |
| NetEase Cloud Music | Official CLI, assistant and setup Skills; favorite import | Reuse an existing authorized CLI; unavailable developer setup is not delegated to ordinary users |
| Spotify | Official app guidance plus local Extended Streaming History importer | Use the official host app where available, or import your account's export |

Kugou Skill documents from npm @kg-ai/kugou-skill@0.0.13 are included at vendor/kugou/SKILL.md, alongside QQ and NetEase snapshots. Kugou declares MIT in its original package metadata; QQ and NetEase retain their Apache-2.0 license files. Versions, commits and checksums are pinned in vendor/lock.json. The Kugou CLI runtime and personal login remain separate requirements. See [third-party notices](THIRD_PARTY_NOTICES.md). No official personal-listening Spotify source Skill was identified; its official Ads plugin has a different purpose and is not bundled. See [Spotify integration](references/spotify.md). Bundling instructions does not replace personal account authorization.

## Language

The default follows the computer's UI language: AppleLanguages on macOS, UI Culture on Windows, locale on Linux. Chinese maps to Simplified Chinese; English and unsupported languages use English. Detection failures fall back to English. Explicit --lang overrides PULSEBEAT_LANG, which overrides system detection.

```sh
python3 scripts/pulsebeat.py locale
python3 scripts/demo_report.py --lang en
python3 scripts/demo_report.py --lang zh-CN
```

The Agent's explanation, interpretation, HTML labels and share card use the same language. Song and artist names remain unchanged. When changing language, the Agent rewrites the interpretation; the renderer does not translate user prose. Static Skill metadata is bilingual. Upstream reference files retain their original language. UI language never determines the historical data timezone.

## First run and local analysis

Join [PulseBeat](https://pulsebeat.tennisflow.top) by invitation and connect your WHOOP account. The Agent runs auth-start --open and shows you a confirmation code. Personally check your account and read permissions in the browser before approving. It then runs auth-complete. Credentials stay in ~/.config/pulsebeat with restricted file permissions and can be revoked on /agent.html.

```sh
python3 scripts/pulsebeat.py sync --directory ~/PulseBeat-private/library
python3 scripts/pulsebeat.py analyze --input ~/PulseBeat-private/library/current.json --out ~/PulseBeat-private/report --lang en
```

Pass --qq, --netease and --spotify supplemental files when available; use paths recorded in library/sync.json. The Agent reads analysis.json and writes interpretation.md plus insights.json before rendering:

```sh
python3 scripts/pulsebeat.py html --analysis ~/PulseBeat-private/report/analysis.json --interpretation ~/PulseBeat-private/report/interpretation.md --insights ~/PulseBeat-private/report/insights.json --out ~/PulseBeat-private/report/index.html --lang en
```

Every analysis must deliver index.html, with index-share.svg and a provenance manifest. The template features a dark conclusion panel, recovery ring, metric comparisons and independent trend scales. It uses no remote fonts or chart libraries and can be printed or saved as PDF.

For a preview without an account, run demo_report.py above and open data/template-demo/en/index.html or data/template-demo/zh-CN/index.html. These are clearly labeled, formula-generated examples, not personal health records. Generated data is Git-ignored.

## Spotify history

Select all relevant Extended Streaming History audio JSON files from Spotify's personal data export. Specify the person's actual historical timezone separately:

```sh
python3 scripts/pulsebeat.py spotify-import --files ~/Downloads/Streaming_History_Audio_0.json --timezone Europe/London --out ~/PulseBeat-private/spotify.json
```

The importer uses actual ms_played, removes duplicate events across input files and omits identity, IP and device fields. Pass the resulting file to sync and analyze with --spotify. Totals are grouped by stream end date; they describe observed history, not guaranteed complete daily exposure, and are not automatically correlated with health.

## Boundaries and verification

Raw exports and reports remain local; scripts do not call an LLM API. Your Agent may still use a cloud model. Share only necessary summaries and decide personally whether to share the report or card. No automatic upload occurs. Never commit keys, personal data or real reports.

Favorites are not listening exposure. Missing data is not zero. Sparse or timezone-incompatible observations do not produce correlation claims. Exploratory associations are not causal findings, diagnoses or treatment advice.

```sh
python3 -m unittest discover -s tests -p 'test_*.py'
```

See [English Agent workflow](references/workflow.en.md), [SKILL.md](SKILL.md) and the bundled source notices for integration details.
