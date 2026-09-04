"""Music-first editorial chapter with local SVG charts and embedded artwork."""
import base64,datetime as dt,html,math,urllib.parse
from i18n import CURRENT,resolve

def L(zh,en):return en if (CURRENT.get() or resolve())=='en' else zh
def esc(v):return html.escape(str(v if v is not None else ''),quote=True)
def num(v):return isinstance(v,(int,float)) and not isinstance(v,bool) and math.isfinite(v)
def f(v):return f'{v:,.1f}'.rstrip('0').rstrip('.') if num(v) else '—'
def link(url,label):
    p=urllib.parse.urlsplit(str(url or ''))
    if p.scheme!='https' or not p.hostname or p.username or p.password:return ''
    return '<a target="_blank" rel="noopener noreferrer" href="'+esc(url)+'">'+esc(label)+' ↗</a>'
def artwork(item,title,index):
    uri=item.get('imageDataUri','')
    if uri.startswith(('data:image/jpeg;base64,','data:image/png;base64,','data:image/webp;base64,')) and len(uri)<2100000:
        try:
            from music_media import image_type
            raw=base64.b64decode(uri.split(',',1)[1],validate=True)
            if image_type(raw)==uri.split(';')[0][5:]:return '<img loading="lazy" src="'+esc(uri)+'" alt="'+esc(title)+'" width="400" height="400">'
        except (ValueError,TypeError):pass
    return '<div class="cover-art" style="--record-hue:'+str((index*47+20)%360)+'"><span>'+str(index+1).zfill(2)+'</span><small>'+L('唱片意象 · 非原封面','ILLUSTRATION · NOT ORIGINAL ART')+'</small></div>'

def calendar(rows):
    if not rows:return '<p>'+L('暂无按日记录。','No daily observations.')+'</p>'
    values={r['date']:r['seconds']/60 for r in rows};start=dt.date.fromisoformat(min(values));end=dt.date.fromisoformat(max(values));limit=min((end-start).days+1,366)
    cap=max(values.values()) or 1;cells=['<span></span>']*start.weekday()
    for n in range(limit):
        date=start+dt.timedelta(days=n);v=values.get(str(date));ratio=0 if v is None else v/cap
        label=str(date)+' · '+(L('未覆盖','Not covered') if v is None else f(v)+' min')
        cells.append('<div class="calendar-day '+('missing' if v is None else 'silent' if v==0 else 'listened')+'" style="--heat:'+str(round(.15+.85*ratio,3))+'" title="'+esc(label)+'"><b>'+date.strftime('%m/%d')+'</b><span>'+('—' if v is None else f(v))+'</span></div>')
    return '<div class="listening-calendar">'+''.join('<small>'+x+'</small>' for x in L(['一','二','三','四','五','六','日'],['M','T','W','T','F','S','S']))+''.join(cells)+'</div><p class="music-caption">'+L('单位：分钟。0 为接口返回零；斜纹为未覆盖。最多显示 366 天。','Minutes. Zero is a reported value; stripes mean no coverage. Up to 366 days.')+'</p>'

def weekday_chart(rows):
    maximum=max([r.get('meanMinutes') or 0 for r in rows]+[1]);parts=[]
    for i,r in enumerate(rows):
        v=r.get('meanMinutes');height=(v or 0)/maximum*110;x=22+i*57
        title=L('观测日均值','Observed-day mean')+' '+f(v)+' min · n='+str(r['n'])
        parts.append('<rect x="'+str(x)+'" y="'+str(132-height)+'" width="33" height="'+str(height)+'" rx="5" fill="#e47a42"><title>'+esc(title)+'</title></rect><text x="'+str(x+16)+'" y="'+str(124-height)+'" text-anchor="middle">'+f(v)+'</text><text x="'+str(x+16)+'" y="155" text-anchor="middle">'+L(['一','二','三','四','五','六','日'],['M','T','W','T','F','S','S'])[i]+'</text><text x="'+str(x+16)+'" y="172" text-anchor="middle">n='+str(r['n'])+'</text>')
    return '<svg class="weekday-chart" role="img" aria-label="'+L('每周各日的平均听歌分钟与样本数','Mean listening minutes and sample count by weekday')+'" viewBox="0 0 440 185">'+''.join(parts)+'</svg>'

def tag_bars(rows):
    maximum=max([r['days'] for r in rows]+[1]);out=[]
    for r in rows[:8]:out.append('<div class="taste-bar"><div><b>'+esc(r['name'])+'</b><span>'+str(r['days'])+L(' 个日榜',' daily lists')+'</span></div><i style="width:'+str(r['days']/maximum*100)+'%"></i></div>')
    return ''.join(out) or '<p>'+L('没有来源标签，不猜测曲风。','No source tags; genre is not inferred.')+'</p>'

def clock_map(rows):
    if not rows:return '<p class="music-caption">'+L('没有可靠时段记录，暂不绘制场景热图。','No reliable time bins; a scene heatmap is not available.')+'</p>'
    dates=sorted({r['date'] for r in rows});slots=sorted({(r['start'],r['end']) for r in rows});lookup={(r['date'],r['start'],r['end']):r['minutes'] for r in rows};maximum=max([r['minutes'] for r in rows]+[1]) or 1
    content='<table class="clock-table"><thead><tr><th>'+L('时段','Time')+'</th>'+''.join('<th>'+esc(d[5:])+'</th>' for d in dates)+'</tr></thead><tbody>'
    for start,end in slots:
        content+='<tr><th>'+f'{start:02d}–{end:02d}'+'</th>'
        for date in dates:
            v=lookup.get((date,start,end));tip=date+' · '+f'{start:02d}:00–{end:02d}:00 · '+(L('未返回','Not returned') if v is None else f(v)+' min')
            content+='<td title="'+esc(tip)+'" class="'+('unreported' if v is None else 'reported')+'" style="--heat:'+str(.12+.88*(v or 0)/maximum)+'">'+('·' if v is None else esc(f(v)))+'</td>'
        content+='</tr>'
    return '<div class="clock-scroll">'+content+'</tbody></table></div><p class="music-caption">'+L('仅接口返回的 Top 时段，单位分钟；空格不是零，不补齐为全天行为。','Only provider-returned top time bins, in minutes. Missing bins are not zero or a full-day history.')+'</p>'

def render(data,insights,media):
    portraits=data.get('musicPortraits',{});stories=insights.get('musicStories',{});parts=[];names={'kugou':L('酷狗音乐','Kugou Music'),'qqmusic':'QQ Music','netease':L('网易云音乐','NetEase Cloud Music'),'spotify':'Spotify'}
    for index,(provider,p) in enumerate(portraits.items()):
        story=stories.get(provider,{}) or {};summary=p.get('summary',{});tracks=p.get('tracks',[]);items=(media or {}).get('items',{});cards=[]
        for n,t in enumerate(tracks[:8]):
            item=items.get(provider+':'+t['id'],{});valid=item.get('title')==t['title'] and item.get('artist')==t.get('artist','');item=item if valid else {}
            evidence=(str(t.get('observedPlays',0))+L(' 次榜内记录',' listed plays')+' · '+str(t.get('listedDays',0))+L(' 个出现日',' observed days')) if p.get('basis')=='daily_top_list' else (str(t.get('observedPlays',0))+L(' 条导出事件',' exported events') if p.get('basis')=='export_events' else L('收藏快照','Favorite snapshot'))
            public_context=('<p>'+esc(item.get('context'))+'</p>'+link(item.get('contextSource'),item.get('contextSourceTitle') or L('公开资料','Public source'))) if item.get('context') else '<p>'+L('曲目信息来自本次平台记录；暂无已核对的作品介绍。','Track metadata comes from the provider; no verified editorial context yet.')+'</p>'
            personal=(story.get('trackNotes') or {}).get(t['id'])
            cards.append('<article class="record-card"><div class="record-cover">'+artwork(item,t['title'],n)+'<span class="record-number">'+str(n+1).zfill(2)+'</span></div><h4>'+esc(t['title'])+'</h4><p class="record-artist">'+esc(t.get('artist',''))+'</p><p class="record-evidence">'+esc(evidence)+'</p>'+('<p class="personal-note">'+esc(personal)+'</p>' if personal else '')+'<details><summary>'+L('作品背景与图片来源','Track context & artwork source')+'</summary>'+public_context+link(item.get('imageSource'),L('酷狗提供的图片','Provider artwork'))+'</details></article>')
        chapters=''.join('<article><small>'+esc(c.get('kind',L('观察','Observation')))+'</small><h3>'+esc(c.get('title',''))+'</h3><p>'+esc(c.get('body',''))+'</p><footer>'+esc(c.get('evidence',''))+'</footer></article>' for c in story.get('chapters',[])[:3])
        scenes=''.join('<article class="scene"><span>'+esc(c.get('status',L('待确认','To confirm')))+'</span><h4>'+esc(c.get('title',''))+'</h4><p>'+esc(c.get('body',''))+'</p><small>'+esc(c.get('evidence',''))+'</small></article>' for c in story.get('scenes',[])[:3])
        hero_item=items.get(provider+':'+tracks[0]['id'],{}) if tracks else {}
        if tracks and (hero_item.get('title')!=tracks[0]['title'] or hero_item.get('artist')!=tracks[0].get('artist','')):hero_item={}
        period=' — '.join(summary.get('range',[]));title=story.get('title') or L('把听过的日子，重新听见。','Rediscover the days you listened.');lede=story.get('lede') or L('从实际可用的记录出发，看看哪些歌曲、日期与时间反复出现。','Start with the available records: which songs, days and moments return?')
        stats=[(f(summary.get('totalMinutes')),L('观测窗口总分钟','Minutes in observed window')),(str(summary.get('activeDays','—'))+' / '+str(summary.get('observedDays','—')),L('非零 / 已覆盖天数','Active / covered days')),(str(p.get('distinctListedTracks','—')),L('日榜中不同曲目 · 非完整曲库','Distinct listed tracks · partial catalog'))]
        boundary=L('以下排行累计日 Top 列表中可见的记录，是下限，不等于全量最爱榜。曲风与语言按出现日计数，可重叠，不是时长占比。','Rankings sum records visible in daily top lists: lower bounds, not a complete favorites ranking. Genre/language counts are overlapping day appearances, not duration shares.') if p.get('basis')=='daily_top_list' else L('仅当前导出或收藏快照，不能外推为完整账号历史。','Only the supplied export or favorites snapshot; not the complete account history.')
        parts.append('<section class="sound-story" data-music-provider="'+provider+'"'+(' hidden' if index else '')+'><div class="sound-hero"><div><span class="sound-kicker">SIDE A / YOUR SOUNDTRACK</span><p class="sound-period">'+esc(names.get(provider,provider))+' · '+esc(period)+'</p><h2>'+esc(title)+'</h2><p class="sound-lede">'+esc(lede)+'</p><div class="sound-stats">'+''.join('<div><strong>'+esc(v)+'</strong><small>'+esc(label)+'</small></div>' for v,label in stats)+'</div></div><div class="vinyl-composition"><div class="vinyl"></div><div class="sleeve">'+(artwork(hero_item,tracks[0]['title'],0) if tracks else artwork({},'Music',0))+'</div><span class="vinyl-stamp">'+L('你的声音切片','A SLICE OF YOUR SOUND')+'</span></div></div><div class="listening-chapters">'+chapters+'</div><div class="music-heading"><span>01 / ON REPEAT</span><h3>'+L('有些旋律，不止遇见一次。','Some melodies keep finding you.')+'</h3><p>'+esc(boundary)+'</p></div><div class="record-grid">'+''.join(cards)+'</div><div class="music-heading"><span>02 / THE SHAPE OF YOUR DAYS</span><h3>'+L('听歌并不平均地，发生在每一天。','Listening does not spread evenly across your days.')+'</h3></div><div class="music-split"><article class="music-panel"><h4>'+L('你的听歌日历','Your listening calendar')+'</h4>'+calendar(p.get('daily',[]))+'</article><article class="music-panel"><h4>'+L('一周的节奏','Your weekly rhythm')+'</h4>'+weekday_chart(p.get('weekdays',[]))+'<p>'+esc(story.get('rhythmNote') or L('均值仅由已覆盖日计算，少数长听歌日可能改变整体形状。','Means use covered days only; a few long-listening days can dominate.'))+'</p></article></div><div class="music-split"><article class="music-panel"><h4>'+L('曲风的纹理','The texture of your taste')+'</h4>'+tag_bars(p.get('genreDays',[]))+'</article><article class="music-panel"><h4>'+L('语言的版图','Languages in your rotation')+'</h4>'+tag_bars(p.get('languageDays',[]))+'</article></div><div class="music-heading"><span>03 / MOMENTS, NOT ASSUMPTIONS</span><h3>'+L('听见时间，也给场景留一个问号。','Listen to the timing. Leave room for context.')+'</h3></div><article class="music-panel">'+clock_map(p.get('clockRows',[]))+'</article><div class="scene-grid">'+scenes+'</div><p class="music-caption">'+L('作品简介是公开背景；个人场景来自有标记的观察或假设，不从歌名判断情绪、活动或健康效果。封面仅嵌入本地报告，权利归原权利人。','Public track context is separate from personal observations and hypotheses. Titles do not establish mood, activity or health effects. Artwork is embedded locally; rights remain with its owners.')+'</p></section>')
    if not parts:return ''
    picker='<label class="music-picker">'+L('切换音乐来源','Music source')+' <select id="music-provider">'+''.join('<option value="'+k+'">'+esc(names.get(k,k))+'</option>' for k in portraits)+'</select></label>' if len(parts)>1 else ''
    return '<div id="soundtrack">'+picker+''.join(parts)+'</div>'
