import json
import random
import unittest
from types import SimpleNamespace
from test_core import load_functions, literal


class StripOutfitTests(unittest.IsolatedAsyncioTestCase):
    def namespace(self):
        ns = dict(CLOTHES_FEMALE=literal('CLOTHES_FEMALE'), CLOTHES_MALE=literal('CLOTHES_MALE'),
                  STRIP_SLOTS=literal('STRIP_SLOTS'), STRIP_HEADWEAR=literal('STRIP_HEADWEAR'),
                  CLOTH_BLOCKERS=literal('CLOTH_BLOCKERS'), random=random)
        load_functions({'strip_slot_options', 'outfit_from_choice', 'serialize_strip_outfit', 'play_self_gender',
                        'make_outfit', 'cloth_removable'}, ns)
        return ns

    def choice(self, ns, gender):
        options = ns['strip_slot_options'](gender)
        return {slot: options[slot][0][1][0] for slot in ns['STRIP_SLOTS']}

    def test_five_slots_each_have_options_for_both_genders(self):
        ns = self.namespace()
        for gender in ('female', 'male'):
            options = ns['strip_slot_options'](gender)
            self.assertEqual(set(options), set(ns['STRIP_SLOTS']))
            self.assertTrue(all(options[slot] for slot in options))

    def test_valid_choice_builds_five_items_in_slot_order(self):
        ns = self.namespace()
        items = ns['outfit_from_choice']('female', self.choice(ns, 'female'))
        self.assertEqual(len(items), 5)
        self.assertEqual(len({i['id'] for i in items}), 5)

    def test_incomplete_or_foreign_choice_is_rejected(self):
        ns = self.namespace()
        good = self.choice(ns, 'female')
        self.assertIsNone(ns['outfit_from_choice']('female', {k: v for k, v in good.items() if k != 'shoes'}))
        self.assertIsNone(ns['outfit_from_choice']('female', dict(good, top='INJECTED')))
        self.assertIsNone(ns['outfit_from_choice']('female', dict(good, head='gloves')))
        self.assertIsNone(ns['outfit_from_choice']('female', 'x'))
        self.assertIsNone(ns['outfit_from_choice']('male', dict(self.choice(ns, 'male'), top='blouse')))

    def test_shoes_come_off_before_bottom(self):
        ns = self.namespace()
        items = ns['outfit_from_choice']('male', self.choice(ns, 'male'))
        bottom = next(i for i in items if i['cat'] == 'bottom')
        shoes = next(i for i in items if i['cat'] == 'shoes')
        self.assertFalse(ns['cloth_removable'](items, bottom))
        self.assertTrue(ns['cloth_removable'](items, shoes))


if __name__ == '__main__':
    unittest.main()
