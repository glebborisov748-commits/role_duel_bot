import unittest,types,hashlib
from pathlib import Path
from unittest.mock import AsyncMock
import character_options,profile_options,avatar_preview,online_ui
from test_core import load_functions

class VisualRefreshTests(unittest.TestCase):
 def test_gender_lists_and_world_presets_are_distinct(self):
  male={f['key']:{i['key'] for i in f['items']} for f in character_options.choices('ru','male')}
  female={f['key']:{i['key'] for i in f['items']} for f in character_options.choices('ru','female')}
  self.assertFalse({'long','braid','ponytail'}&male['hair_style'])
  self.assertNotIn('hairclip',male['accessory']);self.assertIn('long',female['hair_style'])
  self.assertNotIn('species',male);self.assertGreaterEqual(len(profile_options.RACES),10)
  root=Path(__file__).resolve().parents[1]/'assets'
  for world in ('anime','realism'):
   for gender in ('male','female'):
    for field in character_options.choices('ru',gender):
     if field['key']=='hair_style':
      for option in field['items']:self.assertTrue((root/f"avatar_{world}_{gender}_{option['key']}.webp").is_file())
  self.assertNotEqual(avatar_preview.base('anime','male','short'),avatar_preview.base('realism','male','short'))
 def test_eye_color_uses_an_iris_mask_and_does_not_draw_fake_eyes(self):
  blue=avatar_preview.svg({'world':'anime','eyes':'blue'},'male');green=avatar_preview.svg({'world':'anime','eyes':'green'},'male')
  self.assertIn('id="eye-mask"',blue);self.assertIn('filter="url(#eye-dye)" mask="url(#eye-mask)"',blue)
  self.assertNotEqual(hashlib.sha256(blue.encode()).hexdigest(),hashlib.sha256(green.encode()).hexdigest())
 def test_online_screen_uses_local_sdk_so_embed_can_share_parent_auth(self):
  import re
  ns={'with_sfx':lambda h:h,'APP_THEME_TAG':'<link rel="stylesheet" href="/theme.css">','_SDK_TAG_RE':re.compile(r'<script src="/tg-sdk\.js"[^>]*>\s*</script>',re.S),'EMBED_BRIDGE':'<script>window.Telegram=window.parent.Telegram;</script>','web':types.SimpleNamespace(Response=lambda **kw:kw),'with_app_back':lambda h:h}
  load_functions({'page_response'},ns)
  html=ns['page_response'](types.SimpleNamespace(query={'embed':'1'}),online_ui.PAGE_HTML)['text']
  self.assertIn('window.parent.Telegram',html);self.assertNotIn('telegram.org/js',html)
  self.assertNotIn('src="/tg-sdk.js"',html)

class EnergizerAdminTests(unittest.IsolatedAsyncioTestCase):
 async def test_permission_validation_and_id_username_routes(self):
  grant=AsyncMock();resolve=AsyncMock(return_value=42);answer=AsyncMock()
  ns={'ADMIN_IDS':[7],'_resolve_admin_target':resolve,'_grant_to':grant}
  load_functions({'giveenergizers_cmd'},ns)
  m=types.SimpleNamespace(from_user=types.SimpleNamespace(id=8),text='/giveenergizers @friend 20',answer=answer)
  await ns['giveenergizers_cmd'](m);grant.assert_not_called();resolve.assert_not_called()
  m.from_user.id=7;m.text='/giveenergizers 42 -1';await ns['giveenergizers_cmd'](m);grant.assert_not_called()
  m.text='/giveenergizers 42 20';await ns['giveenergizers_cmd'](m)
  self.assertEqual(grant.call_args.args[2],['/grant','42','energizers','20'])
  m.text='/giveenergy @friend 3';await ns['giveenergizers_cmd'](m)
  self.assertEqual(grant.call_args.args[2],['/grant','@friend','energizers','3'])
