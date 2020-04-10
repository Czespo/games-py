"""
    Divergence (a Sokoban (or Sokouban if you're a purist) clone)
    Copyright (C) 2020 Czespo
    
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

import sys
import re

import pygame

from pygame.locals import *

FULLSCREEN = True

W_WIDTH = 800
W_HEIGHT = 600

FPS = 10

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

FLOOR = 1
WALL = 2

LEVELS = []


class Cell:

    def __init__(self, type: int, isGoal: bool, hasBox: bool, onGoal: bool):
        self.type = type
        self.isGoal = isGoal
        self.hasBox = hasBox
        self.onGoal = onGoal


class Level:

    def __init__(self, width=0, height=0, goals=0):
        self.width = width
        self.height = height
        self.goals = goals
        
        self.player = {'x': 0, 'y': 0}
        
        self.map = []
    
    def get(self, coord: dict):
        return self.map[coord['y']][coord['x']]


def main():
    global SURFACE, FONT, W_WIDTH, W_HEIGHT

    if not initLevels():
        return
    
    pygame.init()
    
    pygame.display.set_caption("Divergence")
    pygame.display.set_icon(pygame.image.load("divergence.png"))
    
    if FULLSCREEN:  # Launch in fullscreen mode.
        SURFACE = pygame.display.set_mode((0, 0), pygame.constants.FULLSCREEN)
        W_WIDTH = SURFACE.get_width()
        W_HEIGHT = SURFACE.get_height()
    
    else:  # Launch in windowed mode.
        SURFACE = pygame.display.set_mode((W_WIDTH, W_HEIGHT))

    clock = pygame.time.Clock()
    
    curLevel = 0

    complete = False

    # Load first level.
    level = loadLevel(LEVELS[curLevel])

    # Draw initial state.
    draw(level)

    # Main game loop.
    while True:
        # Handle events.
        for event in pygame.event.get():
        
            if event.type == QUIT or (event.type == KEYUP and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()
            
            elif event.type == KEYDOWN:
            
                if event.key in (K_LEFT, K_UP, K_RIGHT, K_DOWN):
                    # Move the player, if possible.
                    # If level is complete, load the next one.
                    if update(event.key, level):
                        # Wait a bit, for esoteric reasons.
                        pygame.time.wait(800)
                        
                        curLevel += 1
                        if curLevel < len(LEVELS):
                            level = loadLevel(LEVELS[curLevel])
                            draw(level)

                        else:
                            print("All levels completed.")
                            pygame.quit()
                            sys.exit(0)

                elif event.key == K_r:
                    # Restart the current level.
                    level = loadLevel(LEVELS[curLevel])
                    draw(level)
        
        clock.tick(20)


def initLevels() -> bool:
    # Load definition strings of Divergence
    # levels from the level file.
    try:
        levelFile = open("levels")

    except FileNotFoundError:
        print("Error: could not find 'levels'!")
        
        return False

    level = ""
    for line in re.split("\r\n|\r|\n", levelFile.read()):

        if line == ",":
            LEVELS.append(level)
            level = ""

        else:
            level += line + "|"

    levelFile.close()

    return True


def loadLevel(definition: str) -> Level:
    global CELL, XP, YP
    
    # Create a Divergence level from a definition string.
    level = Level()
    level.map.append([])

    width = 0
    height = 0
    x = 0
    for i in definition:
        
        if i == ".":  # Goal.
            level.map[height].append(Cell(FLOOR, True, False, False))
            level.goals += 1
        
        elif i == "$":  # Box.
            level.map[height].append(Cell(FLOOR, False, True, False))
        
        elif i == "*":  # Box over goal.
            level.map[height].append(Cell(FLOOR, True, True, True))

        elif i == "#":  # Wall.
            level.map[height].append(Cell(WALL, False, False, False))

        elif i == "@":  # Player.
            level.player = {'x': x, 'y': height}
            level.map[height].append(Cell(FLOOR, False, False, False))
        
        elif i == "&":  # Player over goal.
            level.player = {'x': x, 'y': height}
            level.map[height].append(Cell(FLOOR, True, False, False))
            level.goals += 1

        elif i == "|":  # Start a new row.
            height += 1
            if x > width:
                width = x

            x = -1
            level.map.append([])

        else:  # Empty floor.
            level.map[height].append(Cell(FLOOR, False, False, False))

        x += 1

    level.width = width
    level.height = height

    # Determine cell size based on level and window dimensions.
    # Allows the drawn map to scale to the window size.
    CELL = min(W_WIDTH // width, W_HEIGHT // height)

    # Determine x and y padding, which are
    # used to centre the level within the window.
    XP = (W_WIDTH - (CELL * width)) // 2
    YP = (W_HEIGHT - (CELL * height)) // 2

    return level


def update(direction: int, level: Level) -> bool:
    dest = move(direction, level.player)
    if level.get(dest).type != WALL:
        # If the player moves into a box, we try to push that box.
        if level.get(dest).hasBox and moveBox(direction, dest, level):
            level.player = dest
            
            draw(level)
            
            # Check if the level has been completed.
            if level.goals == 0:
                return True

        elif not level.get(dest).hasBox:
            level.player = dest
            
            draw(level)
    
    return False


def move(direction: int, src: dict) -> dict:
    
    if direction == K_LEFT: return {'x': src['x'] - 1, 'y': src['y']}
    if direction == K_UP: return {'x': src['x'], 'y': src['y'] - 1}
    if direction == K_RIGHT: return {'x': src['x'] + 1, 'y': src['y']}
    if direction == K_DOWN: return {'x': src['x'], 'y': src['y'] + 1}


def moveBox(direction: int, src: dict, level: Level) -> bool:
    # We move the box if the destination does not
    # contain a wall or another box.
    dest = move(direction, src)
    if level.get(dest).type != WALL and not level.get(dest).hasBox:
        level.get(src).hasBox = False
        level.get(dest).hasBox = True
        
        # Increment remaining goals if the box was pushed off a goal.
        if level.get(src).isGoal:
            level.get(src).onGoal = False
            level.goals += 1
        
        # Decrement remaining goals if the box was pushed onto a goal.
        if level.get(dest).isGoal:
            level.get(dest).onGoal = True
            level.goals -= 1

        return True

    return False


def draw(level: Level):
    # Fill the entire surface with black.
    SURFACE.fill(BLACK)

    # Used to draw goals, which need to
    # be comparatively smaller than boxes.
    quarter = CELL // 4
    
    for y in range(level.height):

        for x in range(len(level.map[y])):
            cell = level.map[y][x]
            if cell.type == FLOOR:

                if cell.hasBox:
                    # Determine what colour the box should be.
                    # If the box is on a goal, draw it in green
                    # to differentiate it from other boxes.
                    colour = GREEN if cell.onGoal else RED

                    # Draw the boxes.
                    pygame.draw.rect(SURFACE, colour, (x * CELL + XP, y * CELL + YP, CELL - 1, CELL - 1))

                elif cell.isGoal:
                    # Draw the goals.
                    pygame.draw.rect(SURFACE, RED, (x * CELL + quarter + XP, y * CELL + quarter + YP, CELL - quarter * 2 - 1, CELL - quarter * 2 - 1))
            
            else:
                # Draw the walls.
                pygame.draw.rect(SURFACE, WHITE, (x * CELL + XP, y * CELL + YP, CELL - 1, CELL - 1))

    # Draw the player.
    pygame.draw.rect(SURFACE, BLUE, (level.player['x'] * CELL + XP, level.player['y'] * CELL + YP, CELL - 1, CELL - 1))

    # Update the window with the drawing performed.
    pygame.display.update()


if __name__ == "__main__":
    main()
