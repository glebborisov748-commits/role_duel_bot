"""Two small server-owned work games. No stakes, client-supplied payouts or hidden-state leaks."""
import secrets
import time

GOAL = list(range(1, 9)) + [0]
PUZZLE_REWARD = 110
REST = 30

class GameError(ValueError):
    pass


def neighbors(index):
    return [i for i in range(9) if abs(i//3-index//3)+abs(i%3-index%3)==1]


def snapshot(user, game, now=None):
    now = time.time() if now is None else now
    run = user.get(game+'_job')
    result = {'run':None,'ready_in':max(0, int(user.get(game+'_ready_at',0)-now+0.999)),
              'reward':PUZZLE_REWARD if game=='puzzle' else 180}
    if not run:
        return result
    public = {k:run[k] for k in ('id','revision','status','moves')}
    if game=='puzzle':
        public.update(board=list(run['board']))
    else:
        public.update(pending=run['pending'],opened=dict(run['opened']),safe_left=sum(v>0 for i,v in enumerate(run['contents']) if str(i) not in run['opened']),
                      unopened=9-len(run['opened']),max_open=5)
        # Contents become visible only after the run is irreversibly ended.
        if run['status'] in ('damaged','paid'):
            public['revealed']=list(run['contents'])
    result['run']=public
    return result


def action(user, game, body, now=None, rng=None):
    now = time.time() if now is None else now
    rng = secrets.SystemRandom() if rng is None else rng
    if game not in ('puzzle','warehouse') or not isinstance(body,dict):
        raise GameError('Неизвестная игра')
    kind=body.get('action');run=user.get(game+'_job')
    if kind=='start':
        if run and run['status'] in ('active','ready'):
            return 0
        if user.get(game+'_ready_at',0)>now:
            raise GameError('Небольшая пауза перед новым заданием')
        run=dict(id=secrets.token_hex(12),revision=0,status='active',moves=0,started=now,last=0)
        if game=='puzzle':
            # Shuffle by legal moves: every board is solvable. Avoid immediate undo.
            board=list(GOAL);blank=8;previous=None
            for _ in range(36):
                choices=[i for i in neighbors(blank) if i!=previous];nxt=rng.choice(choices)
                board[blank],board[nxt]=board[nxt],board[blank];previous,blank=blank,nxt
            if board==GOAL:
                nxt=neighbors(blank)[0];board[blank],board[nxt]=board[nxt],board[blank]
            run['board']=board
        else:
            contents=[0,0,16,20,24,28,32,42,60];rng.shuffle(contents)
            run.update(contents=contents,pending=0,opened={})
        user[game+'_job']=run
        return 0
    if not run or body.get('id')!=run['id']:
        raise GameError('Задание устарело. Обнови страницу')
    if run['status'] in ('won','paid','damaged'):
        return 0
    if type(body.get('revision')) is not int or body['revision']!=run['revision']:
        raise GameError('Ход уже изменился. Попробуй ещё раз')
    if game=='puzzle' and kind=='move':
        index=body.get('index');board=run['board'];blank=board.index(0)
        if type(index) is not int or index not in neighbors(blank):
            raise GameError('Двигать можно только плитку рядом с пустым местом')
        candidate=list(board);candidate[blank],candidate[index]=candidate[index],candidate[blank]
        run.update(board=candidate,moves=run['moves']+1,revision=run['revision']+1,last=now)
        if candidate==GOAL:
            run['status']='won';user[game+'_ready_at']=now+REST
            return PUZZLE_REWARD
        return 0
    if game=='warehouse' and kind=='cashout':
        if not run['pending']:
            raise GameError('Сначала открой целый ящик')
        payout=run['pending'];run.update(status='paid',revision=run['revision']+1,last=now)
        user[game+'_ready_at']=now+REST
        return payout
    if game=='warehouse' and kind=='open' and run['status']=='active':
        index=body.get('index')
        if type(index) is not int or not 0<=index<9 or str(index) in run['opened']:
            raise GameError('Выбери закрытый ящик')
        value=run['contents'][index];run['opened'][str(index)]=value
        run.update(moves=run['moves']+1,revision=run['revision']+1,last=now)
        if not value:
            run.update(status='damaged',pending=0);user[game+'_ready_at']=now+REST
        else:
            run['pending']=min(180,run['pending']+value)
            if len(run['opened'])>=5:
                run['status']='ready'
        return 0
    raise GameError('Этот ход недоступен')
