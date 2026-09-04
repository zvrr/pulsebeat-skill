"""Evidence-preserving listening portraits; no network or inferred personal scenes."""
import collections, datetime as dt, math, re, statistics

def number(v):return isinstance(v,(int,float)) and not isinstance(v,bool) and math.isfinite(v) and v>=0

def portrait(export,qq=(),netease=None,spotify=None):
    result={};sources=export.get('sources',{})
    # Latest successful daily snapshot wins. Never add overlapping cached exports.
    daily={}
    for entry in sources.get('music:stats',[]):
        response=entry.get('response') or {};data=response.get('data')
        if entry.get('dateType')!=0 or response.get('errcode')!=0 or not isinstance(data,dict):continue
        try:day=dt.datetime.strptime(entry['date'],'%Y%m%d').date().isoformat()
        except (ValueError,KeyError,TypeError):continue
        if not number(data.get('listen_duration')):continue
        if day not in daily or str(entry.get('collectedAt',''))>=str(daily[day].get('collectedAt','')):daily[day]=entry
    if daily:
        tracks={};genres=collections.Counter();languages=collections.Counter();clocks=[];days=[];ranked=0
        for day,entry in sorted(daily.items()):
            data=entry['response']['data'];days.append({'date':day,'seconds':data['listen_duration'],'plays':data.get('listen_total') if number(data.get('listen_total')) else None})
            ranks=data.get('rank_song') or [];ranked+=bool(ranks);seen=set()
            for row in ranks:
                info=row.get('song_info') or {};title=info.get('song_name') or info.get('name');artist=info.get('artist_name') or info.get('singer_name');count=row.get('count')
                if not title or not number(count):continue
                key=str(info.get('mix_song_id') or str(title)+'|'+str(artist))
                if key in seen:continue
                seen.add(key);track=tracks.setdefault(key,{'id':key,'title':title,'artist':artist or '', 'observedPlays':0,'dates':[],'coverUrl':info.get('cover'),'sourceUrl':info.get('play_link')})
                track['observedPlays']+=count;track['dates'].append(day)
                if info.get('cover'):track['coverUrl']=info['cover']
            # Upstream category counts can overlap and have unclear units: count presence by day only.
            genres.update({str(r['style']) for r in data.get('rank_style') or [] if r.get('style')})
            languages.update({str(r['language']) for r in data.get('rank_language') or [] if r.get('language')})
            seen_slots=set()
            for raw in data.get('top_clocks') or []:
                m=re.fullmatch(r'今日(\d{2}):00-(\d{2}):00听歌(\d+(?:\.\d+)?)分钟',str(raw))
                if not m:continue
                start,end,value=int(m[1]),int(m[2]),float(m[3])
                if not 0<=start<end<=24 or (start,end) in seen_slots:continue
                seen_slots.add((start,end));clocks.append({'date':day,'start':start,'end':end,'minutes':value})
        result['kugou']=finish(days,tracks,'daily_top_list',ranked,genres,languages,clocks)
    qq_days={}
    for report in qq:
        if report.get('source')!='qqmusic' or report.get('timeKey')!='d':continue
        response=report.get('response') or {}
        if any(response.get(k,0) not in (0,None) for k in ['ret','sub_ret']):continue
        data=response.get('dayData') or {}
        try:day=dt.date.fromisoformat(report.get('date','')).isoformat()
        except (TypeError,ValueError):continue
        if not number(data.get('listenTime')):continue
        if day not in qq_days or str(report.get('collectedAt',''))>=str(qq_days[day].get('collectedAt','')):qq_days[day]=report
    if qq_days:
        days=[];tracks={};ranked=0
        for day,report in sorted(qq_days.items()):
            data=report['response']['dayData'];days.append({'date':day,'seconds':data['listenTime'],'plays':None});rows=data.get('songListen') or [];ranked+=bool(rows);seen=set()
            for row in rows:
                title=row.get('songName');count=row.get('sum');key=str(row.get('songMid') or title or '')
                if not title or not number(count) or key in seen:continue
                seen.add(key);track=tracks.setdefault(key,{'id':key,'title':title,'artist':row.get('singerName') or '', 'observedPlays':0,'dates':[]})
                track['observedPlays']+=count;track['dates'].append(day)
        result['qqmusic']=finish(days,tracks,'daily_top_list',ranked,{},{},[])
    # Spotify: full supplied export observations, not a complete account history claim.
    if spotify:
        tracks={};days={}
        for row in spotify.get('records',[]):
            key=row.get('uri');date=row.get('date');value=row.get('seconds')
            if not key or not date or not number(value):continue
            track=tracks.setdefault(key,{'id':key,'title':row.get('track',''),'artist':row.get('artist',''),'observedPlays':0,'dates':[],'seconds':0})
            track['observedPlays']+=1;track['seconds']+=value;track['dates'].append(date)
            day=days.setdefault(date,{'date':date,'seconds':0,'plays':0});day['seconds']+=value;day['plays']+=1
        if days:result['spotify']=finish(list(days.values()),tracks,'export_events',len(days),{},{},[])
    if netease and netease.get('songs'):
        result['netease']={'basis':'favorites_only','tracks':[{'id':str(x.get('id','')),'title':x.get('name',''),'artist':' / '.join(x.get('artists') or []),'dates':[]} for x in netease['songs'][:12]],'daily':[]}
    return result

def finish(days,tracks,basis,ranked,genres,languages,clocks):
    days=sorted(days,key=lambda x:x['date']);values=[x['seconds']/60 for x in days];active=[x for x in days if x['seconds']>0]
    streak=best=0;last=None
    for row in days:
        day=dt.date.fromisoformat(row['date']);streak=(streak+1 if last and (day-last).days==1 else 1) if row['seconds']>0 else 0;best=max(best,streak);last=day
    week=[]
    for weekday in range(7):
        sample=[x['seconds']/60 for x in days if dt.date.fromisoformat(x['date']).weekday()==weekday]
        week.append({'weekday':weekday,'n':len(sample),'meanMinutes':round(statistics.mean(sample),2) if sample else None})
    top=sorted(tracks.values(),key=lambda x:(-x['observedPlays'],x['title']))
    for track in top:track['listedDays']=len(set(track['dates']));track['dates']=sorted(set(track['dates']))
    return {'basis':basis,'daily':days,'tracks':top[:12],'rankedDays':ranked,'distinctListedTracks':len(tracks),'genreDays':[{'name':k,'days':v} for k,v in sorted(genres.items(),key=lambda x:-x[1])],'languageDays':[{'name':k,'days':v} for k,v in sorted(languages.items(),key=lambda x:-x[1])],'clockRows':clocks,'weekdays':week,'summary':{'observedDays':len(days),'activeDays':len(active),'zeroDays':len(days)-len(active),'totalMinutes':round(sum(values),1),'medianMinutes':round(statistics.median(values),1),'longestObservedStreak':best,'peak':max(days,key=lambda x:x['seconds']) if days else None,'range':[days[0]['date'],days[-1]['date']]}}
