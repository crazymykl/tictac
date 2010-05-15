#! /bin/env python
# -*- coding: utf-8 -*-

from tictacboard import Board, play_game
from tictacstategen import statemap
from tictacAI import Critter, Population
import sys

class Human(object):

    def get_move(self, brd):
        move=''
        while not move in brd.legal_moves():
            try: move=int(raw_input("%s's move? "%brd.active_symbol()))-1
            except ValueError: pass
        return move

def trial(home, num=500):
    wins = 0
    draws = 0
    print "Beginning trials..."

    for i in range(num):
        cr = Critter()
        game = play_game(home, cr, False)
        if game == Board.X: wins += 1
        elif game == Board.draw: draws += 1
        game = play_game(cr, home, False)
        if game == Board.O: wins += 1
        elif game == Board.draw: draws += 1

    return (100. * wins / (num * 2.), 100. * draws / (num * 2.))

if __name__ == "__main__":
    p= Population(int(sys.argv[1]),int(sys.argv[2]))
    print "%f%% wins, %f%% draws"%trial(p)
    while True:
        print "---starting game---"
        print play_game(p, Human()), "won!\n"
