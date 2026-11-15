import copy
import unittest
import chess
import online_games as games


class OnlineGamesTests(unittest.TestCase):
    def setUp(self):
        self.accounts={str(i):{'bucks':1000} for i in range(1,5)}
        self.store={}
        self.now=1700000000

    def pair(self,game,bet=100):
        room=games.start(self.store,self.accounts,'1',game,bet,'friend',self.now)
        games.join(self.store,self.accounts,'2',room['id'],self.now)
        return room

    def play(self,room,seat,action,seq=None):
        return games.move(room,self.accounts,room['players'][seat],room['seq'] if seq is None else seq,action,self.now)

    def test_match_escrow_single_refund_and_recovery(self):
        a=games.start(self.store,self.accounts,'1','chess',100,'random',self.now)
        again=games.start(self.store,self.accounts,'1','chess',100,'random',self.now)
        self.assertIs(a,again);self.assertEqual(self.accounts['1']['bucks'],900)
        b=games.start(self.store,self.accounts,'2','chess',100,'random',self.now)
        self.assertIs(a,b);self.assertEqual(sum(u['bucks'] for u in self.accounts.values()),3800)
        # Restart is an exact serialized state restore, not a new deposit.
        import json
        self.store=json.loads(json.dumps(self.store));room=self.store[a['id']]
        games.leave(room,self.accounts,'2')
        self.assertEqual((self.accounts['1']['bucks'],self.accounts['2']['bucks']),(1100,900))
        games.finish(room,0,self.accounts)
        self.assertEqual(self.accounts['1']['bucks'],1100)

    def test_waiting_cancel_expiry_and_wrong_bet_never_take_more(self):
        a=games.start(self.store,self.accounts,'1','dice',500,'friend',self.now)
        b=games.start(self.store,self.accounts,'2','dice',100,'random',self.now)
        self.assertNotEqual(a['id'],b['id'])
        games.expire(self.store,self.accounts,self.now+601)
        self.assertEqual((self.accounts['1']['bucks'],self.accounts['2']['bucks']),(1000,1000))
        games.expire(self.store,self.accounts,self.now+602)
        self.assertEqual(self.accounts['1']['bucks'],1000)

    def test_one_account_one_live_room_and_no_self_match(self):
        room=self.pair('chess')
        other=games.start(self.store,self.accounts,'3','dice',0,'friend',self.now)
        with self.assertRaises(games.GameError):games.join(self.store,self.accounts,'1',other['id'],self.now)
        self.assertEqual(len(room['players']),2)
        self.assertIs(games.join(self.store,self.accounts,'1',room['id'],self.now),room)
        with self.assertRaises(games.GameError):games.join(self.store,self.accounts,'4',room['id'],self.now)
        self.assertEqual(self.accounts['4']['bucks'],1000)

    def test_hidden_dice_and_bid_order_and_challenge(self):
        room=self.pair('dice');room.update(turn=0,dice=[[2,2,3,4,5],[1,1,3,4,6]])
        self.play(room,0,{'type':'bid','count':2,'face':2})
        view=games.view(room,'2')
        self.assertEqual(view['dice'],[1,1,3,4,6]);self.assertNotIn('players_ids',view)
        for bad in [{'type':'bid','count':2,'face':1},{'type':'bid','count':1,'face':6},{'type':'bid','count':11,'face':6}]:
            with self.assertRaises(games.GameError):self.play(room,1,bad)
        self.play(room,1,{'type':'challenge'})
        self.assertEqual(room['counts'],[5,4])
        self.assertEqual(room['reveal']['actual'],2) # Ones are not wild.
        self.assertEqual(room['round'],2)
        self.assertIsNone(room['bid'])

    def test_false_bid_loses_die_and_final_die_settles(self):
        room=self.pair('dice');room.update(turn=0,counts=[1,1],dice=[[2],[3]])
        self.play(room,0,{'type':'bid','count':2,'face':6})
        self.play(room,1,{'type':'challenge'})
        self.assertEqual((room['status'],room['winner']),('done',1))
        self.assertEqual(self.accounts['2']['bucks'],1100)

    def test_connect_four_wins_and_rejects_duplicate_turn(self):
        room=self.pair('connect4');room['turn']=0
        self.play(room,0,{'column':0});seq=room['seq']
        with self.assertRaises(games.GameError):self.play(room,0,{'column':0})
        for col in (1,0,1,0,1,0):self.play(room,room['turn'],{'column':col})
        self.assertEqual(room['winner'],0)
        before=copy.deepcopy(room)
        with self.assertRaises(games.GameError):self.play(room,0,{'column':2},seq)
        self.assertEqual(before,room)

    def test_chess_legal_moves_and_checkmate(self):
        room=self.pair('chess')
        with self.assertRaises(games.GameError):self.play(room,0,{'move':'e2e5'})
        for move in ('f2f3','e7e5','g2g4','d8h4'):self.play(room,room['turn'],{'move':move})
        self.assertEqual(room['winner'],1)
        self.assertEqual(room['reason'],'chess_checkmate')
        self.assertEqual(games.view(room,'1')['legal'],[])

    def test_chess_castling_en_passant_promotion_and_repetition(self):
        room=self.pair('chess',0)
        for move in ('e2e4','a7a6','e4e5','d7d5','e5d6'):self.play(room,room['turn'],{'move':move})
        self.assertIsNone(games.board_for(room).piece_at(chess.D5))
        room['moves']=[];room['turn']=0
        for move in ('g1f3','g8f6','g2g3','g7g6','f1g2','f8g7','e1g1'):self.play(room,room['turn'],{'move':move})
        self.assertEqual(games.board_for(room).piece_at(chess.F1).piece_type,chess.ROOK)
        room['moves']=[];room['turn']=0
        for move in ('a2a4','h7h5','a4a5','h5h4','a5a6','h4h3','a6b7','h3g2','b7a8n'):self.play(room,room['turn'],{'move':move})
        self.assertEqual(games.board_for(room).piece_at(chess.A8).piece_type,chess.KNIGHT)
        room.update(moves=[],turn=0)
        for move in ('g1f3','g8f6','f3g1','f6g8')*2:
            if room['status']=='playing':self.play(room,room['turn'],{'move':move})
        self.assertTrue(games.view(room,room['players'][room['turn']])['claim_draw'])
        self.play(room,room['turn'],{'type':'claim_draw'})
        self.assertEqual(room['winner'],None)
        self.assertEqual(room['status'],'done')

    def test_rps_choices_secret_immutable_and_simultaneous(self):
        room=self.pair('rps');seq=room['seq'];deadline=room['deadline']
        self.play(room,0,{'choice':'rock'})
        self.assertEqual(room['seq'],seq)
        self.assertEqual(room['deadline'],deadline)
        opponent=games.view(room,'2')
        self.assertNotIn('choices',opponent);self.assertFalse(opponent['submitted']);self.assertIsNone(opponent['last'])
        with self.assertRaises(games.GameError):self.play(room,0,{'choice':'paper'})
        self.play(room,1,{'choice':'scissors'},seq)
        self.assertEqual(room['scores'],[1,0]);self.assertEqual(room['seq'],seq+1)
        self.assertEqual(room['choices'],[None,None])
        for _ in range(2):
            self.play(room,1,{'choice':'scissors'});self.play(room,0,{'choice':'rock'})
        self.assertEqual(room['winner'],0)

    def test_timeout_no_moves_draws_rps_and_one_move_wins(self):
        room=self.pair('rps');games.expire(self.store,self.accounts,self.now+46)
        self.assertIsNone(room['winner']);self.assertEqual(self.accounts['1']['bucks'],1000)
        self.accounts['1'].pop('online_room',None);self.accounts['2'].pop('online_room',None)
        room=self.pair('rps');self.play(room,1,{'choice':'paper'})
        games.expire(self.store,self.accounts,self.now+46)
        self.assertEqual(room['winner'],1)
        self.assertEqual(self.accounts['2']['bucks'],1100)

    def test_turn_timeout_and_bot_games_never_mint_bucks(self):
        room=self.pair('chess');games.expire(self.store,self.accounts,self.now+301)
        self.assertEqual(room['winner'],1)
        for game in games.GAMES:
            accounts={'1':{'bucks':1000}};store={}
            room=games.start(store,accounts,'1',game,0,'bot',self.now)
            self.assertIn('bot',room['players'])
            games.leave(room,accounts,'1')
            self.assertEqual(accounts['1']['bucks'],1000)
        with self.assertRaises(games.GameError):games.start({},self.accounts,'1','chess',100,'bot',self.now)

    def test_closed_search_is_not_matched_with_a_later_player(self):
        first=games.start(self.store,self.accounts,'1','chess',100,'random',self.now)
        later=games.start(self.store,self.accounts,'2','chess',100,'random',self.now+20)
        self.assertNotEqual(first['id'],later['id'])
        self.assertEqual(first['status'],'waiting')
        games.expire(self.store,self.accounts,self.now+121)
        self.assertEqual(self.accounts['1']['bucks'],1000)

    def test_non_members_cannot_view_or_move(self):
        room=self.pair('dice')
        with self.assertRaises(games.GameError):games.view(room,'3')
        with self.assertRaises(games.GameError):games.move(room,self.accounts,'3',room['seq'],{'type':'challenge'},self.now)
