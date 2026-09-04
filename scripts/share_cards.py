#!/usr/bin/env python3
"""Generate a local editorial carousel from selected report summaries, never raw exports."""
import argparse,base64,json,pathlib,hashlib
from i18n import activate
from music_story_html import L,esc,f,artwork,tag_bars
ASSETS=pathlib.Path(__file__).resolve().parents[1]/'assets'

def generate(data,info,media,out,lang='auto'):
    language=activate(lang);out=pathlib.Path(out);out.mkdir(parents=True,exist_ok=True)
    portraits=data.get('musicPortraits',{});provider=next(iter(portraits),'kugou');p=portraits.get(provider,{});s=p.get('summary',{});story=info.get('musicStories',{}).get(provider,{})
    pair=next((a for a in data.get('associations',[]) if a.get('provider')==provider and a.get('outcome')=='recovery'),{});n=pair.get('n',0)
    health={r['date']:r for r in data.get('healthDaily',[])};music={r['date']:r for r in data.get('musicDaily',{}).get(provider,[])}
    period=' — '.join(s.get('range',[])) or L('当前可用记录','Available records');health_period=' — '.join((data.get('healthMetrics',{}).get('recovery') or {}).get('range',[]))
    logo='data:image/svg+xml;base64,'+base64.b64encode((ASSETS/'brand/icon.svg').read_bytes()).decode();cards=[]
    def add(title,body,foot,kicker,theme='cream'):
        i=len(cards)+1
        cards.append('<article class="share-card '+theme+'" id="card-'+str(i)+'"><header><div><img src="'+logo+'" alt="">pulsebeat.</div><span>MY RHYTHM / '+str(i).zfill(2)+'</span></header><div class="content"><p class="eyebrow">'+esc(kicker)+'</p><h1>'+esc(title)+'</h1>'+body+'</div><footer><span>'+esc(foot)+'</span><b>'+str(i).zfill(2)+' / 06</b></footer></article>')
    cover='<p class="lead">'+esc(info.get('summary',''))+'</p><div class="orbits"><div class="orbit music"><strong>'+f(s.get('totalMinutes'))+'</strong><span>'+L('音乐 · 分钟','MUSIC · MINUTES')+'</span></div><div class="orbit body"><strong>'+str(n)+'</strong><span>'+L('身体 × 音乐 · 有效配对','BODY × MUSIC · VERIFIED PAIRS')+'</span></div></div><div class="cover-note"><b>'+L('我的身体与音乐观察手记','My body & music journal')+'</b><p>'+esc(provider.upper()+' · '+period)+'<br>WHOOP · '+esc(health_period)+'</p></div>'
    add(info.get('headline',L('把身体和音乐，放在一起看。','Body and music, in the same frame.')),cover,L('个人记录，不代表因果。仅使用已授权数据。','Personal observations, not causation. Authorized data only.'),'BODY × MUSIC / PERSONAL EDITION','dark')
    rows=[]
    for dates in sorted(pair.get('paired_dates',[]),key=lambda x:x['health'])[-4:]:
        h=health.get(dates['health'],{});m=music.get(dates['music'],{});v=m.get('seconds');r=h.get('recovery')
        rows.append('<div class="pair-row"><div class="dates">'+esc(dates['music'][5:])+' → '+esc(dates['health'][5:])+'</div><div class="pair-values"><span class="orange">'+f(v/60 if v is not None else None)+'<small>'+L('分钟听歌','min listening')+'</small></span><span class="green">'+f(r)+'<small>'+L('次日恢复','next-day recovery')+'</small></span><span>'+f(h.get('sleep_hours'))+'<small>'+L('小时主睡眠','h main sleep')+'</small></span></div></div>')
    note=(info.get('findings') or [{}])[0]
    add(L('同一条时间线，\n听见身体的另一面。','One timeline.\nTwo kinds of signal.'),'<div class="pair-table">'+(''.join(rows) or '<p>'+L('暂无经核对的配对记录。','No verified paired records yet.')+'</p>')+'</div><div class="callout"><h2>'+esc(note.get('title',''))+'</h2><p>'+esc(note.get('detail',''))+'</p></div>',health_period+' · '+L('前一自然日音乐 → 次日 WHOOP；0 为本平台零值。展示最近至多 4 对。','Prior-day music → next-day WHOOP. Zero is provider-specific. Latest 4 pairs at most.'),'01 / A SHARED TIMELINE')
    genres=tag_bars(p.get('genreDays',[])[:4]);languages=tag_bars(p.get('languageDays',[])[:4]);chapters=story.get('chapters',[]);c=chapters[1] if len(chapters)>1 else {}
    add(c.get('title') or L('听歌偏好，有自己的纹理。','The texture of your taste.'),'<p class="lead">'+esc(c.get('body') or L('只展示来源中确实出现的标签，不从歌名猜测口味。','Only source-supplied tags; titles do not establish taste.'))+'</p><div class="taste-columns"><section><h2>'+L('曲风出现日','Genre appearances')+'</h2>'+genres+'</section><section><h2>'+L('语言出现日','Language appearances')+'</h2>'+languages+'</section></div><div class="big-strip"><strong>'+str(s.get('activeDays','—'))+' / '+str(s.get('observedDays','—'))+'</strong><span>'+L('非零听歌日 / 已覆盖日','Active / covered listening days')+'</span></div>',esc(provider.upper()+' · '+period)+' · '+L('标签按日榜出现计数，可重叠，非时长占比。','Overlapping daily-list appearances, not duration shares.'),'02 / YOUR TASTE')
    songs=[]
    for i,t in enumerate(p.get('tracks',[])[:4]):
        item=(media or {}).get('items',{}).get(provider+':'+t['id'],{})
        if item.get('title')!=t['title'] or item.get('artist')!=t.get('artist',''):item={}
        stat=(str(t.get('observedPlays',0))+L(' 次榜内记录 · ',' listed plays · ')+str(t.get('listedDays',0))+L(' 天',' days')) if p.get('basis')=='daily_top_list' else L('当前导出 / 收藏记录','Supplied export / favorite')
        songs.append('<section class="song"><div class="sleeve">'+artwork(item,t['title'],i)+'</div><h2>'+esc(t['title'])+'</h2><p>'+esc(t.get('artist',''))+'</p><small>'+esc(stat)+'</small></section>')
    add(L('这些旋律，\n在我的记录里留下名字。','The songs that\nleft a trace.'),'<div class="songs">'+(''.join(songs) or '<p>'+L('本次没有可用曲目。','No track records available.')+'</p>')+'</div>',esc(provider.upper()+' · '+period)+' · '+L('日榜是可见下限，非全量最爱榜。封面权利归原权利人。','Daily lists are lower bounds, not a full favorites ranking. Artwork belongs to its owners.'),'03 / ON REPEAT','peach')
    scenes=story.get('scenes',[])[:2];scene_html=''.join('<div class="scene"><small>'+esc(x.get('status',''))+'</small><h2>'+esc(x.get('title',''))+'</h2><p>'+esc(x.get('body',''))+'</p><em>'+esc(x.get('evidence',''))+'</em></div>' for x in scenes)
    add(L('音乐发生的时间，\n还需要生活来解释。','Timing needs\nits life context.'),scene_html or '<p class="lead">'+L('暂无可靠场景线索。下次听歌时，记下时间、活动和主观感受。','No reliable scene context yet. Record the time, activity and how you felt.')+'</p>',provider.upper()+' · '+period+' · '+L('时段不等于活动；作品情感不等于个人情绪。','A time bin is not an activity; a song’s theme is not the listener’s mood.'),'04 / MOMENTS & CONTEXT','sage')
    steps=info.get('next_steps',[])[:2];step_html=''.join('<div class="step"><span>'+str(i+1).zfill(2)+'</span><div><h2>'+esc(x.get('title',''))+'</h2><p>'+esc(x.get('detail',''))+'</p></div></div>' for i,x in enumerate(steps))
    add(L('下次听歌，\n多留一条生活线索。','Next time you listen,\nleave a little context.'),step_html+'<div class="prompt"><small>'+L('我的记录提示','MY JOURNAL PROMPT')+'</small><p>'+L('在做什么？\n什么时候听？\n听完感觉如何？','What was I doing?\nWhen did I listen?\nHow did I feel afterward?')+'</p></div>',L('本地生成，未自动发布。个人观察，不是医疗建议。','Generated locally; not automatically published. Personal observations, not medical advice.'),'05 / THE NEXT CHAPTER','dark')
    css=(ASSETS/'share-series.css').read_text();html='<!doctype html><html lang="'+language+'"><head><meta charset="utf-8"><meta name="viewport" content="width=1080"><meta http-equiv="Content-Security-Policy" content="default-src \'none\'; img-src data:; style-src \'unsafe-inline\'; base-uri \'none\'; form-action \'none\'"><title>PulseBeat · '+L('分享图集','Share series')+'</title><style>'+css+'</style></head><body><!--DOWNLOADS-->'+''.join(cards)+'</body></html>'
    (out/'cards.html').write_text(html,encoding='utf-8');(out/'cards.html').chmod(0o600)
    (out/'index.html').write_text(html,encoding='utf-8');(out/'index.html').chmod(0o600)
    manifest={'language':language,'count':len(cards),'size':[1080,1440],'rendered':False,'sourceAnalysisSha256':hashlib.sha256(json.dumps(data,sort_keys=True,ensure_ascii=False).encode()).hexdigest(),'files':[]}
    (out/'manifest.json').write_text(json.dumps(manifest,indent=2));return out/'index.html'

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--analysis',required=True);p.add_argument('--insights',required=True);p.add_argument('--media');p.add_argument('--out',required=True);p.add_argument('--lang',default='auto');a=p.parse_args()
    read=lambda path:json.loads(pathlib.Path(path).read_text())
    info=read(a.insights)
    from i18n import resolve
    if info.get('language') and resolve(info['language'])!=resolve(a.lang):raise ValueError('Rewrite insights in the selected language first')
    print(generate(read(a.analysis),info,read(a.media) if a.media else None,a.out,a.lang))
if __name__=='__main__':main()
