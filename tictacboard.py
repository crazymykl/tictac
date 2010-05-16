#! /bin/env python
# -*- coding: utf-8 -*-
'''The representation of a grid for genetic tic-tac-toe.'''

class Board(object):
    '''A tic-tac-toe board.'''

    X = 'X'
    O = 'O'
    unresolved = '-'
    draw = 'D'

    transforms = {
        None    : (0, 1, 2, 3, 4, 5, 6, 7, 8),
        'rot90' : (6, 3, 0, 7, 4, 1, 8, 5, 2),
        'rot180': (8, 7, 6, 5, 4, 3, 2, 1, 0),
        'rot270': (2, 5, 8, 1, 4, 7, 0, 3, 6),
        'flip_h': (2, 1, 0, 5, 4, 3, 8, 7, 6),
        'flip_v': (6, 7, 8, 3, 4, 5, 0, 1, 2),
        'flip_d': (0, 3, 6, 1, 4, 7, 2, 5, 8),
        'flip_a': (8, 5, 2, 7, 4, 1, 6, 3, 0),
    }

    def __init__(self, sqr=unresolved*9):
        '''Creates a new board, either empty, or with squares pre-assigned.'''
        self.squares = ''.join(sqr)
        self.move = len([x for x in sqr if x != Board.unresolved])

    def symbol_won(self, symbol):
        '''Check if anyone has won the game.'''
        def all_symbol(indices):
            '''Check if all the indices contain the same symbol.'''
            for index in indices:
                if self.squares[index] != symbol: return False
            return True

        for group in ((0, 1, 2), (3, 4, 5), (6, 7, 8), (0, 3, 6), (1, 4, 7), \
            (2, 5, 8), (0, 4, 8), (2, 4, 6)):
            if all_symbol(group): return True

        return False

    def game_state(self):
        '''Check if there's a winner, or if the board's full without one.'''
        for symbol in Board.X + Board.O:
            if self.symbol_won(symbol): return symbol
        if self.move == 9: return Board.draw
        return Board.unresolved

    def potential_winners(self):
        '''Check who still can win the game.'''
        states = set()
        queue = [self]

        while queue:
            brd = queue.pop()
            if brd.game_state() != Board.unresolved:
                states.add(brd.game_state())
            else:
                queue.extend([brd.make_move(i) for i in brd.legal_moves()])

        return list(states)

    def active_symbol(self):
        '''Check whose turn it is.'''
        return Board.O if self.move % 2 else Board.X

    def legal_moves(self):
        '''Check which moves can be made now.'''
        return [i for i in range(9) if self.squares[i] == Board.unresolved]

    def make_move(self, square):
        '''Returns a board where the active player moved in square.'''
        if square in self.legal_moves():
            sqr  = self.squares[:square]
            sqr += self.active_symbol()
            sqr += self.squares[square+1:]
            return Board(sqr)

    def transform(self, which):
        '''Perform a transform on the board, to check symmetries.'''
        out = Board.transforms[which]
        sqr = self.squares
        sqr_ = list(Board.unresolved*9)
        for old, new in zip(range(9), out):
            sqr_[old] = sqr[new]
        return Board(sqr_)

    def __str__(self):
        '''Returns a human-readable representation of this board.'''
        sqr = self.squares
        return  \
            ' %s | %s | %s\n'% (sqr[0],sqr[1],sqr[2])+ \
            '---+---+---\n'+ \
            ' %s | %s | %s\n'% (sqr[3],sqr[4],sqr[5])+ \
            '---+---+---\n'+ \
            ' %s | %s | %s\n'% (sqr[6],sqr[7],sqr[8])

def play_game(x, o, show=True):
    '''Plays a game of tic-tac-toe between x and o.'''
    players = { Board.X : x, Board.O : o }
    brd = Board()

    while brd.game_state() == Board.unresolved:
        if show: print brd
        move = players[brd.active_symbol()].get_move(brd)
        brd = brd.make_move(move)

    if show:
        print brd
        if brd.game_state() == Board.draw: print "It's a draw!\n"
        else: print "%s won!\n"% brd.game_state()

    return brd.game_state()