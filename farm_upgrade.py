"""One fertilizer charge with a use-triggered restock, independent of crop payouts."""
import math
import time

PRICE=2000
STARS=5
RESTOCK=2*3600
NEW_CROPS={
 'strawberry':dict(emoji='🍓',ru='Клубника',en='Strawberries',de='Erdbeeren',grow_hours=2,base_payout=175,water_bonus=25),
 'chili':dict(emoji='🌶️',ru='Острый перец',en='Chili peppers',de='Chili',grow_hours=5,base_payout=500,water_bonus=55),
 'pineapple':dict(emoji='🍍',ru='Ананас',en='Pineapple',de='Ananas',grow_hours=16,base_payout=1800,water_bonus=190),
 'mango':dict(emoji='🥭',ru='Манго',en='Mango',de='Mango',grow_hours=20,base_payout=2200,water_bonus=230),
}

def snapshot(user,now=None):
 now=time.time() if now is None else now;stock=user.get('farm_fertilizer') or {}
 left=max(0,math.ceil(stock.get('ready_at',0)-now))
 return dict(owned=bool(stock.get('owned')),ready_in=left,available=not stock.get('owned') and left==0,price=PRICE,stars=STARS,restock_seconds=RESTOCK,reduction=.5)

def grant(user,now=None):
 if not snapshot(user,now)['available']:return False
 user['farm_fertilizer']=dict(owned=True,ready_at=0)
 return True

def apply(user,plot,seconds_left,now=None):
 now=time.time() if now is None else now
 if not snapshot(user,now)['owned'] or not plot or plot.get('fertilized') or not math.isfinite(seconds_left) or seconds_left<=1:return False
 saved=seconds_left*.5
 plot['growth_bonus_seconds']=float(plot.get('growth_bonus_seconds',0))+saved;plot['fertilized']=True
 user['farm_fertilizer']=dict(owned=False,ready_at=now+RESTOCK)
 return saved
