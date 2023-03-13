# Will Kearney
# board.py
#
# Defines the Board class, containing the data structure for the board, list of legal moves, and methods for getting subsequent moves.

import pygame
import numpy as np
import itertools
import copy
import numpy as np

from .piece import Piece
from .constants import *

class Board(object):
	"""Class for representing a Board, which is owned by a CheckersGame object."""
	def __init__(self):
		super(Board, self).__init__()

		self.board = np.empty((NUM_ROWS, NUM_COLS), dtype=Piece) # init an 8x8 board with nothing

		self.reset()

		# is a piece selected?
		self.selected_piece = None

		# this is a list that stores tuples for legal moves, if a piece is selected
		self.legal_move_tiles = []
		self.human_forced_capture_moves = [] # used to handle forced capture moves

	def reset(self):
		'''Resets the board.'''

		for i in range(NUM_ROWS):
			# first check what color piece we should place
			# white = 1, black = -1
			if i in [0,1,2]:
				# white pieces
				piece_indicator = 1
			elif i in [5,6,7]:
				# black pieces
				piece_indicator = -1
			else:
				# no piece
				continue

			for j in range(NUM_COLS):
				if (i % 2) == 0:
					# this is an even row, place pieces on odd columns
					if (j % 2) == 1:
						self.board[i,j] = Piece(indicator=piece_indicator, row=i, col=j)
				else:
					# this is an odd row, place pieces on even columns
					if (j % 2) == 0:
						self.board[i,j] = Piece(indicator=piece_indicator, row=i, col=j)

		self.selected_piece = None

		# this is a list that stores tuples for legal moves, if a piece is selected
		self.legal_move_tiles = []
		self.human_forced_capture_moves = []

	def update_force_capture_list(self):
		'''Updates a list with all capture moves that are available.'''

		all_positions = list(itertools.product(list(range(NUM_ROWS)), repeat=2))

		self.human_forced_capture_moves = []

		for from_location in all_positions:
			from_row = from_location[0]
			from_col = from_location[1]

			if self.board[from_row, from_col] and self.board[from_row, from_col].indicator == -1:
				# there is a piece here that can be moved. Let's see where it can be moved to...

				for to_location in all_positions:

					# print("\nChecking move ({}, {}) to ({}, {})".format(from_row, from_col, to_row, to_col))
					move_legality = self.check_move_legality(from_location, to_location)

					# check if this is a capture scenario
					if move_legality and not isinstance(move_legality, bool):
						self.human_forced_capture_moves.append(from_location)

	def update_legal_moves(self):
		'''Updates a list with all the currently legal moves. Used by minimax to get possible next moves.'''

		self.legal_move_tiles = []

		if not self.selected_piece:
			# no piece is selected, so just do nothing
			return

		# otherwise, let's get the selected piece and see where it can move....
		from_location = (self.selected_piece.row, self.selected_piece.col)

		force_capture_moves = []
		for to_row in range(NUM_ROWS):
			for to_col in range(NUM_COLS):
				to_location = (to_row, to_col)

				move_legality = self.check_move_legality(from_location, to_location)
				if move_legality:
					self.legal_move_tiles.append(to_location)
				if not isinstance(move_legality, bool):
					# this is a capture
					force_capture_moves.append((to_row, to_col))

		# remove all the moves that aren't a capture, assuming that this is a capture
		if len(force_capture_moves) > 0:
			self.legal_move_tiles = force_capture_moves
					
	def deselect_other_pieces(self, selected_piece):
		'''Helper function to deselect all the pieces except for the one passed in as an argument.'''

		for row in range(NUM_ROWS):
			for col in range(NUM_COLS):
				if self.board[row, col] and self.board[row, col] != selected_piece:
					self.board[row, col].selected = False

	def select_piece(self, x, y):
		'''Given x and y (position in window coordinates), select a piece if we need to.'''

		for row in range(NUM_ROWS):
			for col in range(NUM_COLS):

				# check if there's a piece here AND our click selected it AND it's not already selected
				if self.board[row, col] and self.board[row, col].check_select(x, y) and self.board[row, col].selected == False:

					if self.board[row, col] and self.board[row, col].indicator == 1:
						# if it's white, don't select it
						return

					# first select it
					self.selected_piece = self.board[row, col]
					self.board[row, col].selected = True

					self.deselect_other_pieces(self.board[row, col])

					# update the legal moves
					self.update_legal_moves()

					return True

				elif self.board[row, col] and self.board[row, col].check_select(x, y) and self.board[row, col].selected == True:

					# deselect it
					self.selected_piece = None
					self.board[row, col].selected = False

					# update the legal moves
					self.update_legal_moves()

					return True

		else:
			# this means no piece was clicked
			return False

	def draw_board(self, window, pieces=True):
		'''Given a pygame window, draw the current game state.'''

		for row in range(NUM_ROWS):
			for col in range(NUM_COLS):

				if (row % 2 == col % 2):
					# row and col are either both even or odd, so fill this in with red
					# pygame.draw.rect(surface, RED, (col*TILE_SIZE, row*TILE_SIZE, TILE_SIZE, TILE_SIZE))

					window.blit(LIGHT_BACKGROUND, (col*TILE_SIZE, row*TILE_SIZE), (col*TILE_SIZE, row*TILE_SIZE, TILE_SIZE, TILE_SIZE))
				else:
					window.blit(DARK_BACKGROUND, (col*TILE_SIZE, row*TILE_SIZE), (col*TILE_SIZE, row*TILE_SIZE, TILE_SIZE, TILE_SIZE))

				# check if there is a piece here, and if so draw it
				if pieces and isinstance(self.board[row, col], Piece):
					self.board[row, col].draw_piece(window)

		# draw any legal move indicators
		if pieces:
			for legal_move_tile in self.legal_move_tiles:
				row = legal_move_tile[0]
				col = legal_move_tile[1]

				pygame.draw.rect(window, BLUE, (col*TILE_SIZE, row*TILE_SIZE, TILE_SIZE, TILE_SIZE), 3)

	def distance_between_centroids(self):
		'''Calculates the distance between the white and black centroids. Used for a static evaluation heuristic.'''

		# init some empty lists
		white_coordinates = []
		black_coordinates = []

		# in Cartesian coordinates, the centroid is just the mean of the components
		for row in range(NUM_ROWS):
			for col in range(NUM_COLS):
				if self.board[row, col] and self.board[row, col].indicator == 1:
					white_coordinates.append((float(row), float(col)))
				elif self.board[row, col] and self.board[row, col].indicator == -1:
					black_coordinates.append((float(row), float(col)))

		if len(white_coordinates) == 0 or len(black_coordinates) == 0:
			# if there's no pieces of a color, return None
			return None

		if len(white_coordinates) == 1:
			white_centroid = white_coordinates[0]
		else:
			white_centroid = np.mean(white_coordinates, axis=0)

		if len(black_coordinates) == 1:
			black_centroid = black_coordinates[0]
		else:
			black_centroid = np.mean(black_coordinates, axis=0)

		return ((white_centroid[0] - black_centroid[0])**2 + (white_centroid[1] - black_centroid[1])**2) ** 0.5


	def static_evaluation(self, aggressive=False):
		'''Perform a static evaluation of the board game. If the aggressive argument is True, then also incorporate centroid distance into the evaluation.'''

		evaluation = 0
		num_white_pieces = 0
		num_black_pieces = 0
		for row in range(NUM_ROWS):
			for col in range(NUM_COLS):

				if self.board[row, col]:
					if self.board[row, col].indicator == 1:
						num_white_pieces += 1
					elif self.board[row, col].indicator == -1:
						num_black_pieces += 1

					# check if this is a king piece, let's weight them more
					if self.board[row, col].king == False:
						evaluation = evaluation + self.board[row, col].indicator
					elif self.board[row, col].king == True:
						evaluation = evaluation + (self.board[row, col].indicator * 2)

		# this is a winning move; return the largest (or smallest) number possible
		if num_white_pieces == 0:
			return -np.inf
		elif num_black_pieces == 0:
			return np.inf

		if aggressive:
			distance_between_centroids = self.distance_between_centroids()

			if distance_between_centroids:
				evaluation -= distance_between_centroids

		return evaluation

	def get_num_pieces(self, piece_indicator):
		'''Returns the number of pieces remaining for a given piece indicator (1 = white, -1 = black).'''

		num_pieces = 0
		for row in range(NUM_ROWS):
			for col in range(NUM_COLS):
				if self.board[row, col] and self.board[row, col].indicator == piece_indicator:
					num_pieces += 1

		return num_pieces

	def is_winner(self, piece_indicator):
		'''Given a piece indicator (1 = white, -1 = black), determine if the player has won.'''

		opponent_indicator = piece_indicator * -1

		num_opponents_remaining = 0
		for row in range(NUM_ROWS):
			for col in range(NUM_COLS):
				if self.board[row, col] and self.board[row, col].indicator == opponent_indicator:
					num_opponents_remaining = num_opponents_remaining + 1

		if num_opponents_remaining == 0:
			return True
		else:
			return False

	def move_piece(self, from_row, from_col, to_row, to_col):
		'''Move a piece given a from and to location, in row coordinates (NOT window coordinates).'''

		move_legality = self.check_move_legality((from_row, from_col), (to_row, to_col))

		if not move_legality:
			return None

		self.board[to_row, to_col] = self.board[from_row, from_col]
		self.board[from_row, from_col] = None

		# update the position in the piece object
		self.board[to_row, to_col].row = to_row
		self.board[to_row, to_col].col = to_col

		if to_row == 0 and self.board[to_row, to_col].indicator == -1:
			self.board[to_row, to_col].king = True

		if to_row == NUM_ROWS - 1 and self.board[to_row, to_col].indicator == 1:
			self.board[to_row, to_col].king = True

		# check to see if it was a capture
		if not isinstance(move_legality, bool):
			# it WAS a capture -- remove the captured piece

			# regicide; check if the captured piece is a king or not
			if self.board[move_legality[0], move_legality[1]].king == True:
				self.board[to_row, to_col].king = True

			self.board[move_legality[0], move_legality[1]] = None

		return self.board[to_row, to_col]

	def get_possible_next_moves(self, player):
		'''Given a board configuration and a player to move, return all possible moves that can be made in the form of new boards'''

		all_positions = list(itertools.product(list(range(NUM_ROWS)), repeat=2))

		possible_next_moves = []
		forced_capture_moves = []

		for from_location in all_positions:
			from_row = from_location[0]
			from_col = from_location[1]

			if self.board[from_row, from_col] and self.board[from_row, from_col].indicator == player:
				# there is a piece here that can be moved. Let's see where it can be moved to...
				for to_location in all_positions:
					to_row = to_location[0]
					to_col = to_location[1]

					# print("\nChecking move ({}, {}) to ({}, {})".format(from_row, from_col, to_row, to_col))
					move_legality = self.check_move_legality(from_location, to_location)

					if move_legality:
						# this is a legal move
						# create a copy of this board
						possible_game_state = copy.deepcopy(self)

						# make the move
						possible_game_state.move_piece(from_row, from_col, to_row, to_col)

						# check to see if it was a capture
						if not isinstance(move_legality, bool):
							forced_capture_moves.append(possible_game_state)
						
						# append to our list
						possible_next_moves.append(possible_game_state)		

		if len(forced_capture_moves) > 0:
			# there were capture moves
			possible_next_moves = forced_capture_moves

		np.random.shuffle(possible_next_moves)

		return possible_next_moves

	def check_move_legality(self, from_location, to_location, print_statements=False):
		'''Given a from and to location, determine if a move is legal (also checks if a piece is present at the from location).'''

		from_row = from_location[0]
		from_col = from_location[1]
		to_row = to_location[0]
		to_col = to_location[1]

		# make sure move is within bounds
		if to_row < 0 or to_row > 7 or to_col < 0 or to_col > 7:
			if print_statements: print("TO location is outside the board boundaries.")
			return False

		if from_row < 0 or from_row > 7 or from_col < 0 or from_col > 7:
			if print_statements: print("FROM location is outside the board boundaries.")
			return False

		# this will weed out a bunch of non-legal moves
		if to_row == from_row:
			if print_statements: print("TO row and FROM row must be different.")
			return False

		# make sure there is a piece at the from location, and get info
		if self.board[from_row, from_col]:
			# there is a piece here. Get the color indicator
			piece_indicator = self.board[from_row, from_col].indicator
			king = self.board[from_row, from_col].king
		else:
			if print_statements: print("There is no piece at the FROM location.")
			return False

		# make sure these is NO piece at the to location
		if self.board[to_row, to_col]:
			if print_statements: print("There is a piece at the TO location.")
			return False

		# check if this is a legal diagonal move (no-capture, non-king)
		if (to_row == from_row + piece_indicator) and (to_col in [from_col-1, from_col+1]):
			if print_statements: print("Legal non-capturing move.")
			return True

		# check if this is a legal diagonal move (no-capture, king)
		if (king) and (to_row == from_row - piece_indicator) and (to_col in [from_col-1, from_col+1]):
			if print_statements: print("Legal non-capturing move (king).")
			return True

		# get the opposite indicator
		opponent_indicator = int(piece_indicator * -1)

		# check if this is a single capture move
		if (to_row == from_row + (piece_indicator * 2)) and (to_col in [from_col-2, from_col+2]):
			# this might be a capture; check if a piece of the opposite color is in the middle

			row_to_check = from_row + piece_indicator

			if to_col > from_col:
				col_to_check = from_col + 1
			elif to_col < from_col:
				col_to_check = from_col - 1

			if self.board[row_to_check, col_to_check] and self.board[row_to_check, col_to_check].indicator == opponent_indicator:
				if print_statements: print("Piece of opposite color exists in the middle of the jump (location {}, {})".format(row_to_check, col_to_check))
				return (row_to_check, col_to_check)
			else:
				return False

		# do the same, but for a king
		if king and (to_row == from_row - (piece_indicator * 2)) and (to_col in [from_col-2, from_col+2]):
			# this might be a capture; check if a piece of the opposite color is in the middle

			row_to_check = from_row - piece_indicator

			if to_col > from_col:
				col_to_check = from_col + 1
			elif to_col < from_col:
				col_to_check = from_col - 1

			if self.board[row_to_check, col_to_check] and self.board[row_to_check, col_to_check].indicator == opponent_indicator:
				if print_statements: print("Piece of opposite color exists in the middle of the king jump (location {}, {})".format(row_to_check, col_to_check))
				return (row_to_check, col_to_check)
			else:
				return False

		# if it doesn't pass any of these, return False
		return False

	def __str__(self):
		'''Overwrite the built-in string method. We use this printing boards to the console for debugging.'''
		return np.array2string(self.board, formatter={'all': lambda x: "w" if x and x.indicator == 1 else ("b" if x and x.indicator == -1 else "-")})