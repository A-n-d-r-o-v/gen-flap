""" 
Game-specific stuff
"""

import pygame
import random

class Environment():
	def __init__(self, screen_width, screen_height, pipe_distance, pipe_width, gap_height):
		self.screen_width = screen_width
		self.screen_height = screen_height
		self.pipe_distance = pipe_distance
		self.pipe_width = pipe_width
		self.gap_height = gap_height

		self.pipe_count = 2 + int(self.screen_width / self.pipe_distance)
		self.pipe_list = self.instantiate_pipes()

	def instantiate_pipes(self):
		pipes = []
		for x in range(self.pipe_count):
			pipes.append(PipePair((self.screen_width + 550) - x * self.pipe_distance, self.screen_height, self.pipe_width, self.gap_height))
		return pipes

	def collides_with(self, player_rect):
		for pipe in self.pipe_list:
			if player_rect.colliderect(pipe.rects[0]) or player_rect.colliderect(pipe.rects[1]):
				return True
		return False

	def closest_pipe(self, x):
		# Find any pipe that is to the right of the player.
		closest_pipe = None
		for pipe in self.pipe_list:
			if not pipe.horizontal_distance(x) == -1:
				closest_pipe = pipe
				break
		# Loop through each consecutive pipe that satisfies that condition, and find the closest one to the specified x value.
		for pipe in self.pipe_list:
			if not pipe.horizontal_distance(x) == -1:
				if pipe.x_pos < closest_pipe.x_pos:
					closest_pipe = pipe
		return closest_pipe

	def pipe_right_count(self, x):
		count = 0
		for pipe in self.pipe_list:
			if x < pipe.x_pos:
				count += 1
		return count

	def move_pipes(self, velocity):
		for i in range(len(self.pipe_list)):
			pipe = self.pipe_list[i]
			pipe.x_pos -= velocity

			if pipe.x_pos < -self.pipe_width:
				pipe.x_pos = self.pipe_list[(i + 1) % self.pipe_count].x_pos + self.pipe_distance
				pipe.gap_y = pipe.calc_y_gap()

			pipe.rects = pipe.rectangle_bounds()

	def render_pipes(self, surface, closest_pipe=None):
		for pipe_pair in self.pipe_list:
			pipe_pair.render(surface, self.pipe_width, self.gap_height, is_closest=(pipe_pair is closest_pipe))

	def reset(self):
		self.pipe_list = self.instantiate_pipes()


class PipePair():
	def __init__(self, x_pos, screen_height, pipe_width, gap_height, min_gap_y=60):
		self.x_pos = x_pos
		self.screen_height = screen_height
		self.pipe_width = pipe_width
		self.gap_height = gap_height
		self.min_gap_y = min_gap_y
		self.gap_y = self.calc_y_gap()
		self.rects = self.rectangle_bounds()
		self.default_color = (255, 255, 255)

	def rectangle_bounds(self):
		pipe_rects = [pygame.Rect(self.x_pos, 0, self.pipe_width, self.gap_y - self.gap_height/2),
						pygame.Rect(self.x_pos, self.gap_y + self.gap_height/2, self.pipe_width, self.screen_height)]
		return pipe_rects

	def calc_y_gap(self):
		return random.randrange(self.min_gap_y, self.screen_height - self.min_gap_y)

	# Distance to an agent, if the agent is located to the left of the pipe
	def horizontal_distance(self, x):
		if x < self.x_pos + self.pipe_width + 10:
			return self.x_pos - x + self.pipe_width
		else:
			return -1

	def vertical_distance(self, y, surface=None):
		if surface:
			pygame.draw.line(surface,(0,0,255),(200,y),(200,self.gap_y))

		return y - self.gap_y

	def render(self, surface, pipe_width, gap_height, is_closest=False):
		closest_color = (0, 255, 0)
		color = closest_color if is_closest else self.default_color

		top_pipe_rect = pygame.Rect(self.x_pos, 0, pipe_width, self.gap_y - gap_height/2)
		bottom_pipe_rect = pygame.Rect(self.x_pos, self.gap_y + gap_height/2, pipe_width, self.screen_height)
		pygame.draw.rect(surface, color, top_pipe_rect)
		pygame.draw.rect(surface, color, bottom_pipe_rect)