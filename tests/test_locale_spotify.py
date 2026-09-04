import argparse, datetime as dt, json, pathlib, plistlib, re, sys, tempfile, unittest
from unittest.mock import patch
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]/'scripts'))
import i18n, pulsebeat, report_html, spotify_import

class LocaleTests(unittest.TestCase):
    def test_explicit_and_environment_override(self):
        with patch.dict('os.environ',{'PULSEBEAT_LANG':'zh-TW'},clear=True),patch.object(i18n,'system_language',return_value='en'):
            self.assertEqual(i18n.resolve(),'zh-CN');self.assertEqual(i18n.resolve('en'),'en')
    def test_mac_ui_language_not_terminal_locale(self):
        with patch.object(i18n.platform,'system',return_value='Darwin'),patch.object(i18n.subprocess,'check_output',return_value=plistlib.dumps({'AppleLanguages':['zh-Hans-CN','en-CN']})),patch.dict('os.environ',{'LANG':'en_US.UTF-8'},clear=True):
            self.assertEqual(i18n.system_language(),'zh-CN')
    def test_windows_ui_and_linux_fallback(self):
        with patch.object(i18n.platform,'system',return_value='Windows'),patch.object(i18n.subprocess,'check_output',return_value='en-US\n'):
            self.assertEqual(i18n.system_language(),'en')
        with patch.object(i18n.platform,'system',return_value='Linux'),patch.dict('os.environ',{'LANGUAGE':'zh_CN:en','LANG':'en_US.UTF-8'},clear=True):
            self.assertEqual(i18n.system_language(),'zh-CN')
        with patch.object(i18n.platform,'system',return_value='Linux'),patch.dict('os.environ',{'LANG':'fr_FR.UTF-8'},clear=True):
            self.assertEqual(i18n.system_language(),'en')
    def test_report_languages_and_original_prose(self):
        for lang,label in [('en','Recovery score'),('zh-CN','恢复分数')]:
            i18n.activate(lang);data=pulsebeat.analyze({})
            out=report_html.render(data,'Original song: 青花瓷',{'headline':'My rhythm','summary':'Only evidence','language':lang},lang=lang)
            self.assertIn('lang="'+lang+'"',out);self.assertIn(label,out);self.assertIn('青花瓷',out)
            if lang=='en': self.assertFalse(re.search('[\u4e00-\u9fff]',out.replace('青花瓷','')))
    def test_language_mismatch_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            root=pathlib.Path(d);(root/'a.json').write_text('{}');(root/'note.md').write_text('Some real interpretation');(root/'i.json').write_text('{"language":"zh-CN"}')
            with self.assertRaisesRegex(ValueError,'language mismatch'):
                report_html.build(argparse.Namespace(analysis=root/'a.json',interpretation=root/'note.md',insights=root/'i.json',out=root/'r.html',lang='en'))

class SpotifyTests(unittest.TestCase):
    def row(self):return {'ts':'2026-01-01T17:00:00Z','ms_played':123000,'spotify_track_uri':'spotify:track:synthetic','master_metadata_track_name':'Synthetic song','master_metadata_album_artist_name':'Synthetic artist','username':'private-person','ip_addr':'PRIVATE_IP'}
    def test_local_timezone_actual_duration_dedup_and_privacy(self):
        with tempfile.TemporaryDirectory() as d:
            p=pathlib.Path(d)/'music.json';p.write_text(json.dumps([self.row(),self.row()]))
            report=spotify_import.normalize([p,p],'Asia/Shanghai')
            self.assertEqual(len(report['records']),1);self.assertEqual(report['daily'][0]['date'],'2026-01-02');self.assertEqual(report['daily'][0]['seconds'],123)
            self.assertNotIn('PRIVATE_IP',json.dumps(report));self.assertNotIn('private-person',json.dumps(report))
            result=pulsebeat.analyze({},spotify=report)
            self.assertEqual(result['musicCoverage']['spotify']['mean_minutes'],2.05)
            self.assertTrue(all(a['n']==0 and a['spearman_r'] is None for a in result['associations']))
    def test_unknown_schema_and_mixed_accounts_fail(self):
        with tempfile.TemporaryDirectory() as d:
            p=pathlib.Path(d)/'music.json';p.write_text('[{"track":{"duration_ms":99999}}]')
            with self.assertRaises(ValueError):spotify_import.normalize([p],'UTC')
            other={**self.row(),'username':'someone-else'};p.write_text(json.dumps([self.row(),other]))
            with self.assertRaisesRegex(ValueError,'Mixed Spotify'):spotify_import.normalize([p],'UTC')
    def test_excludes_podcast_and_never_fills_missing_days(self):
        with tempfile.TemporaryDirectory() as d:
            p=pathlib.Path(d)/'music.json';p.write_text(json.dumps([self.row(),{**self.row(),'spotify_track_uri':None,'master_metadata_track_name':None}]))
            report=spotify_import.normalize([p],'UTC');self.assertEqual(report['excludedNonMusic'],1);self.assertEqual(len(report['daily']),1)

if __name__=='__main__':unittest.main()
