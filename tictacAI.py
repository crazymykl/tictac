#! /bin/env python
# -*- coding: utf-8 -*-

import multiprocessing, zlib
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

def restore(size, verbose=True):
    with open('population%s.dat'%size,'rb') as f:
        if verbose: print "Loading old population"
        data = zlib.decompress(f.read()).split('\n')
        generation = int(data.pop())
        critters = [Critter(line) for line in data]
        if verbose: print "At generation %i"%generation
        return generation, critters

def gauntlet(data):
    i, sz = data
    _ ,critters = restore(sz, False)
    x = critters[i]
    ret = [play_game(x, o, False) for o in critters]
    print "evaluated %i of %i"%(i+1, sz)
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
        self.pool = multiprocessing.Pool()

        try: self.generation, self.critters = restore(size)
        except IOError:
            print "Seeding population of size", size
            self.generation = 0
            self.critters = [Critter() for i in xrange(size)]
            self.save()
            self.select()

        self.evolve(gens)
        self.pool.close()

    def evolve(self, gens):
        while self.generation < gens:
            print "Propogating gen %s of %s"%(self.generation + 1, gens)
            start = time()
            self.propogate()
            self.save()
            self.select()
            t=localtime()
            self.generation += 1
            print "[%02i:%02i:%02i] gen %s took %s"% \
                (t.tm_hour, t.tm_min, t.tm_sec, self.generation, \
                humanize_dt(start, time()))
            self.save(True)

        print "Evolution Complete!"

    def select(self):
        print "Determing fitnesses..."
        size = (self.size for i in xrange(self.size))
        results = self.pool.map(gauntlet, izip(count(), size))
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
        babies = []
        while len(babies) + len(survivors) < self.size:
            baby = choice(survivors).reproduce(choice(survivors))
            if random() < self.mutation: baby.mutate()
            babies.append(baby)
        for critter in survivors: critter.score = 0
        self.critters = survivors + babies

    def get_move(self,brd): return self.critters[0].get_move(brd)

    def save(self, verbose=False):
        def _save(verbose):
            with open('population%s.dat'%self.size,'wb') as f:
                data = ''
                for guy in self.critters:
                    data += (''.join(guy.chromosome)+'\n')
                data += str(self.generation)
                compr = zlib.compress(data)
                f.write(compr)
            ratio = float(len(compr)) / len(data) * 100
            if verbose: print "Saved! Compression ratio: %4.2f%%"%ratio

        try:
            if verbose: print "Saving to disk..."
            _save(verbose)
        except KeyboardInterrupt as e:
            print "Completing save before exitting..."
            _save(True)
            raise KeyboardInterrupt(e)
