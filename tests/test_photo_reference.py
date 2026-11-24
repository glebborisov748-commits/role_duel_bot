import json,unittest,base64
import photo_reference as p
import character_options
class ReferenceTests(unittest.TestCase):
 def test_bounded_fields_ignore_identity_and_unknown_enums(self):
  value=p.decode(json.dumps({'usable':True,'appearance':{'hair_color':'black','eyes':'unknown','ethnicity':'anything','race':'alien'},'description':'Someone Famous','face_shape':'oval'}),'female')
  self.assertEqual(value['appearance']['hair_color'],'black');self.assertNotIn('race',value['appearance']);self.assertNotIn('ethnicity',value['appearance']);self.assertNotIn('<',value['description']);self.assertNotIn('Famous',value['description'])
 def test_one_subject_and_json_required(self):
  for raw in ('[]','not-json','{"usable":false}','{"usable":true,"appearance":null}'):
   with self.assertRaises((ValueError,TypeError)):p.decode(raw,'male')
 def test_no_remote_urls_or_invalid_binary(self):
  for data in ('https://example.com/person.jpg','data:image/png;base64,AAAA',None,'data:image/jpeg;base64,'+base64.b64encode(b'bad jpeg'*10).decode()):
   with self.assertRaises(ValueError):p.image_data(data)
 def test_description_limit_and_no_controls(self):
  self.assertLessEqual(len(p.clean_note('x'*2000)),600);self.assertNotIn('\n',p.clean_note('a\nb'))
