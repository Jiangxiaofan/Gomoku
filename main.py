import subprocess
from subprocess import PIPE
import json
import pygame, random, sys, time, math
from pygame.locals import *
import botone, bottwo, gomoku
import os

def quit():
    pygame.quit()
    sys.exit()

COUNTER_SIZE = 40
TILE_SIZE = 50
COUNTER_PADDING = 5
FPS = 40
BOARD_SIZE = 15
WINDOWWIDTH = TILE_SIZE * BOARD_SIZE
WINDOWHEIGHT = TILE_SIZE * BOARD_SIZE

class Engine(object):
    def __init__(self):
        super(Engine, self).__init__()
        self.resources = {}
        self.game = gomoku.Gomoku()

    def startup(self):
        pygame.init()
        self.main_clock = pygame.time.Clock()
        self.surface = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
        pygame.display.set_caption('Reversi')

        font = pygame.font.SysFont(None, 48)

        self.resources['board'] = pygame.image.load('media/board.png')
        self.resources['black'] = pygame.image.load('media/black.png')
        self.resources['white'] = pygame.image.load('media/white.png')

        self.render()

    def drawText(self, text, font, surface, x, y):
        textobj = font.render(text, 1, (0,0,0))
        textrect = textobj.get_rect()
        textrect.topleft = (x, y)
        surface.blit(textobj, textrect)

    def render(self):
        the_board = pygame.Rect(0, 0, WINDOWWIDTH, WINDOWHEIGHT)
        self.surface.blit(self.resources['board'], the_board)

        for x in range(BOARD_SIZE):
            for y in range(BOARD_SIZE):
                player = self.game.board[x][y]
                counter = pygame.Rect(x * TILE_SIZE + COUNTER_PADDING, y * TILE_SIZE + COUNTER_PADDING, COUNTER_SIZE, COUNTER_SIZE)

                if player == 1:
                    self.surface.blit(self.resources['white'], counter)
                elif player == 2:
                    self.surface.blit(self.resources['black'], counter)

        pygame.display.update()

    def new_game(self):
        self.game.__init__()

    def start(self):
        self.startup()
        self.new_game()
        move = (-1, -1)
        while True:
            for event in pygame.event.get():
                if event.type == QUIT:
                    quit()  
            if self.game.player == 1:
                p = subprocess.Popen(["python", "bot.py"],
                     shell=True,
                     stdin=PIPE,
                     stdout=PIPE,
                     universal_newlines=True)
                full_input = json.dumps(
                    {"requests": self.game.get_requests(),
                     "responses": self.game.get_responses()
                     })
                output, error = p.communicate(full_input)
                response = json.loads(output)["response"]
                move = (response['x'], response['y'])
            else:
                p = subprocess.Popen(["python", "bot.py"],
                     shell=True,
                     stdin=PIPE,
                     stdout=PIPE,
                     universal_newlines=True)
                full_input = json.dumps(
                    {"requests": self.game.get_requests(),
                     "responses": self.game.get_responses()
                     })
                output, error = p.communicate(full_input)
                response = json.loads(output)["response"]
                move = (response['x'], response['y'])
            winnner = self.game.perform_move(move)
            self.render()
            if winnner:
                break
            
            self.main_clock.tick(FPS)
        print("player {} wins".format(winnner))

if __name__ == '__main__':
        ge = Engine()
        ge.start()

