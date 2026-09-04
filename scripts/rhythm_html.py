"""Combined listening / next-day health story, using verified analysis pairs only."""
from music_story_html import L,esc,f,artwork

def render(data,info,media=None):
    blocks=[];health={r['date']:r for r in data.get('healthDaily',[])}
    for a in data.get('associations',[]):
        if a.get('outcome')!='recovery':continue
        provider=a['provider'];music={r['date']:r for r in data.get('musicDaily',{}).get(provider,[])}
        pairs=a.get('paired_dates',[]);cards=[]
        portrait=data.get('musicPortraits',{}).get(provider,{})
        for pair in sorted(pairs,key=lambda p:p['health'])[-7:]:
            h=health.get(pair['health']);m=music.get(pair['music'])
            if not h or not m:continue
            tracks=[t for t in portrait.get('tracks',[]) if pair['music'] in t.get('dates',[])][:3]
            covers=[]
            for i,t in enumerate(tracks):
                item=(media or {}).get('items',{}).get(provider+':'+t['id'],{})
                if item.get('title')!=t['title'] or item.get('artist')!=t.get('artist',''):item={}
                covers.append('<div class="rhythm-song">'+artwork(item,t['title'],i)+'<span>'+esc(t['title'])+'<small>'+esc(t.get('artist',''))+'</small></span></div>')
            context=(info.get('rhythmNotes') or {}).get(provider+':'+pair['health'],'')
            music_note=L('本平台返回零时长，不代表全天没有听歌。','Zero reported by this provider; not proof of no listening elsewhere.') if m['seconds']==0 else L('歌曲仅取当前可见日榜，不代表当天完整播放列表。','Songs come from available daily lists, not the complete playlist.')
            cards.append('<article class="rhythm-day"><div class="rhythm-dates"><b>'+esc(pair['music'][5:])+'</b><span>→</span><b>'+esc(pair['health'][5:])+'</b></div><div class="rhythm-values"><div class="sound-value"><small>'+L('当天听歌 · 分钟','Listening · minutes')+'</small><strong>'+f(m['seconds']/60)+'</strong></div><div><small>'+L('次日恢复 · 分','Next-day recovery')+'</small><strong>'+f(h.get('recovery'))+'</strong></div></div><p class="rhythm-sleep">'+L('次日主睡眠','Next-day main sleep')+' <b>'+f(h.get('sleep_hours'))+' h</b> · HRV <b>'+f(h.get('hrv_ms'))+' ms</b></p>'+''.join(covers)+'<p class="rhythm-context">'+esc(context or music_note)+'</p>'+('<small class="rhythm-boundary">'+esc(music_note)+'</small>' if context else '')+'</article>')
        if cards:blocks.append('<div class="rhythm-provider">'+esc(provider.upper())+' × WHOOP · '+str(len(pairs))+L(' 组有效对齐 · 展示最近至多 7 组',' verified pairs · latest 7 at most')+'</div><div class="rhythm-days">'+''.join(cards)+'</div>')
    if not blocks:return '<section class="panel"><h2>'+L('让身体与音乐，在同一段时间里相遇。','Bring body and music into the same window.')+'</h2><p>'+L('目前没有经过时区与日期核对的有效配对。下方保留各自的记录，不拼接成未经验证的生活场景。','No date- and timezone-verified pairs yet. Keep the available records without inventing a shared scene.')+'</p></section>'
    return '<section class="rhythm-section"><div class="section-heading"><div><span class="kicker">01 / ONE LIFE, TWO SIGNALS</span><h2>'+L('白天听见什么，醒来身体如何。','What you heard. How you woke.')+'</h2></div></div><p class="rhythm-intro">'+L('把前一自然日的音乐记录与次日健康观测放在同一页。这里展示时间上的相邻，不把相邻解释为因果；睡眠归属沿用 WHOOP 的观测日。','Previous-calendar-day listening sits beside next-day health. Temporal adjacency is not causation; sleep retains its WHOOP observation date.')+'</p>'+''.join(blocks)+'</section>'
