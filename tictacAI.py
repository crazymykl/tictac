#! /bin/env python
# -*- coding: utf-8 -*-

import pickle, multiprocessing
from random import random, choice
from itertools import izip, count
from tictacboard import Board, play_game
from tictacstategen import statemap
from time import time, localtime

def humanize_dt(start, end):
    delta = end - start
    days , delta = divmod(delta, 24 * 60 * 60)
    hours, delta = divmod(delta, 60 * 60)
    mins , secs  = divmod(delta, 60)
    ret=''
    if days : ret += "%id "%days
    if hours: ret += "%ih "%hours
    if mins : ret += "%im "%mins
    if secs : ret += "%.2fs"%secs
    return ret

def gauntlet(data):
    i, x, Os = data
    ret = [play_game(x, o, False) for o in Os]
    i += 1
    print "evaluated %i of %i"%(i, len(Os))
    return ret

class Critter(object):

    def __init__(self, chromosome=None):
        if chromosome is None: self.randomize()
        else: self.chromosome = chromosome
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
        if self.score >= partner.score:
            dominant  = self.chromosome
            recessive = partner.chromosome
        else:
            dominant  = partner.chromosome
            recessive = self.chromosome
        for i in xrange(len(statemap)):
            baby_chrome[i] = dominant[i] if random() > .3 else recessive[i]
        return Critter(baby_chrome)

    def get_move(self, brd):
        return int(self.chromosome[statemap.index[brd.squares]])

class Population(object):

    def __init__(self, size=1000 ,gens=100, survival=.15,
                        mutation=.02, win_val=2, loss_val=5):
        self.size = size
        self.survival = survival
        self.mutation = mutation
        self.win_val  = win_val
        self.loss_val = loss_val
        self.generation = 0
        self.pool = multiprocessing.Pool()

        try:
            with open('population%s.dat'%self.size,'rb') as f:
                pop = pickle.load(f)
                if pop.size == self.size and pop.survival == self.survival and \
                    pop.loss_val == self.loss_val and pop.win_val == self.win_val \
                    and pop.mutation == self.mutation:
                        self.critters = pop.critters
                        self.generation = pop.generation
        except IOError: pass

        if self.generation == 0:
            print "Seeding population of size", size
            self.critters = [Critter() for i in xrange(size)]
            self.select()
        self.evolve(gens)

    def evolve(self, gens):
        while self.generation < gens:
            print "Propogating gen %s of %s"%(self.generation + 1, gens)
            start = time()
            self.propogate()
            self.select()
            self.generation += 1
            t=localtime()
            print "[%02i:%02i:%02i] gen %s took %s"% \
                (t.tm_hour, t.tm_min, t.tm_sec, self.generation, \
                humanize_dt(start, time()))
            print "Saving to disk..."
            pool = self.pool
            self.pool = None
            try:
                with open('population%s.dat'%self.size,'wb') as f:
                    pickle.dump(self,f)
            except KeyboardInterrupt as e:
                print "Completing save before exitting..."
                with open('population%s.dat'%self.size,'wb') as f:
                    pickle.dump(self,f)
                print "Saved!"
                raise KeyboardInterrupt(e)
            self.pool = pool
        print "Evolution Complete!"

    def select(self):
        print "Determing fitnesses..."
        all_critters=(self.critters for i in xrange(self.size))
        results = self.pool.map(gauntlet, \
            izip(count(), self.critters, all_critters))
        for games, x in izip(results, self.critters):
            for winner, o in izip(games, self.critters):
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
        while len(babies) + len(survivors) < self.size:
            baby = choice(survivors).reproduce(choice(survivors))
            if random() < self.mutation: baby.mutate()
            babies.append(baby)
        for critter in survivors: critter.score = 0
        self.critters = survivors + babies

    def get_move(self,brd): return self.critters[0].get_move(brd)

