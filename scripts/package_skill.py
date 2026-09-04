#!/usr/bin/env python3
"""Build a standalone skill archive from explicit public resource roots."""
import pathlib, zipfile
root=pathlib.Path(__file__).resolve().parents[1]
files=[root/name for name in ('SKILL.md','README.md','README.en.md','THIRD_PARTY_NOTICES.md')]
for directory in ('agents','assets','references','locales','vendor','scripts'):
    files.extend(p for p in (root/directory).rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix not in ('.pyc','.log'))
target=root/'dist'/'pulsebeat-skill.zip';target.parent.mkdir(parents=True,exist_ok=True)
with zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED) as z:
    for p in sorted(files):z.write(p,'pulsebeat/'+p.relative_to(root).as_posix())
print('Skill ZIP:',target,'files:',len(files))
