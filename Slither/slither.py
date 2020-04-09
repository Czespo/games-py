"""
    Slither (a Snake clone)
    Copyright (C) 2020 Guywan
    
    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.
    
    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.
    
    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>
"""

import random
import sys

import pygame

from pygame.locals import *

FULLSCREEN = False

B_WIDTH = 20
B_HEIGHT = 20

FPS = 10

BLACK = (0, 0, 0)
GRAY = (128, 128, 128)
DARK_GREEN = (0, 128, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)


def main():
    pygame.init()
    
    pygame.display.set_caption("Slither")
    pygame.display.set_icon(pygame.image.load("slither.png"))

    if FULLSCREEN:  # Launch in fullscreen mode.
        surface = pygame.display.set_mode((0, 0), pygame.constants.FULLSCREEN)
        w_width = surface.get_width()
        w_height = surface.get_height()
    
    else:  # Launch in windowed mode.
        w_width = 800
        w_height = 600
        surface = pygame.display.set_mode((w_width, w_height))
    
    # Determine cell size based on board and window dimensions.
    # Allows the drawn board to scale to the window size.
    CELL = min(w_width // B_WIDTH, w_height // B_HEIGHT)
    
    # Determine x and y padding, which are
    # used to centre the board within the window.
    XP = (w_width - (CELL * B_WIDTH)) // 2
    YP = (w_height - (CELL * B_HEIGHT)) // 2
    
    clock = pygame.time.Clock()
    
    surface.fill(GRAY)
    
    direction = K_RIGHT
    
    # Initialize the snake body.
    body = []
    length = 3
    for i in range(length):
        body.append({'x': B_WIDTH // 2 - i, 'y': B_HEIGHT // 2})

    # Initialize the food location.
    food = {'x': random.randrange(0, B_WIDTH), 'y': random.randrange(0, B_HEIGHT)}
    
    paused = False

    # Main game loop.
    while true:
        # Handle events.
        for event in pygame.event.get():
            
            if event.type == QUIT or (event.type == KEYUP and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()

            elif event.type == KEYDOWN:
            
                if event.key in [K_LEFT, K_UP, K_RIGHT, K_DOWN]:
                    direction = event.key

                elif event.key == K_p:
                    paused = not paused
        
        if paused:
            continue
        
        # Move the snake.
        nx = body[0]['x']
        ny = body[0]['y']
        if direction == K_LEFT:
            nx = body[0]['x'] - 1

        elif direction == K_UP:
            ny = body[0]['y'] - 1

        elif direction == K_RIGHT:
            nx = body[0]['x'] + 1

        else:
            ny = body[0]['y'] + 1

        # If the snake tries to go off the edge
        # of the board, wrap it around.
        if nx >= B_WIDTH:
            nx -= B_WIDTH
        
        elif nx < 0:
            nx += B_WIDTH
        
        elif ny >= B_HEIGHT:
            ny -= B_HEIGHT
        
        elif ny < 0:
            ny += B_HEIGHT

        # Move the snake by adding a new head.
        body.insert(0, {'x': nx, 'y': ny})

        # Check if the snake is eating food.
        if body[0] == food:
            # Increment length.
            length += 1

            # Set food to a new random location.
            food['x'] = random.randrange(0, B_WIDTH)
            food['y'] = random.randrange(0, B_HEIGHT)
        
        else:
            # If the snake hasn't eaten, remove the tail.
            body.pop()

        # Check if the snake is eating itself.
        # Start with the third part, since the
        # snake cannot eat any part before that.
        for i in range(2, length):
        
            if body[0] == body[i]:
                # Set length to 3 and trim body.
                length = 3
                while len(body) > length:
                    body.pop()

                break
        
        # Do drawing.
        
        # Fill the board with black.
        pygame.draw.rect(surface, BLACK, (XP, YP, CELL * B_WIDTH, CELL * B_HEIGHT))

        # Draw the snake's head, in dark green.
        pygame.draw.rect(surface, DARK_GREEN, (body[0]['x'] * CELL + XP, body[0]['y'] * CELL + YP, CELL - 1, CELL - 1))

        # Draw the rest of the body, in light green.
        for i in range(1, length):
            pygame.draw.rect(surface, GREEN, (body[i]['x'] * CELL + XP, body[i]['y'] * CELL + YP, CELL - 1, CELL - 1))

        # Draw the food.
        pygame.draw.rect(surface, RED, (food['x'] * CELL + XP, food['y'] * CELL + YP, CELL - 1, CELL - 1))

        # Update the window with the drawing performed.
        pygame.display.update()

        # Wait for 1000 / FPS milliseconds before continuing.
        # Controls how fast the snake moves.
        clock.tick(FPS)


if __name__ == "__main__":
    main()
