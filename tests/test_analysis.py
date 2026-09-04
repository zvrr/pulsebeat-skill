import datetime as dt, importlib.util, pathlib, unittest, sys
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]/'scripts'))
spec=importlib.util.spec_from_file_location('pulsebeat',pathlib.Path(__file__).resolve().parents[1]/'scripts/pulsebeat.py');pb=importlib.util.module_from_spec(spec);spec.loader.exec_module(pb)
def fixture(n):
    source={k:[] for k in ['cycle','recovery','sleep','music:stats']}
    for i in range(n):
        day=dt.date(2026,1,2)+dt.timedelta(days=i);previous=day-dt.timedelta(days=1)
        source['cycle'].append({'id':i,'start':previous.isoformat()+'T01:00:00Z','score_state':'SCORED','score':{'strain':i/2}})
        source['sleep'].append({'id':str(i),'cycle_id':i,'end':previous.isoformat()+'T23:00:00Z','timezone_offset':'+08:00','nap':False,'score_state':'SCORED','score':{'stage_summary':{'total_light_sleep_time_milli':3600000,'total_slow_wave_sleep_time_milli':3600000,'total_rem_sleep_time_milli':3600000}}})
        source['recovery'].append({'cycle_id':i,'sleep_id':str(i),'score_state':'SCORED','score':{'recovery_score':i+20,'hrv_rmssd_milli':i+10}})
        source['music:stats'].append({'dateType':0,'date':previous.strftime('%Y%m%d'),'response':{'data':{'listen_duration':(i+1)*60}}})
    return {'sources':source}
class AnalysisTests(unittest.TestCase):
    def test_short_sample_and_correct_sleep_day(self):
        r=pb.analyze(fixture(6));a=r['associations'][0]
        self.assertEqual(a['n'],6);self.assertIsNone(a['spearman_r']);self.assertEqual(a['paired_dates'][0],{'music':'2026-01-01','health':'2026-01-02'})
        self.assertEqual(r['healthMetrics']['sleep_hours']['mean'],3)
    def test_enough_and_ties(self):
        a=pb.analyze(fixture(21))['associations'][0];self.assertEqual(a['spearman_r'],1);self.assertEqual(a['split_half_r'],[1,1]);self.assertEqual(pb.ranks([1,1,3]),[1.5,1.5,3])
    def test_pending_calibration_duplicates_timezone(self):
        f=fixture(6);s=f['sources'];s['recovery'][0]['score_state']='PENDING_SCORE';s['recovery'][1]['score']['user_calibrating']=True;s['sleep'][2]['timezone_offset']='-04:00';s['recovery'].append(s['recovery'][3])
        r=pb.analyze(f);self.assertEqual(r['associations'][0]['n'],2)
    def test_qq_week_never_day_timezone_unverified(self):
        q={'source':'qqmusic','timeKey':'w','date':'2026-01-01','response':{'weekData':{'listenTime':900}}}
        r=pb.analyze(fixture(2),[q]);self.assertNotIn('qqmusic',r['musicCoverage'])
        q.update(timeKey='d',response={'dayData':{'listenTime':120}},timezone='+08:00')
        r=pb.analyze(fixture(2),[q]);a=next(x for x in r['associations'] if x['provider']=='qqmusic');self.assertEqual(a['n'],0)
    def test_netease_preferences_not_exposure(self):
        n={'source':'netease','evidenceType':'favorites','songs':[{'name':'song','durationMs':100000,'addedAtMs':123}]}
        r=pb.analyze(fixture(2),netease=n);self.assertNotIn('netease',r['musicCoverage']);self.assertEqual(r['providerAvailability']['netease'],'available')
    def test_missing_is_not_zero_constant_no_correlation(self):
        f=fixture(21)
        for x in f['sources']['music:stats']: x['response']['data']['listen_duration']=0
        r=pb.analyze(f);self.assertEqual(r['associations'][0]['status'],'no_variation');self.assertEqual(r['musicCoverage']['kugou']['mean_minutes'],0)
        f['sources']['music:stats']=[];self.assertEqual(pb.analyze(f)['associations'],[])
if __name__=='__main__': unittest.main()
