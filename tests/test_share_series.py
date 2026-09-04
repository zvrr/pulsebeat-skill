import json,pathlib,sys,tempfile,unittest
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]/'scripts'))
from share_cards import generate
class ShareTests(unittest.TestCase):
 def test_selected_data_only_and_escaped_copy(self):
  with tempfile.TemporaryDirectory() as tmp:
   out=generate({'profile':{'email':'private@example.test'},'tokens':'NEVER_INCLUDE'}, {'headline':'<script>alert(1)</script>'},{},tmp,'en')
   text=out.read_text();self.assertEqual(text.count('class="share-card '),6);self.assertNotIn('private@example.test',text);self.assertNotIn('NEVER_INCLUDE',text);self.assertNotIn('<script>',text);self.assertIn('&lt;script&gt;',text)
   self.assertFalse(json.loads((pathlib.Path(tmp)/'manifest.json').read_text())['rendered'])
if __name__=='__main__':unittest.main()
