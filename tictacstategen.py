#! /bin/env python
# -*- coding: utf-8 -*-

import pickle

class StateMap(object):

    def __init__(self):
        self.index = {}
        self.game  = {}

    def add(self, i, g):
        self.index[g] = i
        self.game [i] = g

    def copy(self, states):
        self.index = states.index
        self.game  = states.game

    def __len__(self): return len(self.game)


statemap = StateMap()

try:
    with open('tictac.dat','rb') as f:
        statemap.copy(pickle.load(f))
except IOError:
    from tictacboard import Board

    print "Generating state data..."

    states = set()
    board = Board()

    def search_states(brd):
        if brd.game_state() != Board.unresolved: return
        states.add(brd.squares)
        for sq in brd.legal_moves():
            search_states(brd.make_move(sq))

    search_states(board)

    for i, state in enumerate(states):
        statemap.add(i, state)

    print "Done!"

    with open('tictac.dat','wb') as f:
        pickle.dump(statemap,f)
