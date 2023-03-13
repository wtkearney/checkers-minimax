# Will Kearney
# main.py
#
# This is the main file that is run to launch the game.
# Also contains a function for building some plots to analyze gameplay.

import time
import numpy as np
import matplotlib.pyplot as plt
import pygame

# initialize game engine
pygame.init()

from checkers.constants import *

from checkers.game import CheckersGame

# setup the pygame window and title
window = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption(CAPTION)

def make_centroid_plots():
	'''This is a function that builds plots showing how gameplay is effected when the AI is set to aggressive.'''

	max_turns = 20
	num_simulations = 10

	fig, axs = plt.subplots(3, 1, figsize=(12, 6), dpi=129)

	# create some matrices to hold our data that we will plot later
	centroid_distance_over_time_aggressive = np.zeros(shape=(num_simulations, max_turns))
	number_white_pieces_over_time_aggressive = np.zeros(shape=(num_simulations, max_turns))
	number_black_pieces_over_time_aggressive = np.zeros(shape=(num_simulations, max_turns))

	centroid_distance_over_time = np.zeros(shape=(num_simulations, max_turns))
	number_white_pieces_over_time = np.zeros(shape=(num_simulations, max_turns))
	number_black_pieces_over_time = np.zeros(shape=(num_simulations, max_turns))

	for sim_number in range(num_simulations):

		print("Simulation number: {}".format(sim_number))

		# create the initial board
		game = CheckersGame()
		game.difficulty_level = "Medium"
		game.aggressive_AI = True
		current_turn = 0

		while (not game.winner) and (current_turn < max_turns):

			print("\tCurrent turn: {}".format(current_turn))

			game.make_AI_move(game.current_player)

			distance_between_centroids = game.board.distance_between_centroids()
			centroid_distance_over_time_aggressive[sim_number, current_turn] = distance_between_centroids

			# calculate number of each color remaining
			number_white_pieces_over_time_aggressive[sim_number, current_turn] = game.board.get_num_pieces(1)
			number_black_pieces_over_time_aggressive[sim_number, current_turn] = game.board.get_num_pieces(-1)

			current_turn += 1

		# either the game is won or max turns was reached; let's make some plots
		axs[0].plot(centroid_distance_over_time_aggressive[sim_number, :], color="Blue", alpha=0.2, linewidth=0.8)
		axs[1].plot(number_white_pieces_over_time_aggressive[sim_number, :], color="Blue", alpha=0.2, linewidth=0.8)
		axs[2].plot(number_black_pieces_over_time_aggressive[sim_number, :], color="Blue", alpha=0.2, linewidth=0.8)


		# Do it again without being aggressive
		game = CheckersGame()
		game.difficulty_level = "Medium"
		game.aggressive_AI = False
		current_turn = 0

		while (not game.winner) and (current_turn < max_turns):

			print("\tCurrent turn: {}".format(current_turn))

			game.make_AI_move(game.current_player)

			distance_between_centroids = game.board.distance_between_centroids()
			centroid_distance_over_time[sim_number, current_turn] = distance_between_centroids

			# calculate number of each color remaining
			number_white_pieces_over_time[sim_number, current_turn] = game.board.get_num_pieces(1)
			number_black_pieces_over_time[sim_number, current_turn] = game.board.get_num_pieces(-1)

			current_turn += 1

		# either the game is won or max turns was reached; let's make some plots
		axs[0].plot(centroid_distance_over_time[sim_number, :], color="Orange", alpha=0.2, linewidth=0.8)
		axs[1].plot(number_white_pieces_over_time[sim_number, :], color="Orange", alpha=0.2, linewidth=0.8)
		axs[2].plot(number_black_pieces_over_time[sim_number, :], color="Orange", alpha=0.2, linewidth=0.8)


	# let's get and plot averages...
	centroid_avg_aggressive = np.mean(centroid_distance_over_time_aggressive, axis=0)
	centroid_avg = np.mean(centroid_distance_over_time, axis=0)
	axs[0].plot(centroid_avg_aggressive, color="Blue", alpha=1, label="Aggressive", linewidth=2)
	axs[0].plot(centroid_avg, color="Orange", alpha=1, label="Non-aggressive", linewidth=2)

	number_white_pieces_over_time_aggressive = np.mean(number_white_pieces_over_time_aggressive, axis=0)
	number_white_pieces_over_time = np.mean(number_white_pieces_over_time, axis=0)
	axs[1].plot(number_white_pieces_over_time_aggressive, color="Blue", alpha=1, label="Aggressive", linewidth=2)
	axs[1].plot(number_white_pieces_over_time, color="Orange", alpha=1, label="Non-aggressive", linewidth=2)

	number_black_pieces_over_time_aggressive = np.mean(number_black_pieces_over_time_aggressive, axis=0)
	number_black_pieces_over_time = np.mean(number_black_pieces_over_time, axis=0)
	axs[2].plot(number_black_pieces_over_time_aggressive, color="Blue", alpha=1, label="Aggressive", linewidth=2)
	axs[2].plot(number_black_pieces_over_time, color="Orange", alpha=1, label="Non-aggressive", linewidth=2)

	# do some formatting
	axs[0].set_title("Aggressive vs non-aggressive gameplay")

	axs[0].set_ylabel("Centroid\ndistance")
	axs[1].set_ylabel("White pieces\nremaining")
	axs[2].set_ylabel("Black pieces\nremaining")

	axs[1].set_ylim([None, 13])
	axs[2].set_ylim([None, 13])

	axs[0].grid()
	axs[1].grid()
	axs[2].grid()

	axs[0].legend()
	axs[1].legend()
	axs[2].legend()

	plt.show()

def main():
	# this tells us if the game is running or not
	running = True

	# this tells us if we should display the splash screen or game over screen, respectively
	splash_screen = True

	# clock to control frame rate for different computer speeds
	clock = pygame.time.Clock()

	# create the initial board
	game = CheckersGame()

	# start the main event loop
	while running:
		# tick the clock forward
		clock.tick(FPS)

		if splash_screen:

			# get mouse position
			position = pygame.mouse.get_pos()

			for event in pygame.event.get():

				if event.type == pygame.QUIT:
					running = False # this means we should quit the game

				if event.type == pygame.MOUSEBUTTONDOWN:

					# we clicked something
					if game.handle_mouse_click_start(position[0], position[1]):
						splash_screen = False

					# check to see if any button were clicked
					game.handle_mouse_click_difficulty(position[0], position[1])
					game.handle_mouse_click_aggressive(position[0], position[1])

			game.draw_splash_screen(window, position)

		elif game.winner:
			time.sleep(0.5)

			for event in pygame.event.get():

				if event.type == pygame.QUIT:
					running = False

				if event.type == pygame.MOUSEBUTTONDOWN:

					# we clicked something
					game.board.reset()
					game.winner = None
					game.current_player = -1
					splash_screen = True

			game.draw_game_over_screen(window)

		elif game.forced_capture_error:
			# display popup warning
			game.draw_forced_capture_warning(window)

			# update display
			pygame.display.flip()

			# show this message for 1.5 seconds, then go back to playing the game
			time.sleep(1.5)
			game.forced_capture_error = False

		else:
			if game.current_player == 1:
				game.make_AI_move(game.current_player)

			# check to see if any events have happened (they'll be stored in the even list if so)
			for event in pygame.event.get():

				if event.type == pygame.QUIT:
					running = False

				if event.type == pygame.MOUSEBUTTONDOWN:

					# we clicked something
					position = pygame.mouse.get_pos()
					
					# check to see if a piece was selected or needs to be moved
					game.handle_mouse_click(position[0], position[1])

			# draw the board game
			game.board.draw_board(window)

		# regardless, update the display
		pygame.display.flip() # I think this may be faster then pygame.display.update()?

	# if we're here, quit the game
	pygame.quit()

if __name__ == '__main__':
	main()
	# make_centroid_plots()