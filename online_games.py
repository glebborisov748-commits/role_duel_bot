"""Server-authoritative two-player games. Mutations run synchronously in one bot process.

State, escrow and account balances are saved together in the application's atomic JSON file.
Never run multiple bot writers against this file. No network/model calls in this module.
"""
import random
import secrets
import time
import chess

GAMES = ('dice', 'connect4', 'chess', 'rps', 'rps18')
BETS = (0, 100, 500, 1000, 5000)
RNG = random.SystemRandom()
FINISHED = ('done', 'cancelled')


class GameError(ValueError):
    pass


def board_for(room):
    board = chess.Board()
    for move in room['moves']:
        board.push_uci(move)
    return board


def c4_win(board, player):
    for r in range(6):
        for c in range(7):
            for dr, dc in ((0,1),(1,0),(1,1),(1,-1)):
                if all(0 <= r+dr*i < 6 and 0 <= c+dc*i < 7 and board[r+dr*i][c+dc*i] == player+1 for i in range(4)):
                    return True
    return False


def drop(board, col, player):
    if type(col) is not int or col not in range(7) or board[0][col]:
        raise GameError('invalid_move')
    for row in range(5, -1, -1):
        if not board[row][col]:
            board[row][col] = player+1
            return row


def begin(room, now):
    room.update(status='playing', turn=RNG.randrange(2), deadline=now+(300 if room['game']=='chess' else 90), seq=0)
    game = room['game']
    if game == 'connect4':
        room['board'] = [[0]*7 for _ in range(6)]
    elif game == 'chess':
        room.update(moves=[], turn=0)
    elif game == 'dice':
        room.update(counts=[5,5], round=1)
        roll(room)
    else:
        room.update(scores=[0,0], choices=[None,None], last=None, round=1)
        room['deadline'] = now+45


def roll(room):
    room['dice'] = [[RNG.randint(1,6) for _ in range(n)] for n in room['counts']]
    room['bid'] = None


def finish(room, winner, accounts, reason='finished'):
    if room['status'] in FINISHED:
        return
    room.update(status='done', winner=winner, reason=reason, finished=time.time())
    stake = room['bet']
    # Waiting rooms have one escrow deposit. Live rooms have two.
    for seat, uid in enumerate(room['players']):
        if uid == 'bot':
            continue
        amount = stake if winner is None else (stake*len(room['players']) if seat == winner else 0)
        accounts[uid]['bucks'] = accounts[uid].get('bucks',0)+amount
    room['paid'] = True


def expire(store, accounts, now):
    for room in list(store.values()):
        if room['status'] in FINISHED:
            if now-room.get('finished',now) > 86400:
                store.pop(room['id'],None)
            continue
        if now <= room['deadline']:
            continue
        if room['status'] == 'waiting':
            finish(room, None, accounts, 'queue_expired')
        elif room['game'].startswith('rps'):
            choices = room['choices']
            winner = None if all(x is None for x in choices) else next(i for i,x in enumerate(choices) if x is not None)
            finish(room,winner,accounts,'timeout')
        else:
            finish(room,1-room['turn'],accounts,'timeout')


def current(store, accounts, uid):
    code = accounts[uid].get('online_room')
    room = store.get(code)
    return room if room and uid in room['players'] else None


def seat_of(room, uid):
    if uid not in room['players']:
        raise GameError('not_member')
    return room['players'].index(uid)


def start(store, accounts, uid, game, bet=0, kind='random', now=None):
    now = time.time() if now is None else now
    expire(store,accounts,now)
    if game not in GAMES or type(bet) is not int or bet not in BETS or kind not in ('random','friend','bot'):
        raise GameError('invalid_request')
    if kind == 'bot' and bet:
        raise GameError('bot_free_only')
    old = current(store,accounts,uid)
    if old and old['status'] not in FINISHED:
        return old
    if accounts[uid].get('bucks',0) < bet:
        raise GameError('insufficient_bucks')
    if kind == 'random':
        candidates = [r for r in store.values() if r['status']=='waiting' and r['kind']=='random' and r['game']==game and r['bet']==bet and uid not in r['players'] and now-r.get('seen',r['created'])<15]
        if candidates:
            room = min(candidates,key=lambda r:r['created'])
            join(store,accounts,uid,room['id'],now=now)
            return room
    code = secrets.token_hex(4).upper()
    while code in store:
        code = secrets.token_hex(4).upper()
    accounts[uid]['bucks'] = accounts[uid].get('bucks',0)-bet
    room = dict(id=code,game=game,bet=bet,kind=kind,players=[uid],status='waiting',created=now,seen=now,deadline=now+(600 if kind=='friend' else 120),seq=0)
    store[code] = room
    accounts[uid]['online_room'] = code
    if kind == 'bot':
        room['players'].append('bot')
        begin(room,now)
        bot_turn(room,accounts,now)
    return room


def join(store, accounts, uid, code, now=None):
    now = time.time() if now is None else now
    expire(store,accounts,now)
    room = store.get(code)
    if room and uid in room['players']:
        return room
    if not room or room['status']!='waiting' or len(room['players'])!=1:
        raise GameError('room_unavailable')
    old = current(store,accounts,uid)
    if old and old['status'] not in FINISHED:
        raise GameError('already_playing')
    if accounts[uid].get('bucks',0)<room['bet']:
        raise GameError('insufficient_bucks')
    accounts[uid]['bucks'] = accounts[uid].get('bucks',0)-room['bet']
    accounts[uid]['online_room'] = code
    room['players'].append(uid)
    begin(room,now)
    return room


def move(room, accounts, uid, seq, action, now=None):
    now = time.time() if now is None else now
    seat = seat_of(room,uid)
    expire({room['id']:room},accounts,now)
    if room['status']!='playing' or type(seq) is not int or seq != room['seq']:
        raise GameError('stale_move')
    game = room['game']
    revealed = False
    if not game.startswith('rps') and room['turn'] != seat:
        raise GameError('not_your_turn')
    if game == 'connect4':
        col = action.get('column')
        row = drop(room['board'],col,seat)
        room['last'] = {'row':row,'column':col}
        if c4_win(room['board'],seat):
            finish(room,seat,accounts)
        elif all(room['board'][0]):
            finish(room,None,accounts)
        room['turn'] = 1-seat
    elif game == 'chess':
        board = board_for(room)
        if action.get('type') == 'claim_draw':
            if not board.can_claim_draw():
                raise GameError('invalid_move')
            finish(room,None,accounts,'chess_claimed_draw')
            room['seq'] += 1
            return
        try:
            chosen = chess.Move.from_uci(action.get('move',''))
        except (ValueError,TypeError):
            raise GameError('invalid_move')
        if chosen not in board.legal_moves:
            raise GameError('invalid_move')
        room['moves'].append(chosen.uci())
        board.push(chosen)
        room['turn'] = 1-seat
        outcome = board.outcome()
        if outcome:
            winner = None if outcome.winner is None else (0 if outcome.winner else 1)
            finish(room,winner,accounts,'chess_'+outcome.termination.name.lower())
    elif game == 'dice':
        if action.get('type') == 'bid':
            count, face = action.get('count'), action.get('face')
            old = room['bid']
            if type(count) is not int or type(face) is not int or count not in range(1,sum(room['counts'])+1) or face not in range(1,7) or (old and (count,face)<=(old['count'],old['face'])):
                raise GameError('invalid_bid')
            room['bid'] = dict(count=count,face=face,seat=seat)
            room['turn'] = 1-seat
        elif action.get('type') == 'challenge' and room['bid']:
            bid = room['bid']
            actual = sum(hand.count(bid['face']) for hand in room['dice'])
            loser = seat if actual >= bid['count'] else bid['seat']
            room['reveal'] = dict(dice=[list(h) for h in room['dice']],bid=dict(bid),actual=actual,loser=loser,round=room['round'])
            room['counts'][loser] -= 1
            if room['counts'][loser] == 0:
                finish(room,1-loser,accounts)
            else:
                room['round'] += 1
                room['turn'] = loser
                roll(room)
        else:
            raise GameError('invalid_move')
    else:
        choice = action.get('choice')
        if choice not in ('rock','paper','scissors') or room['choices'][seat] is not None:
            raise GameError('invalid_move')
        room['choices'][seat] = choice
        if all(room['choices']):
            revealed = True
            a,b = room['choices']
            winner = None if a==b else (0 if (a,b) in (('rock','scissors'),('paper','rock'),('scissors','paper')) else 1)
            if winner is not None:
                room['scores'][winner] += 1
            room['last'] = dict(choices=list(room['choices']),winner=winner,round=room['round'])
            target = 5 if game=='rps18' else 3
            if winner is not None and room['scores'][winner]>=target:
                finish(room,winner,accounts)
            room['round'] += 1
            room['choices'] = [None,None]
    # Secret submissions never advance the public revision or extend the shared deadline.
    if not game.startswith('rps') or revealed:
        room['seq'] += 1
        room['deadline'] = now+(300 if game=='chess' else 45 if game.startswith('rps') else 90)


def bot_turn(room, accounts, now):
    if 'bot' not in room['players'] or room['status']!='playing':
        return
    seat = room['players'].index('bot')
    game = room['game']
    if game.startswith('rps'):
        if room['choices'][seat] is not None:
            return
        # Independently committed hidden choice, before the human's request is processed.
        action = {'choice':RNG.choice(('rock','paper','scissors'))}
    elif room['turn'] != seat:
        return
    elif game == 'connect4':
        cols = [c for c in range(7) if not room['board'][0][c]]
        col = None
        for who in (seat,1-seat):
            for c in cols:
                trial = [list(row) for row in room['board']]
                drop(trial,c,who)
                if c4_win(trial,who):
                    col = c
                    break
            if col is not None:
                break
        action = {'column':col if col is not None else min(cols,key=lambda c:abs(c-3)+RNG.random())}
    elif game == 'chess':
        board = board_for(room)
        values = {chess.PAWN:1,chess.KNIGHT:3,chess.BISHOP:3,chess.ROOK:5,chess.QUEEN:9,chess.KING:0}
        def score(m):
            board.push(m)
            if board.is_checkmate():
                result = 10000
            else:
                result = sum(values[p.piece_type]*(1 if p.color == (seat==0) else -1) for p in board.piece_map().values())
                # Penalize the opponent's strongest legal capture.
                threats = [values.get((board.piece_at(n.to_square) or chess.Piece(chess.KING,True)).piece_type,0) for n in board.legal_moves if board.is_capture(n)]
                result -= max(threats,default=0)*0.8
                result += RNG.random()*0.2
            board.pop()
            return result
        action = {'move':max(list(board.legal_moves),key=score).uci()}
    else:
        bid = room['bid']
        hand = room['dice'][seat]
        if bid and bid['count'] > hand.count(bid['face'])+room['counts'][1-seat]/6+0.8:
            action = {'type':'challenge'}
        else:
            candidates = [(count,face) for count in range(1,sum(room['counts'])+1) for face in range(1,7) if not bid or (count,face)>(bid['count'],bid['face'])]
            if not candidates:
                action = {'type':'challenge'}
            else:
                count,face = max(candidates,key=lambda cf: hand.count(cf[1])+room['counts'][1-seat]/6-cf[0]-0.04*cf[0])
                action = dict(type='bid',count=count,face=face)
    move(room,accounts,'bot',room['seq'],action,now)


def leave(room, accounts, uid):
    seat = seat_of(room,uid)
    if room['status'] == 'waiting':
        finish(room,None,accounts,'cancelled')
    elif room['status'] == 'playing':
        finish(room,1-seat,accounts,'resigned')
    accounts[uid].pop('online_room',None)


def view(room, uid):
    if not room:
        return None
    seat = seat_of(room,uid)
    game = room['game']
    data = {key:room.get(key) for key in ('id','game','bet','kind','status','turn','seq','deadline','winner','reason','round','scores','last','reveal','counts')}
    data.update(seat=seat,opponent='bot' if 'bot' in room['players'] else 'player',players=len(room['players']))
    if room['status']=='waiting':
        return data
    if game == 'dice':
        data.update(dice=list(room['dice'][seat]),bid=room['bid'])
    elif game == 'chess':
        board = board_for(room)
        data.update(fen=board.fen(),moves=list(room['moves']),check=board.is_check(),claim_draw=board.can_claim_draw() and room['turn']==seat,legal=[m.uci() for m in board.legal_moves] if room['status']=='playing' and room['turn']==seat else [])
    elif game == 'connect4':
        data['board'] = [list(row) for row in room['board']]
    else:
        data.update(submitted=room['choices'][seat] is not None)
    return data
