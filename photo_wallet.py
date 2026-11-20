"""Durable photo entitlements. No provider calls or energy side effects."""
from datetime import datetime, timedelta
import secrets
MONTHLY={'pro':45,'super_pro':90,'elite':200}
WEEKLY={'pro':10,'super_pro':20,'elite':45}
PACKS={'photo_3':(3,25),'photo_8':(8,60),'photo_20':(20,140)}
LEGACY_PACKS={'photo_1':(1,10),'photo_5':(5,45),'photo_15':(15,120)}
ALL_PACKS={**LEGACY_PACKS,**PACKS}

def now():return datetime.now()
def ensure(user):
 if user.get('photo_wallet_version')!=1:
  user['photo_credits']=max(0,int(user.get('photo_credits',0)))+max(0,int(user.pop('avatar_credits',0)))
  user['photo_wallet_version']=1
  if user.get('avatar_job'):user.setdefault('photo_reservations',{})['avatar']={'started':user['avatar_job'].get('started',now().isoformat())}
  if not user.get('photo_trial_granted'):
   user['photo_credits']+=1;user['photo_trial_granted']=True
  sub=user.get('subscription') or {}
  try:remaining=(datetime.fromisoformat(sub.get('expires_at',''))-now()).total_seconds()/86400
  except (ValueError,TypeError):remaining=0
  if sub.get('active') and remaining>0 and sub.get('level') in MONTHLY:
   grant(user,max(1,int(MONTHLY[sub['level']]*min(30,remaining)/30)),sub['expires_at'])
 user.setdefault('photo_grants',[]);user.setdefault('photo_reservations',{})
 repair_admin_subscription(user)
 user['photo_grants']=[g for g in user['photo_grants'] if g['remaining']>0 and g['expires_at']>now().isoformat()]

def grant(user,count,expires_at=None):
 if expires_at:user.setdefault('photo_grants',[]).append({'id':secrets.token_hex(8),'remaining':count,'expires_at':expires_at})
 else:user['photo_credits']=max(0,int(user.get('photo_credits',0)))+count

def balance(user):
 ensure(user)
 return max(0,int(user.get('photo_credits',0)))+sum(g['remaining'] for g in user['photo_grants'])

def reserve(user,key):
 ensure(user)
 if key in user['photo_reservations']:return False
 grants=sorted(user['photo_grants'],key=lambda g:g['expires_at'])
 if grants:
  source=grants[0];source['remaining']-=1
  entry={'grant_id':source['id'],'expires_at':source['expires_at']}
 elif user['photo_credits']>0:
  user['photo_credits']-=1;entry={}
 else:return False
 user['photo_reservations'][key]=dict(entry,started=now().isoformat());return True

def finish(user,key,refund=False):
 entry=user.get('photo_reservations',{}).pop(key,None)
 if entry is None:return False
 if refund:
  # Failed jobs remain retryable even if the subscription expired in flight.
  target=next((g for g in user.get('photo_grants',[]) if g['id']==entry.get('grant_id') and g['expires_at']>now().isoformat()),None)
  if entry.get('portrait_credit'):user['portrait_credits']=user.get('portrait_credits',0)+1
  elif target:target['remaining']+=1
  elif entry.get('grant_id') and entry.get('expires_at','')>now().isoformat():
   user.setdefault('photo_grants',[]).append({'id':entry['grant_id'],'remaining':1,'expires_at':entry['expires_at']})
  else:grant(user,1)
 return True

def snapshot(user):
 total=balance(user)
 return {'total':total,'purchased':user.get('photo_credits',0),'subscription':sum(g['remaining'] for g in user['photo_grants']),
         'expires_at':min((g['expires_at'] for g in user['photo_grants']),default=None)}


def recover(user):
 """Refund interrupted jobs once, including legacy avatar jobs without wallet escrow."""
 if user.get('avatar_job'):
  if 'avatar' not in user.get('photo_reservations',{}):
   if user.get('photo_wallet_version')==1:grant(user,1)
   else:user['avatar_credits']=int(user.get('avatar_credits',0))+1
  user.pop('avatar_job',None);user['avatar_error']='interrupted'
 for key in list(user.get('photo_reservations',{})):finish(user,key,refund=True)


def grant_subscription(user,tier,days,expires_at):
 """Called once by the shared subscription grant path, after wallet migration."""
 count=(WEEKLY if days==7 else MONTHLY).get(tier,0)
 if days not in (7,30):count=max(0,int(MONTHLY.get(tier,0)*days/30))
 if count:grant(user,count,expires_at)
 user['subscription_photo_granted_at']=now().isoformat()


def repair_admin_subscription(user):
 """One-time, bounded repair for old command grants made after wallet migration.
 Paid accounts and accounts with a surviving grant/escrow do not receive extra quota.
 """
 if not user.get('granted_sub_at') or user.get('subscription_photo_granted_at'):return
 sub=user.get('subscription') or {}
 try:remaining=(datetime.fromisoformat(sub.get('expires_at',''))-now()).total_seconds()/86400
 except (ValueError,TypeError):return
 if not sub.get('active') or remaining<=0 or sub.get('level') not in MONTHLY:return
 if not user.get('ever_subscribed') and not user.get('photo_grants') and not user.get('photo_reservations'):
  grant(user,max(1,int(MONTHLY[sub['level']]*min(30,remaining)/30)),sub['expires_at'])
 user['subscription_photo_granted_at']=now().isoformat()


def reserve_portrait(user):
 ensure(user)
 if 'avatar' in user['photo_reservations']:return False
 if user.get('portrait_credits',0)<=0:return reserve(user,'avatar')
 user['portrait_credits']-=1
 user['photo_reservations']['avatar']={'portrait_credit':True,'started':now().isoformat()}
 return True
