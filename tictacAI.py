#! /bin/env python
# -*- coding: utf-8 -*-

from random import random, choice
from tictacboard import Board, play_game
from tictacstategen import statemap

class Critter(object):

    def __init__(self, chromosome=None):
        if chromosome is None: self.randomize()
        else:
            assert(len(chromosome) == len(statemap))
            self.chromosome = chromosome
        self.score = 0

    def random_gene(self, idx):
        valid_moves = Board(statemap.game[idx]).legal_moves()
        self.cromosome[idx] = str(choice(valid_moves))

    def randomize(self):
        chromosome = [None]*len(statemap)
        for k, v in statemap.game.iteritems():
            valid_moves = Board(v).legal_moves()
            chromosome[k] = str(choice(valid_moves))
        self.chromosome = chromosome

    def mutate(self):
        self.chromosome = self.reproduce(Critter()).chromosome

    def reproduce(self, partner):
        baby_chrome = [None]*len(statemap)
        for i in range(len(statemap)):
            baby_chrome[i] = choice((self.chromosome[i],partner.chromosome[i]))
        return Critter(baby_chrome)

    def get_move(self, brd):
        return int(self.chromosome[statemap.index[brd.squares]])

class Population(object):

    def __init__(self, size=1000 ,gens=100, survival=.15, mutation=.02, win_val=2, loss_val=5):
        self.size = size
        self.survival = survival
        self.mutation = mutation
        self.win_val  = win_val
        self.loss_val = loss_val
        print "Seeding population of size", size
        self.critters = [Critter() for i in xrange(size)]
        self.select()
        self.evolve(gens)
        print ''.join(self.critters[0].chromosome)

    def evolve(self, gens):
        for i in xrange(gens):
            print "Propogating gen %s of %s"%(i+1, gens)
            self.propogate()
            self.select()
        print "Evolution Complete!"

    def select(self):
        print "Determing fitnesses..."
        for x in self.critters:
            for o in self.critters:
                winner = play_game(x, o, False)
                if winner == Board.X:
                    x.score += self.win_val
                    o.score -= self.loss_val
                elif winner == Board.O:
                    o.score += self.win_val
                    x.score -= self.loss_val
        self.critters.sort(key=lambda x: x.score, reverse=True)

    def propogate(self):
        survivors = self.critters[:int(self.size*self.survival)]
        for critter in survivors: critter.score = 0
        babies = []
        while len(babies) + len(survivors)< self.size:
            baby = choice(survivors).reproduce(choice(survivors))
            if random() < self.mutation: baby.mutate()
            babies.append(baby)
        for critter in survivors: critter.score = 0
        self.critters = survivors + babies

    def get_move(self,brd): return self.critters[0].get_move(brd)


class PerfectPlayer(object):

    def get_move(self, brd):
        def win():
            for move in moves:
                if brd.make_move(move).game_state == symbol:
                    return move
            return None
        def poo(): pass

        symbol = brd.active_symbol()
        moves  = brd.legal_moves()
