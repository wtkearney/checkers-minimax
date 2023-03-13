# Will Kearney
# game.py
#
# Defines the CheckersGame class, including the minimax algortihm, drawing things, and handling mouse clicks

import numpy as np
import itertools
import copy

from .board import Board
from .constants import *

class CheckersGame(object):
	"""Class for representing a checkers game"""
	def __init__(self):
		super(CheckersGame, self).__init__()

		self.difficulty_level = "Easy"

		self.rows = 8
		self.cols = 8

		self.board = Board()
		self.board.reset()

		self.winner = None

		# who's turn is it? Black always goes first
		self.current_player = -1

		self.forced_capture_error = False # this gets toggled on to display the warning pop-up
		self.aggressive_AI = False

	def handle_mouse_click(self, x, y):
		'''Handle a mouse click from the user given an x and y in window coordinates.'''

		if self.current_player == 1:
			# AI turn, do nothing
			return

		# position is (x,y) coordinates. Let's check if a piece is there.
		piece_selected = self.board.select_piece(x, y)

		if not piece_selected:
			# check if a piece is already selected
			if not self.board.selected_piece:
				# there is no currently selected piece (a piece was only deselected), so we can just return
				return

		else:
			# this means a piece was clicked, we can just return
			return

		# if we're here, it means the user is trying to move a piece

		# get row and column of mouse click
		to_row = int(y / TILE_SIZE)
		to_col = int(x / TILE_SIZE)

		from_row = self.board.selected_piece.row
		from_col = self.board.selected_piece.col

		if len(self.board.human_forced_capture_moves) > 0 and (from_row, from_col) not in self.board.human_forced_capture_moves:

			# the user is trying to move somewhere, even though a capture is possible
			self.forced_capture_error = True

			from_location = self.board.human_forced_capture_moves[0]
			self.board.selected_piece = self.board.board[from_location[0], from_location[1]]
			self.board.selected_piece.selected = True
			self.board.deselect_other_pieces(self.board.selected_piece)
			self.board.update_legal_moves()

			return

		# check if this is in the legal move list
		if (to_row, to_col) in self.board.legal_move_tiles:
			# make the move
			self.board.move_piece(self.board.selected_piece.row, self.board.selected_piece.col, to_row, to_col)
			self.current_player = self.current_player * -1

		# deselect the piece
		self.board.selected_piece = None
		self.board.deselect_other_pieces(None)
		self.board.update_legal_moves()

		self.check_winner()

		return

	def handle_mouse_click_difficulty(self, x, y):
		'''Checks and handles if the user has changed the difficulty level.'''

		x_center = int(TILE_SIZE * NUM_COLS / 2)
		y_center = int(TILE_SIZE * 5)
		width = TILE_SIZE*2
		height = TILE_SIZE*0.8

		if (x > x_center - width // 2) and (x < x_center + width // 2) and (y > y_center - height // 2) and (y < y_center + height // 2):
			if self.difficulty_level == "Easy":
				self.difficulty_level = "Medium"
			elif self.difficulty_level == "Medium":
				self.difficulty_level = "Hard"
			elif self.difficulty_level == "Hard":
				self.difficulty_level = "Easy"
		else:
			return False

	def handle_mouse_click_aggressive(self, x, y):
		'''Checks and handles if the user has changed the aggressive AI feature.'''

		x_center = int(TILE_SIZE * NUM_COLS / 2)
		y_center = int(TILE_SIZE * 4)
		width = TILE_SIZE*2
		height = TILE_SIZE*0.8

		if (x > x_center - width // 2) and (x < x_center + width // 2) and (y > y_center - height // 2) and (y < y_center + height // 2):
			self.aggressive_AI = not self.aggressive_AI


	def handle_mouse_click_start(self, x, y):
		'''Checks and handles if the user has pressed the start game button.'''

		x_center = int(TILE_SIZE * NUM_COLS / 2)
		y_center = int(TILE_SIZE * 6)
		width = TILE_SIZE*2
		height = TILE_SIZE*0.8

		# first check if we're on the start button
		if (x > x_center - width // 2) and (x < x_center + width // 2) and (y > y_center - height // 2) and (y < y_center + height // 2):
			return True
		else:
			return False

	def draw_aggressive_button(self, window, position):
		'''Handles drawing the button to activate the aggressive AI feature.'''

		x_center = int(TILE_SIZE * NUM_COLS / 2)
		y_center = int(TILE_SIZE * 4)
		width = TILE_SIZE*2
		height = TILE_SIZE*0.8

		# we need to use a surface because pygame.rect doesn't allow for alpha blending
		s = pygame.Surface((width, height))
		s.set_alpha(200)

		x_mouse = position[0]
		y_mouse = position[1]

		# check if mouse is over the start button
		if (x_mouse > x_center - width // 2) and (x_mouse < x_center + width // 2) and (y_mouse > y_center - height // 2) and (y_mouse < y_center + height // 2):
			s.fill(ORANGE)
		else:
			s.fill(DARKER_ORANGE)

		# draw it
		window.blit(s, (x_center - s.get_width() // 2, y_center - s.get_height() // 2))

		if self.aggressive_AI:
			text = "Aggressive AI"
		else:
			text = "Normal AI"

		text_size = s.get_height() // 4

		# get bounding rectangles of text
		text_rect = game_font.get_rect(text, size=text_size)

		# set the center points
		text_rect.center = (x_center, y_center)

		game_font.render_to(window, text_rect, text, BLACK, size = text_size)

	def draw_difficulty_button(self, window, position):
		'''Handles drawing the button to change difficulty level.'''

		x_center = int(TILE_SIZE * NUM_COLS / 2)
		y_center = int(TILE_SIZE * 5)
		width = TILE_SIZE*2
		height = TILE_SIZE*0.8

		# we need to use a surface because pygame.rect doesn't allow for alpha blending
		s = pygame.Surface((width, height))
		s.set_alpha(200)

		x_mouse = position[0]
		y_mouse = position[1]

		# check if mouse is over the start button
		if (x_mouse > x_center - width // 2) and (x_mouse < x_center + width // 2) and (y_mouse > y_center - height // 2) and (y_mouse < y_center + height // 2):
			if self.difficulty_level == "Easy":
				s.fill(EASY_COLOR_SELECTED)
			elif self.difficulty_level == "Medium":
				s.fill(MEDIUM_COLOR_SELECTED)
			elif self.difficulty_level == "Hard":
				s.fill(HARD_COLOR_SELECTED)
		else:
			if self.difficulty_level == "Easy":
				s.fill(EASY_COLOR)
			elif self.difficulty_level == "Medium":
				s.fill(MEDIUM_COLOR)
			elif self.difficulty_level == "Hard":
				s.fill(HARD_COLOR)

		# draw it
		window.blit(s, (x_center - s.get_width() // 2, y_center - s.get_height() // 2))

		difficulty_text= "Difficulty: " + self.difficulty_level
		difficulty_text_size = s.get_height() // 4

		# get bounding rectangles of text
		difficulty_text_rect = game_font.get_rect(difficulty_text, size=difficulty_text_size)

		# set the center points
		difficulty_text_rect.center = (x_center, y_center)

		game_font.render_to(window, difficulty_text_rect, difficulty_text, BLACK, size = difficulty_text_size)

	def draw_start_button(self, window, position):
		'''Handles drawing the start button.'''

		x_center = int(TILE_SIZE * NUM_COLS / 2)
		y_center = int(TILE_SIZE * 6)
		width = TILE_SIZE*2
		height = TILE_SIZE*0.8

		# we need to use a surface because pygame.rect doesn't allow for alpha blending
		s = pygame.Surface((width, height))
		s.set_alpha(200)

		x_mouse = position[0]
		y_mouse = position[1]

		# check if mouse is over the start button
		if (x_mouse > x_center - width // 2) and (x_mouse < x_center + width // 2) and (y_mouse > y_center - height // 2) and (y_mouse < y_center + height // 2):
			s.fill(GREEN)
		else:
			s.fill(DARKER_GREEN)

		# draw it
		window.blit(s, (x_center - s.get_width() // 2, y_center - s.get_height() // 2))

		start_text= "Start"
		start_text_size = s.get_height() // 3

		# get bounding rectangles of text
		start_text_rect = game_font.get_rect(start_text, size=start_text_size)

		# set the center points
		start_text_rect.center = (x_center, y_center)

		game_font.render_to(window, start_text_rect, start_text, BLACK, size = start_text_size)

	def draw_splash_screen(self, window, position):
		'''Draws the splash screen, including the various buttons.'''

		# draw the empty board as the background
		self.board.draw_board(window, pieces=False)

		# define text
		pretitle_text = "Welcome to"
		pretitle_text_size = 50
		title_text= "CHECKERS"
		title_text_size = 100

		# get bounding rectangles of text
		pretitle_text_rect = game_font.get_rect(pretitle_text, size = pretitle_text_size)
		title_text_rect = game_font.get_rect(title_text, size = title_text_size)

		# set the center points
		pretitle_text_rect.center = (TILE_SIZE * NUM_COLS / 2, TILE_SIZE * 2 - (TILE_SIZE / 2))
		title_text_rect.center = (TILE_SIZE * NUM_COLS / 2, TILE_SIZE * 3 - (TILE_SIZE / 2))

		game_font.render_to(window, pretitle_text_rect, pretitle_text, BLACK, size = pretitle_text_size)
		game_font.render_to(window, title_text_rect, title_text, BLACK, size = title_text_size)

		self.draw_start_button(window, position)
		self.draw_difficulty_button(window, position)
		self.draw_aggressive_button(window, position)

	def draw_game_over_screen(self, window):
		'''Draws the game over screen.'''

		# draw the empty board as the background
		self.board.draw_board(window, pieces=False)

		# define text
		title_text= "GAME OVER"
		title_text_size = 100

		button_text= "Click anywhere to return to splash screen"
		button_text_size = 30

		# get bounding rectangles of text
		title_text_rect = game_font.get_rect(title_text, size = title_text_size)
		button_text_rect = game_font.get_rect(button_text, size = button_text_size)

		# set the center points
		title_text_rect.center = (TILE_SIZE * NUM_COLS / 2, TILE_SIZE * 3 - (TILE_SIZE / 2))
		button_text_rect.center = (TILE_SIZE * NUM_COLS / 2, TILE_SIZE * 6 - (TILE_SIZE / 2))

		game_font.render_to(window, title_text_rect, title_text, BLACK, size = title_text_size)
		game_font.render_to(window, button_text_rect, button_text, BLACK, size = button_text_size)

	def draw_forced_capture_warning(self, window):
		'''Draws a temporary warning stating that a forced capture is available and needs to happen.'''

		# first draw board as usual
		self.board.draw_board(window)

		# we need to use a surface because pygame.rect doesn't allow for alpha blending
		s = pygame.Surface((TILE_SIZE*6, TILE_SIZE*2))
		s.set_alpha(200)
		s.fill(GRAY)

		# draw it
		window.blit(s, (TILE_SIZE, TILE_SIZE * 3))

		text= "You MUST make the capturing move."
		text_size = 30

		# get bounding rectangles of text
		text_rect = game_font.get_rect(text, size = text_size)

		# set the center points
		text_rect.center = (TILE_SIZE * NUM_COLS / 2, TILE_SIZE * NUM_ROWS / 2)

		game_font.render_to(window, text_rect, text, BLACK, size = text_size)


	def check_winner(self):
		'''Checks if a winner exists for the current game state.'''

		# check if the AI wone
		if self.board.is_winner(1):
			self.winner = 1

		# or if the human won
		elif self.board.is_winner(-1):
			self.winner = -1

		return


	def make_AI_move(self, player):
		'''Wrapper function for the minimax that determines the next best AI move. Also handles changing other game attributes as needed and updating game state.'''

		if self.difficulty_level == "Easy":
			depth = 5
			static_eval_limit = 5000
		elif self.difficulty_level == "Medium":
			depth = 6
			static_eval_limit = 7500
		elif self.difficulty_level == "Hard":
			depth = 6
			static_eval_limit = 10000

		# use minimax to determine the best move...
		alpha = -np.inf
		beta = np.inf
		evaluation, board_state = self.minimax_AB(self.board, depth, alpha, beta, player, 0, static_eval_limit, self.aggressive_AI)

		self.board = copy.deepcopy(board_state)

		self.current_player = self.current_player * -1

		self.board.update_force_capture_list()

		self.check_winner()

	def minimax_AB_wrapper(self, depth, alpha, beta, player):
		'''Wrapper function for testing. Not actually used in production...'''

		return self.minimax_AB(self.board, depth, alpha, beta, player)

	def minimax_AB(self, position, depth, alpha, beta, player, static_eval_count, static_eval_limit, aggressive):
		'''Returns value and position (i.e. a Board object.'''

		if depth == 0 or static_eval_count == static_eval_limit:
			if player == 1:
				return position.static_evaluation(aggressive), position
			else:
				return position.static_evaluation(aggressive=False), position

		if position.is_winner(1):
			return np.inf, position

		if position.is_winner(-1):
			return -np.inf, position

		# get possible moves for this player
		possible_next_moves = position.get_possible_next_moves(player)

		if len(possible_next_moves) <= 0:
			if player == 1:
				return position.static_evaluation(aggressive), position
			else:
				return position.static_evaluation(aggressive=False), position

		if player == 1:
			# white player
			max_evaluation = -np.inf
			best_move = None
			for child_board in possible_next_moves:
				evaluation, _ = self.minimax_AB(child_board, depth - 1, alpha, beta, -1, static_eval_count + 1, static_eval_limit, aggressive)
				max_evaluation = np.maximum(max_evaluation, evaluation)
				alpha = np.maximum(alpha, max_evaluation)
				if beta <= alpha:
					best_move = position
					break
				if max_evaluation == evaluation:
					best_move = child_board
			return max_evaluation, best_move

		elif player == -1:
			# black player
			min_evaluation = np.inf
			best_move = None
			for child_board in possible_next_moves:
				evaluation, _ = self.minimax_AB(child_board, depth - 1, alpha, beta, 1, static_eval_count + 1, static_eval_limit, aggressive)
				min_evaluation = np.minimum(min_evaluation, evaluation)
				beta = np.minimum(beta, min_evaluation)
				if beta <= alpha:
					best_move = position
					break
				if min_evaluation == evaluation:
					best_move = child_board
			return min_evaluation, best_move