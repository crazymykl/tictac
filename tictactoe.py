#! /bin/env python
# -*- coding: utf-8 -*-
'''The driver module for genetic tic-tac-toe.'''

from tictacboard import Board, play_game
from tictacAI import Critter, Population, Player
import sys

class Human(Player):
    '''A human player of tic-tac-toe.'''

    def get_move(self, brd):
        '''Asks a user to select a move.'''
        move = ''
        while not move in brd.legal_moves():
            prompt = "%s's move? "% brd.active_symbol()
            try: move = int(raw_input(prompt))-1
            except ValueError: pass # keep trying on nonsense
        return move

def trial(home, num=500):
    '''Tests the home player versus num Critters.'''
    wins = 0
    draws = 0
    print "Beginning trials..."

    for _ in range(num):
        crit = Critter()
        game = play_game(home, crit, False)
        if game == Board.X: wins += 1
        elif game == Board.draw: draws += 1
        game = play_game(crit, home, False)
        if game == Board.O: wins += 1
        elif game == Board.draw: draws += 1

    return (100. * wins / (num * 2.), 100. * draws / (num * 2.))

if __name__ == "__main__":
    if len(sys.argv)<3: print "Usage %s pop_size gens"% sys.argv[0]
    p = Population(int(sys.argv[1]), int(sys.argv[2]))
    print "%f%% wins, %f%% draws"% trial(p)
    x, o = p, Human()
    while True:
        print "---starting game---"
        play_game(x, o)
        x, o = o, x