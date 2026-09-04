#!/usr/bin/env python3
"""Import a user's Spotify Extended Streaming History locally. No API or network."""
import datetime as dt, hashlib, json, math, pathlib
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

def normalize(files, timezone):
    try: zone=ZoneInfo(timezone)
    except ZoneInfoNotFoundError as exc: raise ValueError('Timezone unavailable; use an installed IANA timezone such as Asia/Shanghai or UTC') from exc
    events={};hashes=[];excluded=0;identities=set()
    for filename in files:
        path=pathlib.Path(filename);raw=path.read_bytes();rows=json.loads(raw)
        if not isinstance(rows,list):raise ValueError('Expected a Spotify Extended Streaming History JSON array')
        hashes.append(hashlib.sha256(raw).hexdigest())
        for row in rows:
            if not isinstance(row,dict) or 'ts' not in row or 'ms_played' not in row:
                raise ValueError('Unsupported Spotify export: use Extended Streaming History with ts and ms_played')
            identity=row.get('username') or row.get('user_name')
            if identity:identities.add(str(identity))
            duration=row['ms_played']
            if not isinstance(duration,(int,float)) or isinstance(duration,bool) or not math.isfinite(duration) or duration<0:raise ValueError('Invalid Spotify played duration')
            if not isinstance(row['ts'],str):raise ValueError('Spotify ts must be an ISO timestamp')
            stamp=dt.datetime.fromisoformat(row['ts'].replace('Z','+00:00'))
            if stamp.tzinfo is None:raise ValueError('Spotify timestamp must include UTC offset')
            # Music only: podcasts, videos without track identity and unknown media stay excluded.
            uri=row.get('spotify_track_uri');name=row.get('master_metadata_track_name')
            if not uri or not name:excluded+=1;continue
            stamp=stamp.astimezone(dt.timezone.utc);local=stamp.astimezone(zone)
            event={'endedAt':stamp.isoformat(),'date':local.date().isoformat(),'seconds':duration/1000,'track':str(name),'artist':row.get('master_metadata_album_artist_name'),'uri':str(uri)}
            key=(event['endedAt'],event['uri'],duration)
            events[key]=event
    if len(identities)>1:raise ValueError('Mixed Spotify accounts; import one person at a time')
    rows=sorted(events.values(),key=lambda e:(e['endedAt'],e['uri']));days={}
    for row in rows:days[row['date']]=days.get(row['date'],0)+row['seconds']
    return {'source':'spotify','evidenceType':'extended_streaming_history','collectedAt':dt.datetime.now(dt.timezone.utc).isoformat(),'timezone':timezone,'sourceSha256':hashes,'records':rows,'daily':[{'date':date,'seconds':seconds,'timezone':timezone,'verified':False} for date,seconds in sorted(days.items())],'excludedNonMusic':excluded,'dateBasis':'stream_end_local_date','coverage':'export_observed_days_only','limitation':'Totals are grouped by stream end date, not proven continuous exposure; no automatic health pairing. Missing days are not zero.'}

def validate(report):
    if report.get('source')!='spotify' or report.get('evidenceType')!='extended_streaming_history' or not isinstance(report.get('records'),list):raise ValueError('Expected normalized Spotify export from spotify-import')
    days={}
    for row in report['records']:
        date=dt.date.fromisoformat(row['date']).isoformat();v=row['seconds']
        if not isinstance(v,(int,float)) or isinstance(v,bool) or not math.isfinite(v) or v<0:raise ValueError('Invalid Spotify listening seconds')
        days[date]=days.get(date,0)+v
    return {date:{'seconds':value,'timezone':report.get('timezone'),'verified':False} for date,value in sorted(days.items())}

def command(args):
    from pulsebeat import save
    save(args.out,normalize(args.files,args.timezone));print('Spotify local import: '+str(args.out))
