# Third-party notices

The unmodified snapshots under vendor/qqmusic and vendor/netease originate from tencentmusic/qqmusic-skills and NetEase/skills respectively. Both are distributed under Apache-2.0; original license files and notices are retained in each snapshot. Exact commits and per-file SHA-256 checksums are recorded in vendor/lock.json. PulseBeat adapters, translations and report templates are separate from these upstream files and are not official music-provider products.

Bundled upstream instructions are references for selected music operations, not automatic permission to execute every workflow. PulseBeat never prints keys, requests keys in chat, sends health context to music services, or sets up developer applications for ordinary users. Do not run upstream self-updaters against these pinned snapshots. Scheduled messages, playback and playlist writes require the corresponding user request. Upstream developer setup and media-player installers are included for completeness, not required for local analysis.

No Spotify source skill is bundled: no official personal-listening SKILL.md package was identified. The official Spotify ChatGPT app and personal data export are documented in references/spotify.md; the local import adapter is maintained by PulseBeat.
