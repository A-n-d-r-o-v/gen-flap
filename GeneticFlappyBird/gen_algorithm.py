import pygame
import copy
import torch
import torch.nn as nn
import random

class Neural_Network(nn.Module):
	def __init__(self):
		super(Neural_Network, self).__init__()
		# parameters
		# TODO: parameters can be parameterized instead of declaring them here
		self.inputSize = 4
		self.outputSize = 1
		self.hiddenSize = 20
		# weights
		self.W1 = torch.randn(self.inputSize, self.hiddenSize) 
		self.W2 = torch.randn(self.hiddenSize, self.outputSize)

		self.weights = [self.W1, self.W2] # W1 and W2 correspond to layer weight tensors between input/hidden and hidden/output respectively.

	def forward(self, X):
		self.z = torch.matmul(X, self.W1) 
		self.z2 = torch.nn.functional.relu(self.z)#torch.sigmoid(self.z) # activation function
		self.z3 = torch.matmul(self.z2, self.W2)
		out = torch.sigmoid(self.z3) # final activation function
		return out

class Population():
	def __init__(self, size, environment):
		self.size = size
		self.environment = environment

		agent_gravity_acc = 0.3
		agent_radius = 10

		self.population_list = [Individual(agent_gravity_acc, agent_radius) for i in range(self.size)]

	def is_dead(self):
		everyone_dead = True
		for individual in self.population_list:
			if not individual.is_dead:
				everyone_dead = False
		return everyone_dead

	def reset(self):
		for individual in self.population_list:
			individual.is_dead = False
			individual.reset()

	def live_count(self):
		count = 0
		for individual in self.population_list:
			if not individual.is_dead:
				count += 1
		return count

	def leading_agent(self):
		leading = self.population_list[0]
		for individual in self.population_list:
			if individual.x_pos > leading.x_pos:
				leading = individual
		return leading

	# Roulette wheel selection
	def fittest(self, count=12):
		sorted_population = sorted(self.population_list, key=lambda obj: obj.cost)

		print("PRINTING COSTS:")

		for bird in sorted_population:
			print(bird.cost)

		return sorted_population[-count:]
		'''
		fitness_sum = sum(x.cost for x in self.population_list)
		fittest_list = []
		for individual in self.population_list:
			selection_chance = individual.cost / fitness_sum
			if random.random() < selection_chance:
				fittest_list.append(individual)
		return fittest_list[:count]
		'''

	def breed(self, fittest, target_count):
		offspring_list = []
		while len(offspring_list) < target_count:
			for i in fittest:
				for j in fittest:
					if not (i is j):
						offspring_A, offspring_B = i.crossover(j)
						if random.random() < 0.4:
							offspring_A.mutate(0.3)
							offspring_B.mutate(0.3)
						offspring_list.append(offspring_A)
						offspring_list.append(offspring_B)
		return offspring_list

	def get(index):
		return population_list[index]

class Individual():
	def __init__(self, gravity_acc, radius):
		self.gravity_acc = gravity_acc
		self.radius = radius

		self.y_velocity = 0
		self.x_pos = 200
		self.y_pos = 200
		self.rect = self.rectangle_bounds()
		self.default_color = (255, 255, 255)

		self.neural_network = Neural_Network()

		self.is_dead = False
		self.cost = 0
		self.distance_traveled = 0

	def rectangle_bounds(self):
		return pygame.Rect(self.x_pos - self.radius, self.y_pos - self.radius, self.radius*2, self.radius*2)

	def render(self, surface, is_leading=False):
		leading_color = (255, 255, 0)
		color = leading_color if is_leading else self.default_color
		pygame.draw.circle(surface, color, [int(self.x_pos), int(self.y_pos)], self.radius)

	def update(self, environment, x_velocity):
		self.y_pos += self.y_velocity
		self.y_velocity += self.gravity_acc
		self.rect = self.rectangle_bounds()

		if self.y_pos < 0:
			self.y_pos = 0
			self.is_dead = True
		if self.y_pos > environment.screen_height - self.radius:
			self.y_pos = environment.screen_height - self.radius

		if not self.is_dead:
			self.distance_traveled += x_velocity

	def tick_neural_network(self, env_state):
		output = self.neural_network.forward(env_state)
		if output[0] > 0.5 and not self.is_dead:
			self.jump(5.5)

	def jump(self, power):
		self.y_velocity = -power

	def stop_if_dead(self, pipe_velocity):
		if self.is_dead:
			self.x_pos -= pipe_velocity

	def reset(self):
		self.y_velocity = 0
		self.x_pos = 200
		self.y_pos = 200
		self.distance_traveled = 0
		self.cost = 0

	def mutate(self, mutation_frequency):
		for weight_layer_index in range(len(self.neural_network.weights)):
			for weight_vector_index in range(len(self.neural_network.weights[weight_layer_index])):
				for weight_index in range(len(self.neural_network.weights[weight_layer_index][weight_vector_index])):
					if random.random() < mutation_frequency:
						self.neural_network.weights[weight_layer_index][weight_vector_index][weight_index] = torch.randn(1)

	def print_weights(self):
		for param in self.neural_network.parameters():
			print(param.data)

	# Swap random weights
	def crossover(self, other):
		offspring_A = copy.deepcopy(self)
		offspring_B = copy.deepcopy(other)

		for i in range(len(self.neural_network.weights)): # Loop through layers
			for weight_vec_index in range(len(self.neural_network.weights[i])): # Loop through weight vectors in each matrix
				for weight_index in range(len(self.neural_network.weights[i][weight_vec_index])): # Loop through individual weights in each vector
					#weight_A = offspring_A.neural_network.weights[i][weight_vec_index][weight_index] # Weight from offspring A
					#weight_B = offspring_B.neural_network.weights[i][weight_vec_index][weight_index] # Weight from offspring B

					if random.random() > 0.5:
						# A,B = B,A
						offspring_A.neural_network.weights[i][weight_vec_index][weight_index], \
						offspring_B.neural_network.weights[i][weight_vec_index][weight_index] = \
						offspring_B.neural_network.weights[i][weight_vec_index][weight_index], \
						offspring_A.neural_network.weights[i][weight_vec_index][weight_index] # Swap weights between offspring A and offspring B

		return offspring_A, offspring_B

	def calc_cost(self, next_pipe_dist_y):
		return self.distance_traveled - next_pipe_dist_y 
