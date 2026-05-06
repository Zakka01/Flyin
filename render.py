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
        print(f"width :{self.minwidth} {self.maxwidth}")
        print(f"height {self.minheight} {self.maxheight}")

    def build_grid(self):
        for y in range(self.minheight, self.maxheight):
            row = []
            for x in range(self.minwidth, self.maxwidth):
                row.append(Block(y, x))
            self.grid.append(row)

    def draw_zone(self, cell_size):

        grid_width = (self.maxwidth - self.minwidth) * cell_size
        grid_height = (self.maxheight - self.minheight) * cell_size

        offset_x = (1280 - grid_width) // 2
        offset_y = (720 - grid_height) // 2

        margin = 10
        rect_size = cell_size - 2 * margin

        for zone in self.zones:
            screen_x = offset_x + (zone.x - self.minwidth) * cell_size
            screen_y = offset_y + (zone.y - self.minheight) * cell_size

            if zone.color == "rainbow":
                zone.color = "red"

            if zone.is_zone_restricted():
                fill = (220, 77, 1)
            elif zone.is_zone_blocked():
                fill = "red"
            elif zone.is_zone_priority():
                fill = "green"
            else:
                fill = "#DAB1DA"

            # print(zone.color)
            pygame.draw.rect(
                self.screen,
                fill,
                [screen_x, screen_y, rect_size, rect_size],
                0,
                border_radius=300
            )
            pygame.draw.rect(
                self.screen,
                zone.color,
                [screen_x, screen_y, rect_size, rect_size],
                5,
                border_radius=300
            )

    def play(self):
        running = True
        self.build_grid()
        cell_size = 75

        while running:
            self.clock.tick(60)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        cell_size += 5
                    if event.key == pygame.K_DOWN and cell_size > 55:
                        cell_size -= 5
                    print(cell_size)

            self.screen.fill((156, 173, 120))

            self.draw_zone(cell_size)
            # self.draw_connection()

            pygame.display.flip()

        pygame.quit()
