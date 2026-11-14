import ast
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
tree = ast.parse((ROOT / 'app.py').read_text())
constants = {}
for node in tree.body:
    if isinstance(node, ast.Assign) and isinstance(node.targets[0], ast.Name):
        try: constants[node.targets[0].id] = ast.literal_eval(node.value)
        except (ValueError, TypeError): pass
for node in tree.body:
    if isinstance(node, ast.Assign) and isinstance(node.targets[0], ast.Subscript) and getattr(node.targets[0].value, 'id', '') == 'APP_TEXTS':
        constants['APP_TEXTS']['de'] = {**constants['APP_TEXTS']['en'], **ast.literal_eval(node.value.values[1])}
for node in tree.body:
    if isinstance(node, ast.Expr) and isinstance(node.value, ast.Call) and isinstance(node.value.func, ast.Attribute) and node.value.func.attr=='update' and isinstance(node.value.func.value, ast.Subscript) and getattr(node.value.func.value.value,'id','')=='APP_TEXTS':
        constants['APP_TEXTS'][ast.literal_eval(node.value.func.value.slice)].update(ast.literal_eval(node.value.args[0]))
ui = constants['APP_TEXTS']['ru']
state = {
    'onboarding': None, 'pending': False, 'notices': [], 'can_reroll': True,
    'messages': [{'id':'u1','role':'user','text':'Привет, как прошёл твой день?'}, {'id':'a1','role':'assistant','text':'Привет! Рада тебя видеть.'}],
    'character': {'avatar':'👩🏻', 'avatar_url':'/assets/avatar_real_f1.jpg','name':'Аня','title':'Аня','subtitle':'Реальный мир · Тёплый характер', 'looks':[], 'can_avatar':True,'custom_photo':False},
    'stats': {'energy':90,'energy_max':100,'satiety':80,'water':75,'mood':40,'bucks':2500,'energizers':2,'scenes':0,'level':2,'xp':30,'xp_cost':100},
    'asleep':False,'illness':None, 'wake':{'energizers':2,'elite':False,'price':25},
    'subscription':{'level':'pro','title':'PRO','until':'13.12.2026'},
    'offers':[{'payload':'subscribe_pro','title':'PRO','perks':ui['perks_pro'],'stars':220,'stars_label':'220','rub':None}],
    'upgrade':None,'sale':None,'coupon':None,'hot':{'available':0,'pending':False},
    'settings':{'lang':'ru','scene':'phone','tour_seen':True,'muted':False,'immunity':False,'can_mute':False,'can_immunity':False},
    'relationship':{'trust':12,'respect':15,'stage':'Знакомство'},
    'bucks_packs':[{'payload':'bucks_5000','amount':5000,'stars':10,'saving':0},{'payload':'bucks_15000','amount':15000,'stars':18,'saving':40},{'payload':'bucks_50000','amount':50000,'stars':35,'saving':65}],
    'quests':{'day':'2026-11-14','reset_at':1794690000,'items':[{'id':'courier10','title':'Доставь 10 заказов','event':'courier','target':10,'progress':10,'claimed':False,'reward':{'kind':'bucks','amount':600}},{'id':'hack5','title':'Выполни 5 взломов','event':'hack','target':5,'progress':2,'claimed':False,'reward':{'kind':'energizers','amount':1}}]},
    'animated_reactions':True,
    'server_day':'2026-11-14',
    'referral':{'text':'За друга: 2 000 баксов и 1 энергетик','link':None,'count':0,'earned_bucks':0,'earned_energizers':0},
    'channel':'https://t.me/duel_dev_channel', 'ui':ui,
}
