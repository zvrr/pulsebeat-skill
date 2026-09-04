import sys,pathlib,unittest
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]/'scripts'))
from music_portrait import portrait
from music_media import cover_url,image_type
from music_story_html import render

def day(date,seconds,collected='a',count=1):
 return {'date':date,'dateType':0,'collectedAt':collected,'response':{'errcode':0,'data':{'listen_duration':seconds,'rank_song':[{'count':count,'song_info':{'mix_song_id':1,'name':'Track','singer_name':'Artist'}}],'rank_style':[{'style':'Pop'},{'style':'Pop'}]}}}
class MusicTests(unittest.TestCase):
 def test_latest_snapshot_zero_and_missing(self):
  p=portrait({'sources':{'music:stats':[day('20260101',60),day('20260101',120,'b',2),day('20260103',0)]}})['kugou']
  self.assertEqual(p['summary']['totalMinutes'],2);self.assertEqual(p['summary']['zeroDays'],1);self.assertEqual(p['summary']['observedDays'],2)
  self.assertEqual(p['tracks'][0]['observedPlays'],3);self.assertEqual(p['genreDays'][0]['days'],2)
 def test_missing_day_breaks_streak(self):
  p=portrait({'sources':{'music:stats':[day('20260101',60),day('20260103',60)]}})['kugou'];self.assertEqual(p['summary']['longestObservedStreak'],1)
 def test_qq_dedup_and_units(self):
  q={'source':'qqmusic','timeKey':'d','date':'2026-01-01','response':{'dayData':{'listenTime':120,'songListen':[{'songMid':'x','songName':'T','singerName':'A','sum':3}]}}}
  p=portrait({},[q,q])['qqmusic'];self.assertEqual(p['summary']['totalMinutes'],2);self.assertEqual(p['tracks'][0]['observedPlays'],3)
 def test_artwork_host_boundaries(self):
  for url in ['https://localhost/a','https://imge.kugou.com.evil.test/a','https://x@imge.kugou.com/a','https://imge.kugou.com:8080/a']:self.assertIsNone(cover_url(url))
  self.assertEqual(cover_url('http://imge.kugou.com/{size}/a.jpg?token=secret'),'https://imge.kugou.com/400/a.jpg');self.assertIsNone(image_type(b'<svg onload="x">'))
 def test_external_music_text_escaped(self):
  p=portrait({'sources':{'music:stats':[day('20260101',60)]}})
  p['kugou']['tracks'][0]['title']='<script>alert(1)</script>'
  out=render({'musicPortraits':p},{},{});self.assertNotIn('<script>',out);self.assertIn('&lt;script&gt;',out)
class RhythmTests(unittest.TestCase):
 def test_only_verified_pairs_appear(self):
  from rhythm_html import render
  from i18n import activate
  activate('en')
  data={'healthDaily':[{'date':'2026-01-02','recovery':50,'sleep_hours':7}], 'musicDaily':{'kugou':[{'date':'2026-01-01','seconds':60}]},'associations':[]}
  self.assertNotIn('rhythm-day',render(data,{}))
  data['associations']=[{'provider':'kugou','outcome':'recovery','paired_dates':[{'music':'2026-01-01','health':'2026-01-02'}]}]
  out=render(data,{'rhythmNotes':{'kugou:2026-01-02':'<script>bad</script>'}})
  self.assertIn('Next-day recovery',out);self.assertIn('&lt;script&gt;',out);self.assertNotIn('<script>',out)
if __name__=='__main__':unittest.main()
