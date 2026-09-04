#!/usr/bin/env python3
"""Build an offline, responsive viewer for already exported PNG cards."""
import base64,hashlib,json,pathlib,sys
from i18n import activate
from music_story_html import L,esc

def build(directory):
 p=pathlib.Path(directory);m=json.loads((p/'manifest.json').read_text());activate(m['language']);assets=pathlib.Path(__file__).resolve().parents[1]/'assets'
 if not m.get('rendered'):raise ValueError('Export PNGs before building the viewer')
 figures=[]
 for i,name in enumerate(m['files']):
  if pathlib.Path(name).name!=name or not name.endswith('.png'):raise ValueError('Invalid image filename')
  uri='data:image/png;base64,'+base64.b64encode((p/name).read_bytes()).decode()
  figures.append('<img class="slide" '+('hidden ' if i else '')+'src="'+uri+'" data-file="'+esc(name)+'" alt="'+L('分享图片 ','Share image ')+str(i+1)+'" width="1080" height="1440">')
 css=(assets/'share-viewer.css').read_text();js=(assets/'share-viewer.js').read_text();digest=base64.b64encode(hashlib.sha256(js.encode()).digest()).decode()
 html='<!doctype html><html lang="'+m['language']+'"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta http-equiv="Content-Security-Policy" content="default-src \'none\'; img-src data:; style-src \'unsafe-inline\'; script-src \'sha256-'+digest+'\'; base-uri \'none\'; form-action \'none\'"><title>PulseBeat · '+L('分享图集','Share series')+'</title><style>'+css+'</style></head><body><header><div class="brand">pulsebeat<span>.</span><small>'+L('分享图集','Share series')+'</small></div><div class="downloads"><a id="download" download href="'+esc(m['files'][0])+'">'+L('下载当前 PNG','Download current PNG')+'</a><a class="primary" download href="share-images.zip">'+L('下载全部 ZIP','Download all ZIP')+'</a></div></header><main><div class="toolbar"><div class="pager"><button id="prev" aria-label="'+L('上一张','Previous')+'">←</button><span id="counter" aria-live="polite">1 / '+str(len(figures))+'</span><button id="next" aria-label="'+L('下一张','Next')+'">→</button></div><div class="zoom"><button id="fit" aria-pressed="true">'+L('适应窗口','Fit window')+'</button><button id="actual" aria-pressed="false">100%</button></div><span class="hint">'+L('方向键切换 · 手机左右滑动','Arrow keys · Swipe on mobile')+'</span></div><div id="stage" tabindex="0" aria-label="'+L('图片预览','Image preview')+'">'+''.join(figures)+'</div><nav id="thumbs" aria-label="'+L('选择图片','Choose image')+'"></nav><p class="note">1080 × 1440 PNG · '+L('预览缩放不影响下载清晰度 · 仅保存在本地','Preview scaling does not change download quality · Local files only')+'</p></main><script>'+js+'</script></body></html>'
 (p/'index.html').write_text(html);(p/'index.html').chmod(0o600)
if __name__=='__main__':build(sys.argv[1])
