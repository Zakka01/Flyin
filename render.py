import warnings
import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
warnings.filterwarnings('ignore', category=RuntimeWarning)
from graph import Graph
from connection import Connection
from zone import Zone
from drone import Drone
from typing import List
import pygame


class Block:

    def __init__(self, y: int, x: int):
        """
            Initialize the attributes :
            x, y => ofc the coordinates,
            walls => if the block closed or not
            checked => if the block already visited or not
            ...
        """
        self.x = x
        self.y = y


class Render:
    def __init__(self,
                 zones: List[Zone],
                 connections: List[Connection]):
        self.zones = zones
        self.connections = connections
        self.minheight = 0
        self.maxheight = 0
        self.minwidth = 0
        self.maxwidth = 0
        pygame.init()
        self.screen = pygame.display.set_mode((1280, 720))
        self.clock = pygame.time.Clock()
        self.get_max()
        self.grid = []

    def get_max(self) -> None:
        x = []
        y = []
        for zone in self.zones:
            x.append(zone.x)
            y.append(zone.y)
        self.minheight = min(y)
        self.minwidth = min(x)
        self.maxheight = max(y)
        self.maxwidth = max(x)

    def build_grid(self):
        for y in range(self.minheight, self.maxheight):
            row = []
            for x in range(self.minwidth, self.maxwidth):
                row.append(Block(y, x))
            self.grid.append(row)

    def draw_zone(self):
        cell_size = 50

        grid_width = (self.maxwidth - self.minwidth) * cell_size
        grid_height = (self.maxheight - self.minheight) * cell_size

        offset_x = (1280 - grid_width) // 2
        offset_y = (720 - grid_height) // 2

        margin = 5
        rect_size = cell_size - 2 * margin

        for zone in self.zones:
            screen_x = offset_x + (zone.x - self.minwidth) * cell_size
            screen_y = offset_y + (zone.y - self.minheight) * cell_size

            pygame.draw.rect(
                self.screen,
                "white",
                [screen_x, screen_y, rect_size, rect_size],
                3,
                border_radius=300
            )

    def play(self):
        running = True
        self.build_grid()

        while running:
            self.clock.tick(60)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            self.screen.fill("black")

            self.draw_zone()

            pygame.display.flip()

        pygame.quit()
