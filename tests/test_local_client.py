import argparse, importlib.util, json, pathlib, sys, tempfile, unittest
from unittest.mock import patch
scripts=pathlib.Path(__file__).resolve().parents[1]/'scripts';sys.path.insert(0,str(scripts))
import local_sync, pulsebeat, report_html

def entry(date,seconds,collected='2026-09-04T00:00:00Z'):
    return {'date':date,'dateType':0,'collectedAt':collected,'response':{'errcode':0,'data':{'listen_duration':seconds}}}
class LocalTests(unittest.TestCase):
    def test_music_history_and_freshness(self):
        old={'sources':{'music:stats':[entry('20260801',60),entry('20260901',120)]}}
        newer={'sources':{'music:stats':[entry('20260901',999,'2026-09-01T00:00:00Z'),entry('20260902',180)]}}
        merged=local_sync.merge_music(old,newer)['music:stats'];values={e['date']:e['response']['data']['listen_duration'] for e in merged}
        self.assertEqual(values,{'20260801':60,'20260901':120,'20260902':180})
    def test_sync_keeps_history_and_exposes_failures(self):
        with tempfile.TemporaryDirectory() as directory:
            root=pathlib.Path(directory);fresh={'sources':{'cycle':[{'user_id':100,'id':1}],'music:stats':[entry('20260902',180)]}}
            old={'accountRef':local_sync.account_ref(fresh,'x'),'sources':{'cycle':[{'user_id':100,'id':2}],'music:stats':[entry('20260801',60)]}}
            pulsebeat.save(root/'current.json',old);pulsebeat.save(root/'input.json',{'sources':{},'failures':[{'code':30430}]})
            args=argparse.Namespace(directory=directory,refresh_kugou=False,kugou_file=root/'input.json',qq=[],netease=None)
            with patch.object(local_sync,'credential',return_value={'id':'x'}),patch.object(local_sync,'fetch_data',side_effect=lambda a:pulsebeat.save(a.out,fresh)):
                result=local_sync.sync(args)
            self.assertEqual(result['status'],'partial');current=pulsebeat.read(root/'current.json')
            self.assertEqual(len(current['sources']['music:stats']),2);self.assertEqual(current['sources']['cycle'],fresh['sources']['cycle'])
    def test_other_account_does_not_overwrite_or_archive(self):
        with tempfile.TemporaryDirectory() as directory:
            root=pathlib.Path(directory);old={'accountRef':'someone_else','sources':{}};pulsebeat.save(root/'current.json',old)
            args=argparse.Namespace(directory=directory)
            with patch.object(local_sync,'credential',return_value={'id':'x'}),patch.object(local_sync,'fetch_data',side_effect=lambda a:pulsebeat.save(a.out,{'sources':{'cycle':[{'user_id':101}]}})):
                with self.assertRaises(ValueError):local_sync.sync(args)
            self.assertEqual(pulsebeat.read(root/'current.json'),old);self.assertFalse((root/'snapshots').exists())
    def test_html_external_content_not_executed(self):
        payload='<script>alert(1)</script><img src="https://attacker.invalid">'
        out=report_html.render({'warnings':[payload]},'# Report\n'+payload+'\n| h | v |\n|---|---|\n| field | **bold** |')
        self.assertEqual(out.count('<script>'),1);self.assertNotIn('<script>alert(1)',out);self.assertNotIn('<img ',out);self.assertIn('&lt;script&gt;',out);self.assertIn("default-src 'none'",out);self.assertIn('<strong>bold</strong>',out)
    def test_template_trusted_script_hash_and_gap(self):
        import base64, hashlib, re
        out=report_html.render({},'A real interpretation')
        script=re.search(r'<script>(.*?)</script>',out,re.S)[1]
        self.assertEqual(script,(scripts.parent/'assets/report.js').read_text())
        self.assertIn('sha256-'+base64.b64encode(hashlib.sha256(script.encode()).digest()).decode(),out)
        chart=report_html.chart([('2026-01-01',10),('2026-01-03',30)],'#333')
        self.assertNotIn('<polyline',chart)
    def test_share_card_does_not_embed_raw_source(self):
        data={'sourceFileSha256':'SECRET_HASH','healthDaily':[{'private':'PRIVATE_RECORD'}],'preferences':{'email':'PRIVATE_EMAIL'},'healthMetrics':{}}
        card=report_html.share_card(data,{'headline':'Safe headline'})
        for value in ['SECRET_HASH','PRIVATE_RECORD','PRIVATE_EMAIL']:
            self.assertNotIn(value,card)
    def test_html_requires_ai_interpretation(self):
        with tempfile.TemporaryDirectory() as directory:
            file=pathlib.Path(directory)/'analysis.json';file.write_text('{}')
            with self.assertRaises(ValueError):report_html.build(argparse.Namespace(analysis=file,interpretation=None))
if __name__=='__main__':unittest.main()
