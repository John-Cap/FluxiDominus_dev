from deap import base, creator, tools, algorithms
import random
import numpy as np
import matplotlib.pyplot as plt
from time import sleep
from scipy.interpolate import griddata

from ReactionSimulation.fakeReactionLookup import ReactionLookup
class ReactionGAOptimizer:
    def __init__(self, reactionLookup, pop_size=100, cxpb=0.7, mutpb=0.3, ngen=100, 
                 restart_threshold=10, local_maxima_exclDist=5, 
                 x_min=0, x_max=100, y_min=0, y_max=100):
        self.reactionLookup = reactionLookup
        self.pop_size = pop_size
        self.cxpb = cxpb
        self.mutpb = mutpb
        self.ngen = ngen
        self.restart_threshold = restart_threshold
        self.local_maxima = []  # Local maxima list
        self.local_maxima_exclDist = local_maxima_exclDist
        self.local_maxima_exclDist_max = 10
        self.targetYield = 0.90

        # Ranges for X and Y
        self.x_min = x_min
        self.x_max = x_max
        self.y_min = y_min
        self.y_max = y_max
        
        self._bracketCounter=0
        self._currBracket=None
        self.brackets={}

        self.experiment_counter = 0

        # GA setup using DEAP
        creator.create("FitnessMax", base.Fitness, weights=(1.0,))
        creator.create("Individual", list, fitness=creator.FitnessMax)

        # Register attributes with separate ranges
        self.toolbox = base.Toolbox()
        self.toolbox.register("attr_x", random.uniform, self.x_min, self.x_max)
        self.toolbox.register("attr_y", random.uniform, self.y_min, self.y_max)
        self.toolbox.register("individual", tools.initCycle, creator.Individual, 
                              (self.toolbox.attr_x, self.toolbox.attr_y), n=1)
        self.toolbox.register("population", tools.initRepeat, list, self.toolbox.individual)

        # GA operations
        self.toolbox.register("evaluate", self.evaluate)
        self.toolbox.register("mate", tools.cxBlend, alpha=0.5)
        self.toolbox.register("mutate", tools.mutGaussian, mu=0, sigma=10, indpb=0.2)
        self.toolbox.register("select", tools.selTournament, tournsize=3)
        
        # Visualization setup
        self.fig, self.ax = plt.subplots()
        self.surf = None
        
    def addBracket(self,bracket,bracketName=None): #bracket = {"x": (4, 100), "y": (1, 60)}
        if bracketName is None:
            bracketName=self._bracketCounter
            self._bracketCounter+=1
        self.brackets[bracketName]=bracket
        return bracketName

    def selectBracket(self,idx):
        if len(self.brackets)==0:
            print("No brackets set!")
            return None
        elif not (idx in self.brackets):
            print(f"Bracket with index '{idx}' not found!")
            return None
        elif len(self.brackets)==1 and idx != self.brackets.keys()[0]:
            print(f"Unknown bracket '{idx}', switching to default")
            return None
        
                
    def mutate(self, individual):
        self.toolbox.mutate(individual)
        # Clip each axis to its defined range
        individual[0] = max(self.x_min, min(self.x_max, individual[0]))  # X-axis
        individual[1] = max(self.y_min, min(self.y_max, individual[1]))  # Y-axis
        return individual,

    def evaluate(self, individual):
        """
        Evaluate the yield of an individual, and detect if it's a local maximum.
        """
        x, y = individual
        self.experiment_counter += 1  # Increment the experiment counter
        yield_value = self.reactionLookup.getYield(x, y)

        # Check if this yield is a local maximum compared to neighboring individuals
        is_local_max = self.is_local_maximum(x, y, yield_value)
        if is_local_max:
            self.local_maxima.append((x, y, yield_value))

        return yield_value,  # DEAP expects a tuple

    def is_local_maximum(self, x, y, yield_value):
        """
        Check if a given point is a local maximum by comparing it to nearby points.
        """
        for other_x, other_y, other_yield in self.local_maxima:
            distance = np.sqrt((x - other_x)**2 + (y - other_y)**2)
            if distance < self.local_maxima_exclDist:  # Define a neighborhood radius to consider
                if yield_value < other_yield:
                    self.local_maxima_exclDist=self.local_maxima_exclDist*-0.05 + self.local_maxima_exclDist
                    if self.local_maxima_exclDist < 0:
                        self.local_maxima_exclDist=0
                    return False
        #self.local_maxima_exclDist=self.local_maxima_exclDist*0.05 + self.local_maxima_exclDist
        if self.local_maxima_exclDist_max < self.local_maxima_exclDist:
            self.local_maxima_exclDist=self.local_maxima_exclDist_max
        return True
    
    def restart_population(self, population):
        """
        Restart the population by generating new random individuals.
        """
        return [self.toolbox.individual() for _ in range(len(population))]

    def plot_population(self, population):
        """
        Plot the population on the yield surface.
        """
        # Clear previous plot
        self.ax.clear()

        # Plot the yield surface
        x = self.reactionLookup.data[:, 0]
        y = self.reactionLookup.data[:, 1]
        z = self.reactionLookup.data[:, 2]
        xi = np.linspace(x.min(), x.max(), 100)
        yi = np.linspace(y.min(), y.max(), 100)
        X, Y = np.meshgrid(xi, yi)
        Z = griddata((x, y), z, (X, Y), method='cubic')
        self.ax.contourf(X, Y, Z, levels=50, cmap="viridis", alpha=0.7)

        # Plot population locations
        pop_coords = np.array([[ind[0], ind[1]] for ind in population])
        self.ax.scatter(pop_coords[:, 0], pop_coords[:, 1], color="red", label="Population", alpha=0.8)

        # Label and update the plot
        self.ax.set_title(f"Generation {self.current_generation}: Best Yield = {self.best_yield:.4f}")
        self.ax.set_xlabel("X (Temperature)")
        self.ax.set_ylabel("Y (Time)")
        self.ax.legend()
        plt.pause(0.1)
        
    def optimize(self):
        """
        Perform optimization with visualization, local maxima detection, and progress tracking.
        """
        #Set brackets
        
        population = self.toolbox.population(n=self.pop_size)
        self.best_yield = -float("inf")
        best_solution = None
        no_improvement_counter = 0

        for gen in range(self.ngen):
            self.current_generation = gen  # Track the current generation

            # Apply GA operations
            offspring = algorithms.varAnd(population, self.toolbox, cxpb=self.cxpb, mutpb=self.mutpb)
            fits = list(map(self.toolbox.evaluate, offspring))
            for ind, fit in zip(offspring, fits):
                ind.fitness.values = fit

            # Select the next generation population
            population = self.toolbox.select(offspring, k=len(population))

            # Track the best solution
            current_best = tools.selBest(population, k=1)[0]
            current_yield = self.reactionLookup.getYield(*current_best)

            if current_yield > self.best_yield:
                self.best_yield = current_yield
                best_solution = current_best
                no_improvement_counter = 0
            else:
                no_improvement_counter += 1

            # Restart if no improvement for restart_threshold generations
            if no_improvement_counter >= self.restart_threshold:
                print(f"Restarting population at generation {gen}")
                population = self.restart_population(population)
                no_improvement_counter = 0

            # Visualize population on the yield surface
            self.plot_population(population)

            if current_yield > self.targetYield:
                print(f"Reached target yield with {current_yield*100}%!")
                return best_solution[0], best_solution[1], self.best_yield

        print(f"Total Experiments: {self.experiment_counter}")
        return best_solution[0], best_solution[1], self.best_yield

    def select(self, population):
        """
        Modify the selection process to penalize individuals near local maxima.
        """
        # Filter individuals that are too close to any local maxima
        penalized_population = []
        for ind in population:
            x, y = ind
            if self.is_near_local_maxima(x, y):
                # Apply a penalty by assigning a low fitness value
                ind.fitness.values = (-float('inf'),)
            else:
                # Keep original fitness
                ind.fitness.values = self.evaluate(ind)
            penalized_population.append(ind)
        
        # Return the selection based on the penalized individuals
        return tools.selTournament(penalized_population, tournsize=3)

    def is_near_local_maxima(self, x, y):
        """
        Check if the individual is near any local maxima.
        """
        for local_x, local_y, _ in self.local_maxima:
            distance = np.sqrt((x - local_x)**2 + (y - local_y)**2)
            if distance < self.local_maxima_exclDist:  # Threshold distance to consider it close to a local maximum
                return True
        return False


# Example Usage
if __name__ == "__main__":
    # Load the reaction surface
    lookup = ReactionLookup("ReactionSimulation/tables/max_at_34_10_1.csv")
    time_per_exp=15 #sec

    # Initialize the GA optimizer
    optimizer = ReactionGAOptimizer(
        reactionLookup=lookup,
        pop_size=25,
        ngen=10,
        restart_threshold=10
    )

    best_yield_global=0
    best_xy_global=0
    # Run optimization
    while True:
        optimizer.best_yield=0
        optimizer.local_maxima_exclDist=1
        best_x, best_y, best_yield = optimizer.optimize()
        if best_yield > best_yield_global:
            best_yield_global=best_yield
            best_xy_global=[best_x,best_y]
        print(f'No experiments: {optimizer.experiment_counter}')
        print(f"Optimal parameters: X={best_x:.2f}, Y={best_y:.2f}")
        print(f"Maximum yield: {best_yield:.4f}")
        print(f"Current global maximum: {best_yield_global}, with parameters {best_xy_global}")
        print(f"Experiment is {round(time_per_exp*optimizer.experiment_counter/60,0)} minutes into optimization")
        #TODO - Add logic here that flags local maxima for the solver to avoid
        if best_yield > optimizer.targetYield:
            print("We done here!")
            exit()