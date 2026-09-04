#!/usr/bin/env python3
"""PulseBeat local client. Python standard library only; never calls an LLM."""
import argparse, datetime as dt, hashlib, json, math, os, pathlib, statistics, sys, tempfile, time, urllib.request, urllib.error, urllib.parse, webbrowser
ORIGIN = 'https://pulsebeat.tennisflow.top'
HOME = pathlib.Path(os.environ.get('PULSEBEAT_HOME', str(pathlib.Path.home()/'.config'/'pulsebeat')))
KINDS = ['cycle','recovery','sleep','workout','music:stats','music:favorites','music:recent']
TZ = dt.timezone(dt.timedelta(hours=8))

def now(): return dt.datetime.now(dt.timezone.utc).isoformat()
def save(path, value):
    path=pathlib.Path(path); path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(mode='w',encoding='utf-8',dir=path.parent,delete=False) as f:
        os.chmod(f.name,0o600); json.dump(value,f,ensure_ascii=False,indent=2,allow_nan=False); name=f.name
    os.replace(name,path)
def read(path): return json.loads(pathlib.Path(path).read_text(encoding='utf-8'))
class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self,req,fp,code,msg,headers,newurl): return None

def request(origin,path,body=None,token=None):
    # No arbitrary host override, no redirects carrying bearer credentials.
    if origin not in (ORIGIN,'https://a.y.qq.com'): raise ValueError('Untrusted service origin')
    headers={'User-Agent':'PulseBeat-Skill/1.0','Content-Type':'application/json'}
    if token: headers['Authorization']='Bearer '+token
    req=urllib.request.Request(origin+path,data=None if body is None else json.dumps(body).encode(),headers=headers)
    try:
        with urllib.request.build_opener(NoRedirect).open(req,timeout=45) as r:
            raw=r.read(20_000_001)
            if len(raw)>20_000_000: raise ValueError('Response too large')
            return r.status,json.loads(raw)
    except urllib.error.HTTPError as e:
        return e.code,{'error':{401:'authorization_required',403:'access_denied',429:'slow_down'}.get(e.code,'request_failed')}

def credential():
    c=read(HOME/'credential.json')
    if c.get('origin')!=ORIGIN or not c.get('token','').startswith('pbr_'): raise ValueError('Invalid personal read credential')
    if c.get('expires',0)<=time.time()*1000: raise ValueError('Authorization expired; run auth-start')
    return c

def auth_start(args):
    status,pair=request(ORIGIN,'/api/agent/device',{'label':args.label})
    if status!=200: raise ValueError(f'Authorization start: HTTP {status}')
    pair['started_at']=time.time();save(HOME/'pending.json',pair)
    url=ORIGIN+'/agent.html#code='+urllib.parse.quote(pair['user_code'])
    print('确认码：'+pair['user_code']);print('请在浏览器核对账号和读取范围后批准：'+url)
    if args.open: webbrowser.open(url)

def auth_complete(args):
    pair=read(HOME/'pending.json')
    if time.time()-pair['started_at']>600: raise ValueError('Pairing expired; run auth-start again')
    status,result=request(ORIGIN,'/api/agent/token',{'device_code':pair['device_code']})
    if status==202: print('等待用户在 PulseBeat 网页批准。至少 5 秒后再运行 auth-complete。');return
    if status!=200: raise ValueError(f'Authorization incomplete: HTTP {status}; retry after 5 seconds for 429')
    save(HOME/'credential.json',result);(HOME/'pending.json').unlink(missing_ok=True)
    print('已保存个人只读授权，凭证未输出。到期：'+dt.datetime.fromtimestamp(result['expires']/1000,TZ).isoformat())

def status_command(args):
    valid=False
    try: credential();valid=True
    except (OSError,ValueError,KeyError): pass
    print(json.dumps({'local_credential_valid':valid,'credential_path':str(HOME/'credential.json'),'qq_key_configured':bool(os.environ.get('QQMUSIC_API_KEY'))}))

def fetch_data(args):
    c=credential();result={'schema':'pulsebeat.export.v1','exportedAt':now(),'origin':ORIGIN,'sources':{}}
    start,status=request(ORIGIN,'/api/status',token=c['token'])
    if start!=200: raise ValueError(f'Fetch status: HTTP {start}')
    result['status']=status
    for kind in KINDS:
        rows=[];cursor='';seen=set()
        for _ in range(1000):
            code,page=request(ORIGIN,'/api/records?'+urllib.parse.urlencode({'kind':kind,'cursor':cursor}),token=c['token'])
            if code!=200 or not isinstance(page.get('records'),list): raise ValueError(f'{kind}: HTTP {code}; no complete export saved')
            rows.extend(page['records']);cursor=page.get('next')
            if not cursor: break
            if cursor in seen: raise ValueError('Repeated pagination cursor')
            seen.add(cursor)
        else: raise ValueError('Pagination limit; export incomplete')
        result['sources'][kind]=rows
    result['fetchCompletedAt']=now();result['consistency']='逐类分页导出，非跨接口事务快照；同步进行中时可能变化'
    save(args.out,result);print('Saved: '+str(args.out));print(json.dumps({k:len(v) for k,v in result['sources'].items()}))

def qq_collect(args):
    key=os.environ.get('QQMUSIC_API_KEY')
    if not key: raise ValueError('QQMUSIC_API_KEY 未设置；在 QQ 官方技能授权页配置，不要在对话中粘贴密钥')
    date=dt.date.fromisoformat(args.date)
    if date>=dt.datetime.now(TZ).date(): raise ValueError('Choose a completed day, before today')
    params={'timeKey':'d','startTime':int(dt.datetime.combine(date,dt.time(),TZ).timestamp())}
    status,response=request('https://a.y.qq.com','/me/report',{'params':params,'comm':{'skill_version':'0.0.3'}},key)
    if status!=200 or any(response.get(k,0) not in (0,None) for k in ['ret','sub_ret']): raise ValueError(f'QQ report unavailable: HTTP {status}')
    save(args.out,{'source':'qqmusic','collectedAt':now(),'date':args.date,'timeKey':'d','timezone':'+08:00','timezoneVerified':args.confirm_beijing_day,'params':params,'response':response})
    print('Saved QQ daily report: '+str(args.out))

def num(x): return isinstance(x,(int,float)) and not isinstance(x,bool) and math.isfinite(x)
def safe_score(row): return row.get('score',{}) if row.get('score_state')=='SCORED' else {}
def ranks(xs):
    ordered=sorted(xs);return [(ordered.index(x)+len(ordered)-ordered[::-1].index(x)+1)/2 for x in xs]
def corr(x,y):
    if len(x)<2 or len(set(x))<2 or len(set(y))<2: return None
    return statistics.correlation(ranks(x),ranks(y))
def day_at(iso,offset):
    if not isinstance(offset,str) or len(offset)!=6 or offset[0] not in '+-' or offset[3]!=':': return None
    try:
        minutes=(int(offset[1:3])*60+int(offset[4:]))*(1 if offset[0]=='+' else -1)
        return dt.datetime.fromisoformat(iso.replace('Z','+00:00')).astimezone(dt.timezone(dt.timedelta(minutes=minutes))).date().isoformat()
    except (ValueError,TypeError,AttributeError): return None

def analyze(export, qq_reports=(), netease=None):
    sources=export.get('sources',{});warnings=[];health={};music={};preferences={}
    sleeps={str(s.get('id')):s for s in sources.get('sleep',[]) if not s.get('nap')}
    cycles={str(c.get('id')):c for c in sources.get('cycle',[])}
    # Recovery belongs to main sleep's awakening day. Never pair by cycle start day.
    for r in sources.get('recovery',[]):
        sleep=sleeps.get(str(r.get('sleep_id')));score=safe_score(r)
        if not sleep or score.get('user_calibrating'): continue
        offset=sleep.get('timezone_offset');day=day_at(sleep.get('end'),offset)
        if not day: warnings.append('有恢复记录缺少主睡眠结束时间或明确时区，未参与按日关联');continue
        stages=safe_score(sleep).get('stage_summary',{})
        parts=[stages.get(k) for k in ['total_light_sleep_time_milli','total_slow_wave_sleep_time_milli','total_rem_sleep_time_milli']]
        row={'date':day,'timezone':offset,'recovery':score.get('recovery_score'),'hrv_ms':score.get('hrv_rmssd_milli'),'resting_hr':score.get('resting_heart_rate'),'sleep_hours':sum(parts)/3600000 if all(num(x) and x>=0 for x in parts) else None,'cycle_strain':safe_score(cycles.get(str(r.get('cycle_id')),{})).get('strain')}
        if day in health: health[day]=None;warnings.append('同一天存在多个恢复记录，排除该日关联以避免任意选择')
        else: health[day]=row
    health={d:r for d,r in health.items() if r}
    for entry in sources.get('music:stats',[]):
        value=entry.get('response',{}).get('data',{}).get('listen_duration')
        if entry.get('dateType')!=0 or not num(value) or value<0: continue
        try: day=dt.datetime.strptime(entry['date'],'%Y%m%d').date().isoformat()
        except (KeyError,ValueError,TypeError): continue
        music.setdefault('kugou',{})[day]={'seconds':value,'timezone':'+08:00','verified':True}
    for kind in ['favorites','recent']:
        entries=sources.get('music:'+kind,[])
        if entries:
            songs=entries[-1].get('response',{}).get('data',{}).get('list',[])
            preferences['kugou_'+kind]=[{'song':s.get('song_name'),'artist':s.get('artist_name')} for s in songs[:10]]
    for report in qq_reports:
        if report.get('source')!='qqmusic' or report.get('timeKey')!='d': warnings.append('QQ 非日报仅用于偏好解读，不参与日关联');continue
        resp=report.get('response',{});value=(resp.get('dayData') or {}).get('listenTime')
        if any(resp.get(k,0) not in (0,None) for k in ['ret','sub_ret']) or not num(value) or value<0: continue
        day=dt.date.fromisoformat(report['date']).isoformat()
        music.setdefault('qqmusic',{})[day]={'seconds':value,'timezone':report.get('timezone'),'verified':report.get('timezoneVerified') is True}
        preferences['qqmusic_top_songs']=(resp.get('dayData') or {}).get('songListen',[])[:10]
    if netease:
        if netease.get('source')!='netease' or netease.get('evidenceType')!='favorites' or not isinstance(netease.get('songs'),list): raise ValueError('NetEase export must follow references/providers.md favorites schema')
        preferences['netease_favorites']=netease['songs'][:50]
        warnings.append('网易云为红心偏好快照；收藏时间与曲目长度不是实际收听时间或时长，不参与健康日关联')
    metrics={}
    for metric in ['recovery','hrv_ms','resting_hr','sleep_hours','cycle_strain']:
        pairs=[(day,row[metric]) for day,row in sorted(health.items()) if num(row[metric])]
        values=[v for _,v in pairs]
        metrics[metric]={'n':len(values),'mean':round(statistics.mean(values),3) if values else None,'latest':{'date':pairs[-1][0],'value':pairs[-1][1]} if pairs else None,'range':[pairs[0][0],pairs[-1][0]] if pairs else None}
        if len(pairs)>=14:
            last=dt.date.fromisoformat(pairs[-1][0]);recent=[v for d,v in pairs if 0<=(last-dt.date.fromisoformat(d)).days<7];previous=[v for d,v in pairs if 7<=(last-dt.date.fromisoformat(d)).days<14]
            if len(recent)>=5 and len(previous)>=5: metrics[metric]['change_recent7_vs_previous7']=round(statistics.mean(recent)-statistics.mean(previous),3)
    associations=[];today=dt.datetime.now(TZ).date().isoformat()
    for provider,days in music.items():
        for metric in ['recovery','hrv_ms','sleep_hours']:
            pairs=[]
            for date,row in sorted(health.items()):
                previous=(dt.date.fromisoformat(date)-dt.timedelta(days=1)).isoformat();m=days.get(previous)
                if m and m['verified'] and m['timezone']==row['timezone']=='+08:00' and previous<today and num(row[metric]): pairs.append((m['seconds']/60,row[metric],previous,date))
            n=len(pairs);result={'provider':provider,'exposure':'前一自然日听歌分钟','outcome':metric,'n':n,'required_n':21,'status':'insufficient_data','spearman_r':None,'paired_dates':[{'music':p[2],'health':p[3]} for p in pairs]}
            if n>=21:
                r=corr([p[0] for p in pairs],[p[1] for p in pairs]);result['spearman_r']=round(r,3) if r is not None else None;result['status']='exploratory_only' if r is not None else 'no_variation'
                halves=[pairs[:n//2],pairs[n//2:]];result['split_half_r']=[None if (v:=corr([p[0] for p in part],[p[1] for p in part])) is None else round(v,3) for part in halves]
            associations.append(result)
    warnings.extend(['仅为个人可穿戴与音乐记录描述，不用于诊断；相关不代表音乐导致恢复改变。','前一日音乐与醒来后的恢复配对；日统计仍无法证明音乐发生在睡前，不能识别具体曲目影响。','21 对只是产品最低展示门槛，并非统计显著性；时间自相关、训练、作息、饮酒、压力、旅行等未受控制，多个指标属于探索。','不把不同平台时长相加；缺失不填零，收藏/推荐不能当收听记录。','本地脚本不调用模型。Agent 撰写解读可能使用平台云模型；只读此汇总，不自动读取原始导出。'])
    coverage={p:{'days':len(days),'range':[min(days),max(days)] if days else None,'mean_minutes':round(statistics.mean(x['seconds']/60 for x in days.values()),2) if days else None,'timezone_verified':all(x['verified'] for x in days.values())} for p,days in music.items()}
    return {'schema':'pulsebeat.analysis.v1','generatedAt':now(),'sourceExportedAt':export.get('exportedAt'),'collectionFailures':export.get('localKugouFailures',export.get('status',{}).get('music',{}).get('failures',[]) if export.get('status',{}).get('music') else []),'sourceCounts':{k:len(v) for k,v in sources.items()},'healthMetrics':metrics,'healthDaily':list(health.values()),'musicDaily':{p:[{'date':d,**row} for d,row in sorted(days.items())] for p,days in music.items()},'musicCoverage':coverage,'providerAvailability':{p:('available' if p in music or (p=='netease' and netease) else 'not_connected_or_no_data') for p in ['kugou','qqmusic','netease']},'preferences':preferences,'associations':associations,'warnings':list(dict.fromkeys(warnings))}

def analyze_command(args):
    source=read(args.input)
    if args.kugou:
        local=read(args.kugou)
        for kind,entries in local.get('sources',{}).items():
            if kind.startswith('music:'): source.setdefault('sources',{})[kind]=entries
        source['localKugouFailures']=local.get('failures',[])
    result=analyze(source,[read(p) for p in args.qq],read(args.netease) if args.netease else None)
    result['sourceFileSha256']=hashlib.sha256(pathlib.Path(args.input).read_bytes()).hexdigest()
    result['supplementalFileSha256']={str(p):hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest() for p in [*args.qq,args.netease,args.kugou] if p}
    out=pathlib.Path(args.out);save(out/'analysis.json',result)
    labels={'recovery':'恢复分数','hrv_ms':'HRV（ms）','resting_hr':'静息心率','sleep_hours':'主睡眠小时','cycle_strain':'周期负荷'}
    lines=['# PulseBeat 本地分析底稿','',f"生成：{result['generatedAt']}；数据导出：{result['sourceExportedAt']}",'','这是确定性统计底稿。AI 解读由 Agent 基于 analysis.json 另写 interpretation.md。','','| 指标 | 有效样本 | 均值 | 最新观测 |','|---|---:|---:|---|']
    for k,v in result['healthMetrics'].items(): lines.append(f"| {labels[k]} | {v['n']} | {v['mean'] if v['mean'] is not None else '缺失'} | {v['latest'] or '缺失'} |")
    lines+=['','## 音乐覆盖']
    for p,v in result['providerAvailability'].items(): lines.append(f'- {p}: {v}；{result["musicCoverage"].get(p,{})}')
    lines+=['','## 可检验的关联']
    for a in result['associations']: lines.append(f"- {a['provider']} 前一日音乐 → {labels[a['outcome']]}：{a['n']} 对，{a['status']}，Spearman={a['spearman_r']}。")
    lines+=['','## 解释边界']+['- '+w for w in result['warnings']]
    (out/'report.md').write_text('\n'.join(lines)+'\n',encoding='utf-8');os.chmod(out/'report.md',0o600)
    print('Local analysis: '+str(out/'analysis.json'));print('Statistics report: '+str(out/'report.md'))

def sync_command(args):
    from local_sync import sync
    return sync(args)

def html_command(args):
    from report_html import build
    return build(args)

def main():
    os.umask(0o077)
    p=argparse.ArgumentParser(description=__doc__);sub=p.add_subparsers(dest='command',required=True)
    a=sub.add_parser('auth-start');a.add_argument('--label',default='Local Agent');a.add_argument('--open',action='store_true');a.set_defaults(fn=auth_start)
    a=sub.add_parser('auth-complete');a.set_defaults(fn=auth_complete)
    a=sub.add_parser('status');a.set_defaults(fn=status_command)
    a=sub.add_parser('fetch');a.add_argument('--out',type=pathlib.Path,required=True);a.set_defaults(fn=fetch_data)
    a=sub.add_parser('qq-report');a.add_argument('--date',required=True);a.add_argument('--out',type=pathlib.Path,required=True);a.add_argument('--confirm-beijing-day',action='store_true',help='Only after the user/provider confirms daily timezone');a.set_defaults(fn=qq_collect)
    a=sub.add_parser('analyze');a.add_argument('--input',required=True);a.add_argument('--out',required=True);a.add_argument('--qq',nargs='*',default=[]);a.add_argument('--netease');a.add_argument('--kugou');a.set_defaults(fn=analyze_command)
    a=sub.add_parser('sync');a.add_argument('--directory',required=True);a.add_argument('--days',type=int,choices=range(1,31),default=7);group=a.add_mutually_exclusive_group();group.add_argument('--refresh-kugou',action='store_true');group.add_argument('--kugou-file');a.add_argument('--qq',nargs='*',default=[]);a.add_argument('--netease');a.set_defaults(fn=sync_command)
    a=sub.add_parser('html');a.add_argument('--analysis',required=True);a.add_argument('--interpretation',required=True);a.add_argument('--insights');a.add_argument('--out',required=True);a.set_defaults(fn=html_command)
    args=p.parse_args()
    try: args.fn(args)
    except (ValueError,KeyError,OSError,urllib.error.URLError) as e:
        print('PulseBeat: '+(str(e) if isinstance(e,ValueError) else type(e).__name__+'; check local configuration or network'),file=sys.stderr);sys.exit(1)
if __name__=='__main__': main()
