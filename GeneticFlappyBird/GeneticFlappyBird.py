import pygame
import argparse
import sys
import random
from pygame.locals import QUIT
from environment import *
from gen_algorithm import *

# TODO: Sprites
# TODO: Species (different NN dimensions, mutation rates, etc...)

def main():
	WIDTH = 640
	HEIGHT = 400

	parser = argparse.ArgumentParser(description='Stupid bird brain')
	parser.add_argument('--learning_rate', type=float, default=0.3, 
		metavar='L', help='learning rate (default 0.9)')
	parser.add_argument('--int_test', '-i', type=int, default=3, 
		metavar='I',help='test int, incredibly useful for your integer needs (default 3)')

	args = parser.parse_args()
	#print(args.string_test)
	#print(args.int_test)

	screen = pygame.display.set_mode((WIDTH, HEIGHT))
	surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)

	environment = Environment(WIDTH, HEIGHT, 120, 30, 105)
	population = Population(30, environment)

	show_all = True # Whether or not to show each and every agent or just the leading agent

	pipe_velocity_x = 1.1
	closest_pipe = environment.pipe_list[0]

	clock = pygame.time.Clock()
	tick = 0
	while True:
		surface.fill((0,0,0, 255))

		leading_agent = population.leading_agent()
		#print("Leading X: ", leading_agent.x_pos)

		#print("Number of pipes to the right:", environment.pipe_right_count(leading_agent.x_pos))

		environment.render_pipes(surface, closest_pipe)
		environment.move_pipes(pipe_velocity_x)

		#print("Closest pipe x:", environment.closest_pipe(player_test.x_pos).x_pos)

		pygame.display.flip()

		if not show_all:
			leading_agent.render(surface)

		# Make neural network decision.
		for individual in population.population_list:
			if show_all:
				individual.render(surface, is_leading=(individual is leading_agent))
			individual.update(environment, pipe_velocity_x)

			if environment.collides_with(individual.rect) or individual.y_pos >= environment.screen_height - individual.radius:
				individual.is_dead = True
			individual.stop_if_dead(pipe_velocity_x)

			# Neural network decision-making
			if tick % 5 == 0:
				closest_pipe = environment.closest_pipe(leading_agent.x_pos)
				input_values = torch.tensor([float(closest_pipe.horizontal_distance(individual.x_pos)),
											 float(closest_pipe.vertical_distance(individual.y_pos, surface)),
											 float(individual.y_velocity),
											 float(individual.y_pos)])
				individual.tick_neural_network(input_values)

		if population.is_dead():
			# Calculate cost (fitness)
			# TODO closest pipe is calculated after EVERY bird is dead. Should be calculated at the time of death.
			for individual in population.population_list:
				individual.print_weights()

				closest_pipe = environment.closest_pipe(individual.x_pos)
				pipe_y_dist = closest_pipe.vertical_distance(individual.y_pos, surface)
				individual.cost = individual.calc_cost(pipe_y_dist) # (Distance to next pipe)

			fittest = population.fittest(count=4)
			target_size = population.size - len(fittest)
			offspring = population.breed(fittest, target_size) # Mutation and cross-over occurs here.
			for offs in offspring:  	
				offs.default_color = (255, 0, 255)
			for fit in fittest:
				fit.default_color = (255, 0, 0)
			population.population_list = fittest[:] + offspring[:target_size]

			# Update neural network:
			# - Acquire fitness values
			# - Select fittest (Kill rest)
			# - Cross over
			# - Mutate
			# Continue to next generation

			population.reset()
			environment.reset()

		screen.blit(surface, (0,0))
		for event in pygame.event.get():
			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_a:
					show_all = not show_all # Toggle show all
					#player_test.jump(6)

			if event.type == QUIT:
				sys.exit(0)

		closest_pipe = environment.closest_pipe(leading_agent.x_pos)
		tick = (tick + 1) % 30*100
		clock.tick(60) # Limit FPS


if __name__ == "__main__":
	main()