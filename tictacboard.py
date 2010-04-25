#! /bin/env python
# -*- coding: utf-8 -*-

class Board(object):

    X = 'X'
    O = 'O'
    unresolved = '-'
    draw = 'D'

    def __init__(self, sqr=unresolved*9):
        self.squares = ''.join(sqr)
        self.move = len(filter(lambda x: x != Board.unresolved, sqr))

    def symbol_won(self,symbol):
        def all_symbol(indices):
            for index in indices:
                if self.squares[index] != symbol: return False
            return True

        for group in ((0, 1, 2), (3, 4, 5), (6, 7, 8), (0, 3, 6), (1, 4, 7), \
            (2, 5, 8), (0, 4, 8), (2, 4, 6)):
                if all_symbol(group): return True

        return False

    def game_state(self):
        for symbol in Board.X + Board.O:
            if self.symbol_won(symbol): return symbol
        if self.move == 9: return Board.draw
        return Board.unresolved

    def active_symbol(self): return Board.O if self.move%2 else Board.X

    def legal_moves(self):
        return filter(lambda i: self.squares[i] == Board.unresolved, range(9))

    def make_move(self, square):
        if square in self.legal_moves():
            sqr  = self.squares[:square]
            sqr += self.active_symbol()
            sqr += self.squares[square+1:]
            return Board(sqr)
        return False

    def __str__(self):
        sqr=self.squares
        return  \
            ' %s | %s | %s\n'%(sqr[0],sqr[1],sqr[2])+ \
            '---+---+---\n'+ \
            ' %s | %s | %s\n'%(sqr[3],sqr[4],sqr[5])+ \
            '---+---+---\n'+ \
            ' %s | %s | %s\n'%(sqr[6],sqr[7],sqr[8])

def play_game(x, o, show=True):
    players = { Board.X : x, Board.O : o }
    brd = Board()

    while brd.game_state() == Board.unresolved:
        if show: print brd
        move = players[brd.active_symbol()].get_move(brd)
        brd = brd.make_move(move)

    if show: print brd

    return brd.game_state()