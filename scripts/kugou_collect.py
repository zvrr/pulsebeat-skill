#!/usr/bin/env python3
"""Collect personally authorized Kugou data locally, sequentially. No cloud upload."""
import argparse, datetime as dt, json, re, subprocess, time
from pulsebeat import save, TZ

def run(args):
    try:
        p=subprocess.run(['kugou-cli',*args],text=True,capture_output=True,timeout=60)
        if p.returncode:
            m=re.search(r'(?:code[=: ]+|errcode[\"\s:]+)(\d{4,6})',p.stderr+' '+p.stdout)
            return {'errcode':int(m.group(1)) if m else 'cli_failed'}
        return json.loads(p.stdout)
    except (subprocess.TimeoutExpired,json.JSONDecodeError,FileNotFoundError): return {'errcode':'cli_unavailable'}

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--days',type=int,default=7);p.add_argument('--out',required=True);args=p.parse_args()
    if not 1<=args.days<=30: p.error('--days must be 1..30')
    if not run(['auth','status']).get('logged_in'): raise SystemExit('请通过酷狗 Skill 执行 kugou-cli auth login，完成个人授权。')
    now=dt.datetime.now(TZ);jobs=[('favorites',None,['music','favorites']),('recent',None,['music','recent'])]
    for offset in range(1,args.days+1):
        date=(now.date()-dt.timedelta(days=offset)).strftime('%Y%m%d');jobs.append(('stats',date,['music','stats','--date-type','0','--date',date]))
    result={'schema':'pulsebeat.export.v1','exportedAt':now.isoformat(),'sources':{},'failures':[]}
    for kind,date,command in jobs:
        for attempt in range(3):
            response=run(command)
            if response.get('errcode',response.get('code')) not in (30430,'30430'): break
            time.sleep(10*(attempt+1))
        if response.get('errcode')==0 and isinstance(response.get('data'),dict): result['sources'].setdefault('music:'+kind,[]).append({'kind':kind,'date':date,'dateType':0 if date else None,'response':response,'collectedAt':now.isoformat()})
        else: result['failures'].append({'kind':kind,'date':date,'code':response.get('errcode',response.get('code','invalid'))})
        print(kind+' '+str(date)+': '+('ok' if response.get('errcode')==0 else 'unavailable'),flush=True);time.sleep(2)
    save(args.out,result);print('Saved: '+args.out)
if __name__=='__main__': main()
