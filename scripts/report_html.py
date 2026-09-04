#!/usr/bin/env python3
"""Offline, escaped HTML report; no network, external assets or executable source text."""
from i18n import tr, activate, resolve
import argparse, base64, datetime as dt, hashlib, html, json, math, os, pathlib, re

def esc(value): return html.escape(str(value if value is not None else '—'),quote=True)
def markdown(text):
    # Deliberately small text renderer: raw HTML and Markdown links are not executed.
    blocks=[];table=[]
    def inline(s): return re.sub(r'\*\*(.+?)\*\*',r'<strong>\1</strong>',esc(s))
    def flush_table():
        if table:
            blocks.append('<div class="scroll"><table>'+''.join('<tr>'+''.join('<td>'+inline(c.strip())+'</td>' for c in row.strip('|').split('|'))+'</tr>' for row in table if not re.fullmatch(r'[\s|:\-]+',row))+'</table></div>');table.clear()
    for line in text.splitlines():
        if line.startswith('|'): table.append(line);continue
        flush_table()
        if not line.strip(): continue
        match=re.match(r'^(#{1,4}) (.*)',line)
        if match:
            level=min(4,len(match[1])+1);blocks.append(f'<h{level}>'+inline(match[2])+f'</h{level}>')
        elif line.startswith('- '): blocks.append('<p class="bullet">• '+inline(line[2:])+'</p>')
        else: blocks.append('<p>'+inline(line)+'</p>')
    flush_table();return '\n'.join(blocks)

ASSETS=pathlib.Path(__file__).resolve().parents[1]/'assets'
LABELS={'recovery':'恢复分数','hrv_ms':'HRV','sleep_hours':'主睡眠时长','resting_hr':'静息心率','cycle_strain':'周期负荷'}
COLORS={'recovery':'#86ac48','hrv_ms':'#3ab49c','sleep_hours':'#8792e8','resting_hr':'#e27491','music':'#d98c57'}
PROVIDERS={'kugou':'酷狗音乐','qqmusic':'QQ 音乐','netease':'网易云音乐','spotify':'Spotify'}
def labels(): return {k:tr(v) for k,v in LABELS.items()}
def provider_labels(): return {k:tr(v) for k,v in PROVIDERS.items()}
def numeric(v): return isinstance(v,(int,float)) and not isinstance(v,bool) and math.isfinite(v)
def fmt(v,d=1): return f'{v:.{d}f}'.rstrip('0').rstrip('.') if numeric(v) and d else (str(round(v)) if numeric(v) else '—')
def plain(s): return s.replace('**','').replace(chr(96),'').strip()
def overview(data,note):
    paragraphs=[plain(p) for p in re.split(r'\n\s*\n',note) if p.strip() and not p.lstrip().startswith(('#','|'))]
    findings=[]
    for section in re.split(r'\n## ',note)[1:]:
        body=[p.strip() for p in re.split(r'\n\s*\n',section)[1:] if p.strip() and not p.startswith('|')]
        if body:
            title=re.search(r'\*\*(.+?)\*\*',body[0])
            findings.append({'title':plain(title[1] if title else section.splitlines()[0]),'detail':plain(body[0])[:180],'evidence':tr('详见完整 AI 解读及统计底稿')})
    return {'headline':findings[0]['title'] if findings else tr('每一次记录，都有自己的节奏。'),'summary':findings[0]['detail'] if findings else (paragraphs[0][:180] if paragraphs else tr('等待个人数据解读。')),'findings':findings[:3],'next_steps':[{'title':tr('持续记录，再观察变化'),'detail':tr('结合报告中提出的问题，继续积累同口径数据；只有来源齐全、日期可对齐的记录才参与比较。')},{'title':tr('带着场景理解音乐'),'detail':tr('区分收藏偏好、实际收听和发生时段；不要把同一天的共同变化当成因果。')}]}
def ring(value,mean):
    content='<circle cx="140" cy="140" r="116" fill="none" stroke="#29342d" stroke-width="14"/>'
    if numeric(value):
        total=2*math.pi*116;length=max(0,min(100,value))/100*total
        content+=f'<circle cx="140" cy="140" r="116" fill="none" stroke="#b4ee50" stroke-width="14" stroke-linecap="round" stroke-dasharray="{length:.2f} {total:.2f}" transform="rotate(-90 140 140)"/>'
    if numeric(mean):
        c=2*math.pi*98;limit=max(0,min(100,mean))/100*c
        content+=f'<defs><mask id="baseline"><circle cx="140" cy="140" r="98" fill="none" stroke="white" stroke-width="8" stroke-dasharray="{limit:.2f} {c:.2f}" transform="rotate(-90 140 140)"/></mask></defs><circle cx="140" cy="140" r="98" fill="none" stroke="#5a6e49" stroke-width="3" stroke-dasharray="2 6" mask="url(#baseline)"/>'
    return tr('<svg viewBox="0 0 280 280" role="img" aria-label="恢复分数，刻度零至一百">')+content+'</svg>'
def chart(points,color,unit='',maximum=None,bar=False,mini=False):
    pairs=sorted((dt.date.fromisoformat(d),float(v)) for d,v in points if numeric(v))
    if not pairs:return tr('<p class="subtle">暂无可画图的观测</p>')
    left,right,top,bottom=(2,438,4,45) if mini else (36,426,15,128)
    cap=maximum or max(1,max(v for _,v in pairs)*1.2);start,end=pairs[0][0],pairs[-1][0];span=max(1,(end-start).days)
    x=lambda d:left+(right-left)*((d-start).days/span if end!=start else .5)
    y=lambda v:bottom-(bottom-top)*max(0,min(cap,v))/cap
    parts=[]
    if not mini:
        for v in [0,cap/2,cap]:parts.append(f'<line class="axis" x1="{left}" y1="{y(v):.1f}" x2="{right}" y2="{y(v):.1f}"/><text x="{left-7}" y="{y(v)+3:.1f}" text-anchor="end">{esc(fmt(v))}</text>')
        parts.append(f'<text x="{left}" y="150">{start.strftime("%m/%d")}</text><text x="{right}" y="150" text-anchor="end">{end.strftime("%m/%d")}</text>')
    last=None;segment=[]
    def flush():
        if len(segment)>1:parts.append('<polyline class="path" fill="none" stroke="'+color+'" stroke-width="2.5" points="'+' '.join(segment)+'"/>')
        segment.clear()
    for date,value in pairs:
        px,py=x(date),y(value);tip=esc(f'{date} · {fmt(value,2)} {unit}')
        if bar:
            bw=min(18,(right-left)/max(span+1,1)*.64)
            parts.append(f'<rect x="{px-bw/2:.1f}" y="{py:.1f}" width="{bw:.1f}" height="{max(0,bottom-py):.1f}" rx="2" fill="{color}" tabindex="0"><title>{tip}</title></rect>')
        else:
            if last and (date-last).days!=1:flush()
            segment.append(f'{px:.1f},{py:.1f}')
            parts.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="{2 if mini else 3.3}" fill="{color}" tabindex="0"><title>{tip}</title></circle>');last=date
    flush()
    return f'''<svg class="{('spark' if mini else 'series')}" viewBox="0 0 440 {(50 if mini else 160)}" role="img" aria-label="{esc(unit)}，{start}{tr(' 至 ')}{end}，{len(pairs)}{tr(' 次观测">')}'''+''.join(parts)+'</svg>'
def series_panels(data):
    health=data.get('healthDaily',[]);music=data.get('musicDaily',{})
    series=[(labels()[key],[(r['date'],r.get(key)) for r in health],COLORS[key],unit,cap,False) for key,unit,cap in [('recovery',tr('分'),100),('sleep_hours',tr('小时'),None),('hrv_ms','ms',None),('resting_hr','bpm',None)]]
    series += [(provider_labels().get(p,p)+tr(' · 每日收听'),[(r['date'],r['seconds']/60) for r in rows if numeric(r.get('seconds'))],COLORS['music'],tr('分钟'),None,True) for p,rows in music.items()]
    dates=[dt.date.fromisoformat(d) for _,points,*_ in series for d,v in points if numeric(v)]
    last=max(dates) if dates else dt.date.today();panels=[]
    for window in ['30','7','all']:
        tiles=[]
        for label,points,color,unit,cap,bar in series:
            points=[(d,v) for d,v in points if window=='all' or 0<=(last-dt.date.fromisoformat(d)).days<int(window)]
            table=''.join('<tr><td>'+esc(d)+'</td><td>'+esc(fmt(v,2))+' '+unit+'</td></tr>' for d,v in sorted(points) if numeric(v))
            tiles.append('<article class="chart"><div class="chart-label">'+esc(label)+'<span>'+str(sum(numeric(v) for _,v in points))+tr(' 次观测 · ')+unit+'</span></div>'+chart(points,color,unit,cap,bar)+tr('<details><summary>查看日期与数值</summary><table>')+table+'</table></details></article>')
        panels.append('<div class="trend-grid" data-window="'+window+'"'+(' hidden' if window!='30' else '')+'>'+''.join(tiles)+'</div>')
    return ''.join(panels)
def render(data,interpretation='',insights=None,share_file='share.svg',lang='auto',media=None):
    language=activate(lang)
    info=insights or overview(data,interpretation)
    title=str(info.get('headline',tr('读懂自己的节奏。')));summary=str(info.get('summary',''))
    h=data.get('healthMetrics',{});recovery=h.get('recovery',{});latest=recovery.get('latest') or {};value=latest.get('value');health=data.get('healthDaily',[])
    a=data.get('associations',[]);primary=next((v for v in a if v.get('outcome')=='recovery'),a[0] if a else {})
    pairs=primary.get('n',0);required=primary.get('required_n',21);enough=primary.get('status')=='exploratory_only'
    findings=''.join('<article class="insight"><span class="insight-num">INSIGHT / 0'+str(i+1)+'</span><h3>'+esc(f.get('title',''))+'</h3><p>'+esc(f.get('detail',''))+'</p><small>'+esc(f.get('evidence',''))+'</small></article>' for i,f in enumerate(info.get('findings',[])[:3]))
    metrics=[]
    for key,unit in [('recovery',tr('分')),('sleep_hours','h'),('hrv_ms','ms'),('resting_hr','bpm')]:
        metric=h.get(key,{}) or {};v=(metric.get('latest') or {}).get('value');mean=metric.get('mean');delta=v-mean if numeric(v) and numeric(mean) else None
        compare=('+' if delta is not None and delta>0 else '')+fmt(delta,2)
        points=[(r['date'],r.get(key)) for r in health]
        metrics.append('<article class="metric" style="--accent:'+COLORS[key]+'"><div class="metric-label"><i></i>'+labels()[key]+'</div><div class="value">'+esc(fmt(v,2 if key in ['sleep_hours','hrv_ms'] else 0))+'<small>'+unit+tr('</small></div><div class="comparison">观测均值 ')+esc(fmt(mean,2))+' '+unit+' · n='+esc(metric.get('n',0))+tr('<br><b>最近值差 ')+esc(compare)+' '+unit+'</b></div>'+chart(points,COLORS[key],unit,100 if key=='recovery' else None,mini=True)+'</article>')
    providers=[]
    for p,cn in provider_labels().items():
        c=data.get('musicCoverage',{}).get(p,{});available=data.get('providerAvailability',{}).get(p)=='available'
        description=(' → '.join(c.get('range') or [])+' · '+str(c.get('days',0))+tr(' 天')) if c else (tr('红心偏好，不代表实际收听') if available else tr('未取得个人授权数据'))
        if p=='spotify' and c: description+=tr(' · 按播放结束日统计，不自动关联健康')
        total=('<strong>'+esc(fmt(c.get('mean_minutes')))+tr('<small> 分钟/日</small></strong>')) if c else '<strong class="unavailable">'+(tr('偏好快照') if available else tr('尚未连接'))+'</strong>'
        providers.append('<div class="provider"><span class="provider-icon">'+{'kugou':'KG','qqmusic':'QQ','netease':'NC','spotify':'SP'}[p]+'</span><div><b>'+cn+'</b><p>'+esc(description)+'</p></div>'+total+'</div>')
    associations=[]
    for row in a:
        state={'insufficient_data':tr('样本不足，不推断方向'),'exploratory_only':tr('仅探索，不代表因果'),'no_variation':tr('数据缺少变化')}.get(row.get('status'),tr('暂无结论'))
        associations.append('<tr><td>'+esc(provider_labels().get(row.get('provider'),row.get('provider')))+'</td><td>'+esc(labels().get(row.get('outcome'),row.get('outcome')))+'</td><td>'+esc(row.get('n'))+'</td><td>'+esc(fmt(row.get('spearman_r'),3))+'</td><td><span class="status">'+esc(state)+'</span></td></tr>')
    cov=data.get('musicCoverage',{});p=primary.get('provider') or next(iter(cov),None);music=cov.get(p,{})
    steps=''.join('<article class="next-card"><span class="next-num">'+str(i+1)+'</span><div><h3>'+esc(s.get('title',''))+'</h3><p>'+esc(s.get('detail',''))+'</p></div></article>' for i,s in enumerate(info.get('next_steps',[])[:2]))
    script=(ASSETS/'report.js').read_text();css=(ASSETS/'report.css').read_text()
    from music_story_html import render as music_render
    from rhythm_html import render as rhythm_render
    css+='\n'+(ASSETS/'music-story.css').read_text()+'\n'+(ASSETS/'rhythm.css').read_text()
    tokens={'rhythm':rhythm_render(data,info,media),'brand_icon':'data:image/svg+xml;base64,'+base64.b64encode((ASSETS/'brand/icon.svg').read_bytes()).decode(),'favicon':'data:image/svg+xml;base64,'+base64.b64encode((ASSETS/'brand/favicon.svg').read_bytes()).decode(),'music_story':music_render(data,info,media),'language':language,'title':esc(title),'summary':esc(summary),'edition':esc(str(data.get('generatedAt',''))[:10]),'range':esc(' — '.join(recovery.get('range') or [])),'health_n':esc(recovery.get('n',0)),'music_n':esc(music.get('days',0)),'music_provider':esc(provider_labels().get(p,tr('未连接平台'))),'ring':ring(value,recovery.get('mean')),'recovery':esc(fmt(value,0)),'latest_date':esc(latest.get('date')),'recovery_mean':esc(fmt(recovery.get('mean'))),'findings':findings,'metrics':''.join(metrics),'charts':series_panels(data),'association_title':tr('有可探索的共同变化。') if enough else tr('先积累证据，再谈关联。'),'pairs':esc(pairs),'required':esc(required),'dots':''.join('<i'+(' class="filled"' if i<min(21,pairs*21/max(1,required)) else '')+'></i>' for i in range(21)),'association_summary':esc(f"{provider_labels().get(p, tr('音乐'))}{tr('与次日恢复有 ')}{pairs}{tr(' 对可对齐记录。')}"+(tr('当前系数仍需结合时间分段稳定性与混杂因素解释。') if enough else tr('本轮不据此判断音乐改善或妨碍恢复。'))),'providers':''.join(providers),'associations':''.join(associations),'next_steps':steps,'narrative':markdown(interpretation),'warnings':''.join('<li>'+esc(w)+'</li>' for w in data.get('warnings',[])),'failure_count':str(len(data.get('collectionFailures',[]))),'failures':esc(json.dumps(data.get('collectionFailures',[]),ensure_ascii=False)),'exported':esc(data.get('sourceExportedAt')),'generated':esc(data.get('generatedAt')),'source_hash':esc(data.get('sourceFileSha256')),'share_file':esc(share_file),'script':script,'script_hash':base64.b64encode(hashlib.sha256(script.encode()).digest()).decode(),'css':css}
    return re.sub(r'\{\{(\w+)\}\}',lambda m:tokens[m[1]],tr((ASSETS/'report.html').read_text()).replace('lang="zh-CN"','lang="'+language+'"'))
def share_card(data,info,lang='auto'):
    activate(lang)
    # Only selected summary fields: no raw records, identity, source hashes or file paths.
    title=str(info.get('headline',tr('读懂自己的节奏。')));lines=__import__('textwrap').wrap(title,width=29 if resolve(lang)=='en' else 17)[:4]
    title_svg=''.join(f'<text x="72" y="{190+i*65}" fill="#f5f7ef" font-size="45" font-weight="600">{esc(line)}</text>' for i,line in enumerate(lines))
    cards=[]
    for i,(key,label) in enumerate([('recovery',tr('恢复分数')),('sleep_hours',tr('主睡眠 · h')),('hrv_ms','HRV · ms')]):
        v=((data.get('healthMetrics',{}).get(key) or {}).get('latest') or {}).get('value')
        x=72+i*243;cards.append(f'<text x="{x}" y="515" fill="#a8b3a7" font-size="17">{label}</text><text x="{x}" y="581" fill="#b4ee50" font-size="53">{esc(fmt(v,2 if key!="recovery" else 0))}</text>')
    primary=next((r for r in data.get('associations',[]) if r.get('outcome')=='recovery'),{})
    n=primary.get('n',0);provider=provider_labels().get(primary.get('provider'),tr('音乐'))
    return f"""{tr('<svg xmlns="http://www.w3.org/2000/svg" width="900" height="780" viewBox="0 0 900 780" role="img"><title>PulseBeat 个人分享摘要</title><rect width="900" height="780" rx="38" fill="#141b1b"/><circle cx="895" cy="70" r="180" fill="none" stroke="#34412d"/><g font-family="Avenir Next, PingFang SC, sans-serif"><svg x="72" y="48" width="40" height="40" viewBox="0 0 32 32"><rect width="32" height="32" rx="7" fill="#26312c"/><path d="M9 26V14a7 7 0 1 1 7 7h-3" fill="none" stroke="#b4ee50" stroke-width="3.5" stroke-linecap="round"/><circle cx="16" cy="14" r="1.8" fill="#e47a42"/></svg><text x="124" y="82" fill="#c3d1b7" font-size="25" font-weight="700">pulsebeat.</text><text x="72" y="120" fill="#879782" font-size="12">MY RHYTHM / ')}{esc(str(data.get('generatedAt', ''))[:10])}</text>{title_svg}<line x1="72" y1="455" x2="828" y2="455" stroke="#344237"/>{''.join(cards)}<text x="72" y="669" fill="#b0baad" font-size="17">{esc(provider)}{tr('与次日恢复 · ')}{n}{tr(' 对配对 · 个人观察不代表因果</text><text x="72" y="713" fill="#788675" font-size="13">精选摘要，不含身份资料或原始记录。不是医疗诊断。</text></g></svg>')}"""
def build(args):
    language=activate(getattr(args,'lang','auto'))
    source=pathlib.Path(args.analysis);data=json.loads(source.read_text(encoding='utf-8'))
    if not args.interpretation:raise ValueError('AI interpretation is required before final HTML generation')
    note=pathlib.Path(args.interpretation).read_text(encoding='utf-8')
    if not note.strip():raise ValueError('AI interpretation cannot be empty')
    info=json.loads(pathlib.Path(args.insights).read_text()) if getattr(args,'insights',None) else overview(data,note)
    if info.get('language') and resolve(info['language'])!=language: raise ValueError('Interpretation language mismatch; ask the Agent to rewrite insights and narrative in the selected language')
    out=pathlib.Path(args.out);out.parent.mkdir(parents=True,exist_ok=True);share=out.with_name(out.stem+'-share.svg')
    share.write_text(share_card(data,info,language),encoding='utf-8');os.chmod(share,0o600)
    out.write_text(render(data,note,info,share.name,language,json.loads(pathlib.Path(args.media).read_text()) if getattr(args,'media',None) else None),encoding='utf-8');os.chmod(out,0o600)
    manifest={'language':language,'template':'pulsebeat-integrated-v4','analysisSha256':hashlib.sha256(source.read_bytes()).hexdigest(),'interpretationSha256':hashlib.sha256(note.encode()).hexdigest(),'htmlSha256':hashlib.sha256(out.read_bytes()).hexdigest(),'containsAgentInterpretation':True,'shareFile':share.name}
    if getattr(args,'insights',None):manifest['insightsSha256']=hashlib.sha256(pathlib.Path(args.insights).read_bytes()).hexdigest()
    if getattr(args,'media',None):manifest['mediaSha256']=hashlib.sha256(pathlib.Path(args.media).read_bytes()).hexdigest()
    from pulsebeat import save
    save(out.with_suffix('.manifest.json'),manifest);print('HTML: '+str(out.resolve()));print('Share card: '+str(share.resolve()))
