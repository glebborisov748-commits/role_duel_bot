"""Single-use, server checked radio calibration jobs."""
import secrets
import time
import random

def start(user,now=None):
 now=time.time() if now is None else now
 job=user.get('radio_job')
 if job and 0<=now-job['started']<1200:return job
 job={'id':secrets.token_hex(12),'target':[random.randint(2,8) for _ in range(3)],'started':now}
 user['radio_job']=job
 return job

def complete(user,job_id,values,now=None):
 now=time.time() if now is None else now;job=user.get('radio_job')
 if not job or job.get('id')!=job_id:return False
 if not isinstance(values,list) or len(values)!=3 or any(type(v) is not int or not 0<=v<=10 for v in values):return False
 if not 4<=now-job['started']<=1200 or values!=job['target']:return False
 user.pop('radio_job',None)
 return True
