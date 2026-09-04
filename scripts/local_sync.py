#!/usr/bin/env python3
"""Personal local archive. Uses hosted PulseBeat; never deploys or uploads."""
import argparse, datetime as dt, hashlib, pathlib, subprocess, sys, tempfile
from pulsebeat import fetch_data, credential, read, save, now

def account_ref(export, fallback):
    ids={str(row['user_id']) for kind,rows in export.get('sources',{}).items() if not kind.startswith('music:') for row in rows if row.get('user_id') is not None}
    if len(ids)>1: raise ValueError('Export contains mixed WHOOP identities')
    return hashlib.sha256(('whoop:'+next(iter(ids)) if ids else 'device:'+fallback).encode()).hexdigest()

def stamp(row):
    try: return dt.datetime.fromisoformat(row.get('collectedAt','').replace('Z','+00:00')).timestamp()
    except (ValueError,AttributeError,TypeError): return 0

def merge_music(*exports):
    merged={}
    for export in exports:
        for kind,rows in export.get('sources',{}).items():
            if kind not in ('music:stats','music:favorites','music:recent'): continue
            for row in rows:
                response=row.get('response',{})
                if response.get('errcode')!=0 or not isinstance(response.get('data'),dict): continue
                key=(row.get('dateType'),row.get('date')) if kind=='music:stats' else ('latest',)
                existing=merged.setdefault(kind,{}).get(key)
                if existing is None or stamp(row)>=stamp(existing): merged[kind][key]=row
    return {kind:list(rows.values()) for kind,rows in merged.items()}

def sync(args):
    root=pathlib.Path(args.directory);root.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='pulsebeat-sync-') as temporary:
        downloaded=pathlib.Path(temporary)/'pulsebeat.json'
        fetch_data(argparse.Namespace(out=downloaded))
        fresh=read(downloaded)
    ref=account_ref(fresh,credential()['id'])
    old=read(root/'current.json') if (root/'current.json').exists() else {}
    if old and old.get('accountRef')!=ref: raise ValueError('This local directory belongs to another authorization; choose a separate directory')
    run=root/'snapshots'/dt.datetime.now(dt.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ');run.mkdir(parents=True)
    save(run/'pulsebeat.json',fresh)
    local={};failures=[]
    if args.refresh_kugou:
        p=subprocess.run([sys.executable,str(pathlib.Path(__file__).with_name('kugou_collect.py')),'--days',str(args.days),'--out',str(run/'kugou.json')],capture_output=True,text=True,timeout=7200)
        if p.returncode==0: local=read(run/'kugou.json')
        else: failures.append({'provider':'kugou','error':'local_collection_failed','action':'Use Kugou official skill to check personal login; existing data retained'})
    elif args.kugou_file:
        local=read(args.kugou_file);save(run/'kugou.json',local)
    failures+=local.get('failures',[])
    # Full current WHOOP snapshot replaces old WHOOP data; successful music dates accumulate locally.
    fresh['sources'].update(merge_music(old,fresh,local))
    fresh.update(accountRef=ref,localSyncedAt=now(),localKugouFailures=failures,localArchive='Historical successful music dates are retained with original collectedAt; cloud snapshot is not a transaction')
    qq_dir=root/'music'/'qqmusic';qq_dir.mkdir(parents=True,exist_ok=True)
    for filename in args.qq:
        report=read(filename)
        if report.get('source')!='qqmusic' or report.get('timeKey')!='d': raise ValueError('Only QQ daily reports can be archived by sync')
        date=dt.date.fromisoformat(report['date']).isoformat();response=report.get('response',{})
        if any(response.get(k,0) not in (0,None) for k in ('ret','sub_ret')) or not isinstance(response.get('dayData'),dict):
            failures.append({'provider':'qqmusic','date':date,'error':'invalid_report'});continue
        save(run/('qq-'+date+'.json'),report)
        dest=qq_dir/(date+'.json')
        if not dest.exists() or stamp(report)>=stamp(read(dest)): save(dest,report)
    ncm=root/'music'/'netease.json'
    if args.netease:
        report=read(args.netease)
        if report.get('source')!='netease' or report.get('evidenceType')!='favorites' or not isinstance(report.get('songs'),list): raise ValueError('Invalid NetEase favorites export')
        save(run/'netease.json',report)
        if not ncm.exists() or stamp(report)>=stamp(read(ncm)): save(ncm,report)
    spotify=root/'music'/'spotify.json'
    if getattr(args,'spotify',None):
        from spotify_import import validate
        report=read(args.spotify);validate(report)
        save(run/'spotify.json',report)
        if not spotify.exists() or stamp(report)>=stamp(read(spotify)): save(spotify,report)
    save(root/'current.json',fresh)
    manifest={'schema':'pulsebeat.local-sync.v1','completedAt':now(),'accountRef':ref,'current':str((root/'current.json').resolve()),'snapshot':str(run.resolve()),'qq':[str(p.resolve()) for p in sorted(qq_dir.glob('*.json'))],'netease':str(ncm.resolve()) if ncm.exists() else None,'spotify':str(spotify.resolve()) if spotify.exists() else None,'failures':failures,'status':'partial' if failures else 'complete','counts':{k:len(v) for k,v in fresh['sources'].items()}}
    save(root/'sync.json',manifest)
    print('Local sync: '+str((root/'sync.json').resolve()));print('Status: '+manifest['status']);return manifest
