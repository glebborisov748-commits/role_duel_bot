"""One shared schedule: three jobs daily, all six appear within each two-day block."""
import hashlib,random
JOBS=('clicker','catch','courier','workshop','dig','mine')
EVENTS={'clicker':'hack','catch':'catch','courier':'courier','workshop':'pipes','dig':'dig','mine':'mine'}
NAMES={'clicker':'Взлом','catch':'Заказ','courier':'Курьер','workshop':'Трубы','dig':'Раскопки','mine':'Шахта','farm':'Ферма'}
ALIASES={'hacker_combo':'clicker','hack':'clicker'}
def active(day):
 ordinal=day.toordinal();seed=hashlib.sha256(('role-duel-jobs-v1:'+str(ordinal//2)).encode()).digest()
 jobs=list(JOBS);random.Random(seed).shuffle(jobs);return jobs[(ordinal%2)*3:(ordinal%2)*3+3]
def is_open(job,day,bypass=False):return isinstance(job,str) and (job=='farm' or ALIASES.get(job,job) in (JOBS if bypass else active(day)))
def events(day):return {EVENTS[j] for j in active(day)}|{'plant','water','harvest','chat','share'}
def state(day,reset_at,bypass=False):return {'day':day.isoformat(),'active':list(JOBS) if bypass else active(day),'all':list(JOBS),'names':NAMES,'reset_at':reset_at,'bypass':bool(bypass)}
