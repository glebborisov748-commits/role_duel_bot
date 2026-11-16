import re
import unittest
from test_core import load_functions


class PhotoControlTests(unittest.TestCase):
    def setUp(self):
        self.ns={'character_behavior_rule':lambda u:'','re':re,'save_data':lambda d:None,'user_data':{},'ENERGY_MAX':150,'ENERGIZER_RESTORE_AMOUNT':78}
        load_functions({'is_photo_request','use_energizer','casual_chat_rule','conversation_mode_rule'},self.ns)
    def test_natural_photo_requests(self):
        for text in ('Хочу увидеть тебя','Хочу тебя увидеть','Кинь фотку','Скинь свою фотку','Покажи себя','Покажи как ты выглядишь','Можешь прислать фото в платье?','Можно твоё фото?','Send me a selfie','Zeig dich'):
            self.assertTrue(self.ns['is_photo_request'](text),text)
        for text in ('Привет, как дела?','Вчера ты просила скинуть фото','Не присылай фото','Я покажу себя позже'):
            self.assertFalse(self.ns['is_photo_request'](text),text)
    def test_energizer_disabled_at_capacity_and_clamped_below_it(self):
        user={'energy':150,'energizers':2,'sleep_until':None}
        self.assertFalse(self.ns['use_energizer'](user))
        self.assertEqual(user['energizers'],2)
        user['energy']=140
        self.assertTrue(self.ns['use_energizer'](user))
        self.assertEqual((user['energy'],user['energizers']),(150,1))
        self.assertFalse(self.ns['use_energizer'](user))
        self.assertEqual(user['energizers'],1)
    def test_texting_uses_natural_slang_and_does_not_claim_physical_presence(self):
        prompt=self.ns['conversation_mode_rule']({'scene':'phone','lang':'ru'})
        self.assertIn('на расстоянии',prompt)
        self.assertIn('ща',prompt)
        self.assertIn('сек',prompt)
