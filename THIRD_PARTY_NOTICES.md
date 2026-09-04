# Third-party notices

The unmodified snapshots under vendor/qqmusic and vendor/netease originate from tencentmusic/qqmusic-skills and NetEase/skills respectively. Both are distributed under Apache-2.0; original license files and notices are retained in each snapshot. Exact commits and per-file SHA-256 checksums are recorded in vendor/lock.json. PulseBeat adapters, translations and report templates are separate from these upstream files and are not official music-provider products.

Bundled upstream instructions are references for selected music operations, not automatic permission to execute every workflow. PulseBeat never prints keys, requests keys in chat, sends health context to music services, or sets up developer applications for ordinary users. Do not run upstream self-updaters against these pinned snapshots. Scheduled messages, playback and playlist writes require the corresponding user request. Upstream developer setup and media-player installers are included for completeness, not required for local analysis.

No Spotify source skill is bundled: no official personal-listening SKILL.md package was identified. The official Spotify ChatGPT app and personal data export are documented in references/spotify.md; the local import adapter is maintained by PulseBeat.

## Kugou Music

vendor/kugou contains unmodified SKILL.md, README.md and package.json from the published npm package @kg-ai/kugou-skill version 0.0.13 (https://www.npmjs.com/package/@kg-ai/kugou-skill/v/0.0.13). This matches the CLI version previously verified with PulseBeat. The npm tarball SHA-512 integrity and individual file SHA-256 values are recorded in vendor/lock.json.

The original package.json declares MIT. The published package does not contain a separate LICENSE file or a named author; its original metadata and documentation are preserved without inventing a copyright notice. Only the Skill/documentation snapshot is bundled, not the CLI binaries or installation scripts. Install the runtime separately when needed; do not run npm install inside vendor/kugou, whose package.json is provenance metadata rather than a complete runnable package.

Kugou login output may contain a secret field. Display only the QR code and status required for personal authorization, never raw credential-bearing output. Personal authorization is not included in this distribution.
