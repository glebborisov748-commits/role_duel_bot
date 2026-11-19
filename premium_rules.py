"""Term-preserving upgrades, independent from Telegram handlers."""
from datetime import datetime
import math
NEXT={'pro':('super_pro','upgrade_to_super'),'super_pro':('elite','upgrade_to_elite')}
STAR_PRICES={7:{'pro':100,'super_pro':225,'elite':542},30:{'pro':292,'super_pro':667,'elite':1667}}
PHOTO_LIMITS={7:{'pro':10,'super_pro':20,'elite':45},30:{'pro':45,'super_pro':90,'elite':200}}
def upgrade(user,now=None):
 now=now or datetime.now();sub=user.get('subscription') or {};tier=sub.get('level')
 try:expires=datetime.fromisoformat(sub.get('expires_at',''))
 except (TypeError,ValueError):return None
 if not sub.get('active') or expires<=now or tier not in NEXT:return None
 target,payload=NEXT[tier];term=7 if sub.get('term_days')==7 else 30
 fraction=(expires-now).total_seconds()/86400/term
 return dict(payload=payload,source=tier,target=target,expires_at=sub['expires_at'],term_days=term,
             stars=max(1,math.ceil((STAR_PRICES[term][target]-STAR_PRICES[term][tier])*fraction)),
             photos=max(0,math.ceil((PHOTO_LIMITS[term][target]-PHOTO_LIMITS[term][tier])*fraction)))
