#! /bin/env python
# -*- coding: utf-8 -*-
'''AI module for genetic tic-tac-toe.'''
import multiprocessing, zlib, os
from random import random, choice
from itertools import izip, count
from tictacboard import Board, play_game
from tictacstategen import statemap
from time import time, localtime

def humanize_dt(start, end):
    '''Gives a human-readable time difference between start and end.'''
    delta = end - start
    days , delta = divmod(delta, 24 * 60 * 60)
    hours, delta = divmod(delta, 60 * 60)
    mins , secs  = divmod(delta, 60)
    ret = ''
    if days : ret += "%id " % days
    if hours: ret += "%ih " % hours
    if mins : ret += "%im " % mins
    if secs : ret += "%.2fs"% secs
    return ret

def restore(size, perm=True):
    '''Loads some saved data about a Population from a file on disk.
    Returns the generation count and the Critters themselves.'''
    filename = 'population' if perm else 'temp'
    filename += '%s.dat'% size
    with open(filename,'rb') as f:
        if perm: print "Loading old population"
        data = zlib.decompress(f.read()).split('\n')
        generation = int(data.pop())
        critters = [Critter(line) for line in data]
        if perm: print "At generation %i"% generation
        return generation, critters

def gauntlet(data):
    '''Determines the fitness of Critters in a Population by having them play
    a tournament of tic-tac-toe.'''
    i, sz = data
    _, critters = restore(sz, False)
    x = critters[i]
    ret = [play_game(x, o, False) for o in critters]
    print "evaluated %i of %i"% (i+1, sz)
    return ret

class Player(object): pass

class Critter(Player):
    '''A Critter is a tic-tac-toe-playing organism. It is usually found in
    Populations.'''

    def __init__(self, chromosome=None, score=0):
        '''Constructs a critter, either from a specified chromosome or
        randomly.'''
        if chromosome is None: self.randomize()
        else: self.chromosome = chromosome
        self.score = score

    def randomize(self):
        '''Creates a critter with a wholly random chromosome. All genes are
        assigned random legal values.'''
        chromosome = [None]*len(statemap)
        for k, v in statemap.game.iteritems():
            valid_moves = Board(v).legal_moves()
            chromosome[k] = str(choice(valid_moves))
        self.chromosome = ''.join(chromosome)

    def mutate(self):
        '''Mutates a Critter, giving each gene a 10% chance to become some
        random new legal value.'''
        mutant = self.reproduce(Critter(score=self.score-1), .1)
        self.chromosome = mutant.chromosome

    def reproduce(self, partner, thresh=.3):
        '''Produces a new Critter that is the spawn of this and partner.
        Genes have a chance equal to thresh to come from the lower-scoring
        parent.'''
        baby_chrome = [None]*len(statemap)
        if self.score >= partner.score:
            dominant  = self.chromosome
            recessive = partner.chromosome
        else:
            dominant  = partner.chromosome
            recessive = self.chromosome
        for i in xrange(len(statemap)):
            baby_chrome[i] = dominant[i] if random() > thresh \
                else recessive[i]
        return Critter(''.join(baby_chrome))

    def get_move(self, brd):
        '''Gets the move encoded the chromosome, if any.
        Otherwise, picks randomly.'''
        for trn in Board.transforms: # we need to check all the transforms
            sqr = brd.transform(trn).squares
            if sqr in statemap.index: # this board fits
                move = self.chromosome[statemap.index[sqr]]
                return Board.transforms[trn][int(move)] # undo transform
        return choice(brd.legal_moves()) # fallback for states that are decided

    def __str__(self):
        '''Printing a critter prints its chromosome.'''
        return self.chromosome

class Population(Player):
    '''A Population is a collestion of Critters, vying for survival through
    tic-tac-toe.'''

    def __init__(self, size=1000, gens=100, survival=.15, dom_thresh=.2,
                        mutation=.05, win_value=4, loss_cost=15):
        '''Creates a new Population, with tunables galore'''
        self.size       = size
        self.survival   = survival
        self.mutation   = mutation
        self.win_value  = win_value
        self.loss_cost  = loss_cost
        self.dom_thresh = dom_thresh
        self.pool       = multiprocessing.Pool()

        try: self.generation, self.critters = restore(size,True)
        except IOError:
            print "Seeding population of size", size
            self.generation = 0
            self.critters = [Critter() for _ in xrange(size)]
            self.select()

        self.evolve(gens)
        self.pool.close()

    def evolve(self, gens):
        '''Does the real crunchy work of evolving the Population.'''
        while self.generation < gens:
            print "Propogating gen %s of %s"% (self.generation + 1, gens)
            start = time()
            self.propogate()
            self.select()
            t = localtime()
            self.generation += 1
            print "[%02i:%02i:%02i] gen %s took %s"% \
                (t.tm_hour, t.tm_min, t.tm_sec, self.generation, \
                humanize_dt(start, time()))
            self.save()

        print "Evolution Complete!"

    def select(self):
        '''Runs the Critters through a gauntlet, determining which are the
        most fit. Sorts them accordingly.'''
        print "Determing fitnesses..."
        self.save(False) # the worker threads need to read state from disk
        size = (self.size for i in xrange(self.size))
        results = self.pool.map(gauntlet, izip(count(), size))
        os.remove("temp%s.dat"% self.size)
        for games, x in izip(results, self.critters):
            for winner, o in izip(games, self.critters):
                if winner == Board.X:
                    x.score += self.win_value
                    o.score -= self.loss_cost
                elif winner == Board.O:
                    o.score += self.win_value
                    x.score -= self.loss_cost
        self.critters.sort(key=lambda x: x.score, reverse=True)

    def propogate(self):
        '''Culls those unfit to survive, then produces the offspring of the
        most fit Critters.'''
        survivors = self.critters[:int(self.size*self.survival)]
        babies = []
        while len(babies) + len(survivors) < self.size:
            baby = choice(survivors).reproduce(choice(survivors), \
                self.dom_thresh)
            if random() < self.mutation: baby.mutate()
            babies.append(baby)
        for critter in survivors: critter.score = 0
        self.critters = survivors + babies

    def get_move(self, brd):
        '''Gives the move the most fit Critter thinks is best.'''
        return self.critters[0].get_move(brd)

    def save(self, perm=True):
        '''Writes some information about this population to disk.'''
        def _save(perm):
            '''Does the actual saving.'''
            filename = 'population' if perm else 'temp'
            filename += '%s.dat'% self.size
            with open(filename, 'wb') as f:
                data = ''
                for guy in self.critters:
                    data += (guy.chromosome+'\n')
                data += str(self.generation)
                compr = zlib.compress(data)
                f.write(compr)
            ratio = float(len(compr)) / len(data) * 100
            if perm: print "Saved! Compression ratio: %4.2f%%"% ratio

        try:
            if perm: print "Saving to disk..."
            _save(perm)
        except KeyboardInterrupt as e:
            print "Completing save before exitting..."
            _save(perm)
            raise KeyboardInterrupt(e)
