# Will Kearney
# piece.py
#
# Defines the Piece class, containing methods for drawing a piece, checking if it's selected

import pygame
import numpy as np
import itertools
import copy

from .constants import *

class Piece(object):
	"""Class for representing a checkers piece. These are stored in a Board.board[row, col]."""
	def __init__(self, indicator, row, col):
		super(Piece, self).__init__()

		self.indicator = indicator

		if indicator == 1:
			# this is a white piece
			self.color = WHITE
		elif indicator == -1:
			# this is a black piece
			self.color = BLACK
		else:
			print("Piece indicator must initially be either 1 (white) or -1 (black)")

		self.king = False

		# each piece know's its own location
		self.row = row
		self.col = col

		self.selected = False # flag to determine if a piece is selected

	def check_select(self, x, y):
		'''Given an x and a y, check if this piece get's selected.'''

		# get x and y coordinates of piece on board
		center_y = (self.row * TILE_SIZE) + int(TILE_SIZE / 2)
		center_x = (self.col * TILE_SIZE) + int(TILE_SIZE / 2)

		if (x - center_x) ** 2 + (y - center_y) ** 2 < PIECE_RADIUS_SELECTED ** 2:
			# this piece should indeed be selected (or toggled off)
			return True
		else:
			return False
	
	def draw_piece(self, window):
		'''Given a pygame window, draw the piece on the board.'''

		# x_center and y_center are the center of the circle in window coordinates
		x_center = self.col * TILE_SIZE + (TILE_SIZE / 2)
		y_center = self.row * TILE_SIZE + (TILE_SIZE / 2)

		x_king = x_center - KING_ICON_SCALE // 2
		y_king = y_center - KING_ICON_SCALE // 2

		if self.selected:
			pygame.draw.circle(window, RED, (x_center, y_center), PIECE_RADIUS_SELECTED, 0)
			pygame.draw.circle(window, self.color, (x_center, y_center), PIECE_RADIUS, 0) # last argument is the thickness of the circle border
		else:
			pygame.draw.circle(window, self.color, (x_center, y_center), PIECE_RADIUS, 0)

		if self.king and self.indicator == 1:
			window.blit(WHITE_KING_ICON, (x_king, y_king))
		elif self.king and self.indicator == -1:
			window.blit(BLACK_KING_ICON, (x_king, y_king))