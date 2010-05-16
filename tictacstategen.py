#! /bin/env python
# -*- coding: utf-8 -*-
'''A helper module for generating the map the genome of a Critter represents.'''

import pickle

class StateMap(object):
    '''A data structure mapping board states onto indices, and vice-versa.'''

    def __init__(self):
        '''Creates a new, empty statemap'''
        self.index = {}
        self.game  = {}

    def add(self, idx, game):
        '''Adds a two-way relation between a board state and an index.'''
        self.index[game] = idx
        self.game [idx ] = game

    def copy(self, other):
        '''Copies the values of another statemap.'''
        self.index = other.index.copy()
        self.game  = other.game.copy()

    def __len__(self):
        '''Returns the number of mapped states.'''
        return len(self.game)


statemap = StateMap()

try: # get precomputed statemap
    with open('tictacstates.dat','rb') as f:
        statemap.copy(pickle.load(f))
except IOError: # none exists, make one
    from tictacboard import Board

    print "Generating state data..."

    states = set()
    board = Board()

    def search_states(brd):
        '''Searches for unique, non-decided states to map to indices.'''
        if brd.game_state() != Board.unresolved: return
        for trn in Board.transforms:
            if brd.transform(trn).squares in states: return
        if len(brd.potential_winners()) == 1: return
        states.add(brd.squares)
        for sq in brd.legal_moves():
            search_states(brd.make_move(sq))

    search_states(board)

    for i, state in enumerate(states):
        statemap.add(i, state)

    print "%i states found"% len(statemap)

    # save the statemap to disk is serialized form
    with open('tictacstates.dat','wb') as f:
        pickle.dump(statemap, f)
