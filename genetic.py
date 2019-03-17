import numpy as np
import random as rnd

class GeneticAlgorithm(object):
    def __init__(self):
        self.n_population = 40      # Size of population
        self.dim = 0                # Vectors dimension
        self.minvals = None         # Minimal values
        self.maxvals = None         # Maximal values
        self.population = 0         # Population matrix (n_population x dim)
        self.mutation_factor = 10    # Factor of mutation
        self.mutation_prob = 0.2    # Probability of mutation
        self.n_iters = 300          # Maximal number of iterations
        self.func = None            # Fitness function
        self.display = True         # Display information
        self.n_mutants = 10         # Number of mutants
        self.n_children = 10        # Number of children
        self.n_stability = 50       # Number of constant minvals to break cycle

    def set_minvals(self, mv):
        if isinstance(mv, list) or isinstance(mv, tuple):
            self.dim = len(mv)
            self.minvals = np.array(mv)
        else:
            if self.dim == 0:
                print('Initiate dimensions first!!')
                return
            self.minvals = np.array([mv] * self.dim)

    def set_maxvals(self, mv):
        if isinstance(mv, list) or isinstance(mv, tuple):
            self.dim = len(mv)
            self.maxvals = np.array(mv)
        else:
            if self.dim == 0:
                print('Initiate dimensions first!!')
                return
            self.maxvals = np.array([mv] * self.dim)

    def init_population(self):
        self.population = np.round(np.random.rand(self.n_population, self.dim) * (self.maxvals - self.minvals) + self.minvals).astype(int)

    def check_minmax(self, arr):
        return (arr - self.minvals) % (self.maxvals - self.minvals + 1) + self.minvals

    def mutation(self, arr):
        mutants = arr[np.random.randint(0, arr.shape[0], self.n_mutants), :]
        for i in range(self.n_mutants):
            mutants[i, rnd.randint(0, self.dim - 1)] += rnd.randint(-self.mutation_factor, self.mutation_factor)
        return self.check_minmax(mutants)

    def crossover(self, arr):
        children = np.zeros((self.n_children, self.dim), dtype=int)
        for i in range(0, self.n_children, 2):
            ids = rnd.sample(range(arr.shape[0]), 2)
            parent1 = arr[ids[0], :]
            parent2 = arr[ids[1], :]
            s = rnd.sample(range(1, self.dim), 2)
            children[i, :] = np.hstack((parent1[:min(s)], parent2[min(s):max(s)], parent1[max(s):]))
            children[i + 1, :] = np.hstack((parent2[:min(s)], parent1[min(s):max(s)], parent2[max(s):]))
        return self.check_minmax(children)

    def get_bests(self, n):
        mins = self.func(self.population)
        indexs = np.argsort(mins)[:n]
        return mins[indexs], self.population[indexs, :]

    def minimize(self, func):
        self.func = func
        self.init_population()

        minf, minx = self.get_bests(1)
        if self.display:
            print('Initialization. min_f={0}'.format(minf[0]))

        counter = 0
        best_min = minf

        for iter in range(self.n_iters):
            children = self.crossover(self.population)
            self.population = np.vstack((self.population, children))
            mutants = self.mutation(self.population)
            self.population = np.vstack((self.population, mutants))
            minvals, self.population = self.get_bests(self.n_population)
            index = np.argmin(minvals)
            if minvals[index] < best_min:
                best_min = minvals[index]
                counter = 0
            elif minvals[index] == best_min:
                counter += 1
            if self.display:
                print('Iteration {0}. min_f={1}'.format(iter + 1, minvals[index]))
            if counter >= self.n_stability:
                break
        return best_min, self.population[index, :]
