#!/usr/bin/env python3
"""Cache supplied public cover URLs locally; sends no health or listening metrics."""
import argparse,base64,datetime as dt,hashlib,json,pathlib,urllib.parse,urllib.request
HOSTS={'imge.kugou.com','singerimg.kugou.com'}
class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self,*args,**kwargs):return None

def cover_url(raw):
    try:
        p=urllib.parse.urlsplit(str(raw or '').replace('{size}','400'))
        if p.hostname not in HOSTS or p.username or p.password or p.port not in (None,443) or p.scheme not in ('http','https'):return None
    except ValueError:return None
    return urllib.parse.urlunsplit(('https',p.netloc,p.path,'',''))

def image_type(b):
    if b.startswith(b'\xff\xd8\xff'):return 'image/jpeg'
    if b.startswith(b'\x89PNG\r\n\x1a\n'):return 'image/png'
    if b[:4]==b'RIFF' and b[8:12]==b'WEBP':return 'image/webp'
    return None

def collect(analysis,catalog=None):
    items={};failures=[];opener=urllib.request.build_opener(NoRedirect)
    for provider,portrait in analysis.get('musicPortraits',{}).items():
        for track in portrait.get('tracks',[])[:8]:
            key=provider+':'+track['id'];item={'title':track['title'],'artist':track.get('artist','')};url=cover_url(track.get('coverUrl'))
            public=(catalog or {}).get(key,{})
            if public:
                if public.get('title')!=item['title'] or public.get('artist')!=item['artist']:raise ValueError('Public catalog track identity mismatch: '+key)
                for k in ['context','contextSource','contextSourceTitle','checkedAt']:item[k]=public.get(k)
            if url:
                try:
                    with opener.open(urllib.request.Request(url,headers={'User-Agent':'PulseBeat/0.3 (public artwork cache)'}),timeout=20) as response:raw=response.read(1500001)
                    mime=image_type(raw)
                    if not mime or len(raw)>1500000:raise ValueError('Unsupported or oversized image')
                    item.update(imageDataUri='data:'+mime+';base64,'+base64.b64encode(raw).decode(),imageSource=url,imageSha256=hashlib.sha256(raw).hexdigest())
                except (OSError,ValueError) as exc:failures.append({'track':key,'error':type(exc).__name__})
            items[key]=item
    return {'items':items,'failures':failures,'fetchedAt':dt.datetime.now(dt.timezone.utc).isoformat(),'rights':'Provider-supplied artwork retained for this local report; not a public-domain or redistribution license.'}

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--analysis',required=True);p.add_argument('--catalog');p.add_argument('--out',required=True);a=p.parse_args()
    from pulsebeat import read,save
    result=collect(read(a.analysis),read(a.catalog) if a.catalog else None);save(a.out,result)
    print(json.dumps({'covers':sum('imageDataUri' in v for v in result['items'].values()),'failures':len(result['failures']),'out':a.out}))
if __name__=='__main__':main()
