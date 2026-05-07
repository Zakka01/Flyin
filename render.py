import warnings
import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
warnings.filterwarnings('ignore', category=RuntimeWarning)
from graph import Graph
from connection import Connection
from zone import Zone
from drone import Drone
from simulator import Simulator
from typing import List
import pygame


class Render:
    def __init__(self,
                 zones: List[Zone],
                 connections: dict,
                 graph: Graph,
                 drones: List[Drone],
                 simulator: Simulator):

        self.graph = graph
        self.simulator = simulator
        self.zones = zones
        self.connections = connections
        self.drones = drones
        self.zone_lookup = {z.name: z for z in self.zones}
        self.minheight = 0
        self.maxheight = 0
        self.minwidth = 0
        self.maxwidth = 0

        pygame.init()
        self.screen = pygame.display.set_mode((1280, 720))
        self.clock = pygame.time.Clock()
        self.get_min_max()

        self.grid = []
        self.camera = [0, 0]

    def get_min_max(self) -> None:
        x = []
        y = []
        for zone in self.zones:
            x.append(zone.x)
            y.append(zone.y)

        self.minheight = min(y)
        self.minwidth = min(x)

        self.maxheight = max(y)
        self.maxwidth = max(x)

    def get_zone_screen_pos(self, zone, cell_size, padding, margin):

        grid_width = (self.maxwidth - self.minwidth) * (cell_size + padding)
        grid_height = (self.maxheight - self.minheight) * (cell_size + padding)
        offset_x = (1280 - grid_width) // 2
        offset_y = (720 - grid_height) // 2

        screen_x = offset_x + (zone.x - self.minwidth) * (cell_size + padding) + margin
        screen_y = offset_y + (zone.y - self.minheight) * (cell_size + padding) + margin

        return screen_x, screen_y

    def get_zone_center(self, zone, cell_size, padding, margin):

        screen_x, screen_y = self.get_zone_screen_pos(zone, cell_size, padding, margin)

        rect_size = (cell_size + padding) - 2 * margin
        center_x = screen_x + rect_size // 2
        center_y = screen_y + rect_size // 2

        return center_x, center_y

    def draw_zone(self, cell_size, padding, thickness):
        margin = 10
        rect_size = (cell_size + padding) - 2 * margin

        for zone in self.zones:
            screen_x, screen_y = self.get_zone_screen_pos(zone, cell_size, padding, margin)

            if zone.color == "rainbow":
                zone.color = (220, 77, 1)

            if zone.is_zone_restricted():
                fill = "#E78311"
                center_fill = "#CF5300"
            elif zone.is_zone_blocked():
                fill = "red"
                center_fill = "#690000"
            elif zone.is_zone_priority():
                fill = "#00E479"
                center_fill = "#00B42D"
            elif zone.name == self.graph.start_hub.name:
                fill = "#EA01FF"
                center_fill = "#72007C"
            elif zone.name == self.graph.end_hub.name:
                fill = "#B8AB00"
                center_fill = "#E5FF00"
            else:
                center_fill = "#007C8F"
                fill = "#00A8C2"
            
            pygame.draw.rect(
                self.screen,
                center_fill,
                [screen_x + self.camera[0], screen_y + self.camera[1], rect_size, rect_size],
                0,
                border_radius=100
            )

            pygame.draw.rect(
                self.screen,
                fill,
                [screen_x + self.camera[0], screen_y + self.camera[1], rect_size, rect_size],
                thickness,
                border_radius=100
            )

            pygame.draw.rect(
                self.screen,
                zone.color,
                [screen_x + self.camera[0], screen_y + self.camera[1], rect_size, rect_size],
                2,
                border_radius=100
            )

    def draw_connection(self, cell_size, padding):
        margin = 10

        for zone_name, neighbors in self.connections.items():
            zone = self.zone_lookup[zone_name]
            zone_center_x, zone_center_y = self.get_zone_center(zone, cell_size, padding, margin)

            for neighbor_zone, capacity in neighbors:
                neighbor_center_x, neighbor_center_y = self.get_zone_center(neighbor_zone, cell_size, padding, margin)
                pygame.draw.line(
                    self.screen, 
                    "#6DC5D4",
                    (zone_center_x + self.camera[0], zone_center_y + self.camera[1]),
                    (neighbor_center_x + self.camera[0], neighbor_center_y + self.camera[1]),
                    2
                )

    def draw_drone(self, cell_size, padding, drone_size, thickness):
        margin = 10
        rect_size = (cell_size + padding) - 2 * margin

        for drone in self.drones:
            current = drone.current_zone()
            screen_x, screen_y = self.get_zone_screen_pos(current, cell_size, padding, margin)

            # Center drone inside zone
            drone_x = screen_x + (rect_size - drone_size) // 2
            drone_y = screen_y + (rect_size - drone_size) // 2

            pygame.draw.rect(
                self.screen,
                "#FFF38B",
                [drone_x + 1 + self.camera[0], drone_y + 1 + self.camera[1], drone_size - 2, drone_size - 2],
                0,
                border_radius=100
            )
            pygame.draw.rect(
                self.screen,
                "#FF9100",
                [drone_x + self.camera[0], drone_y + self.camera[1], drone_size, drone_size],
                thickness,
                border_radius=100
            )

    def play(self):
        running = True
        cell_size = 35
        drone_size = 30
        padding = 40
        thickness = 10

        while running:
            self.clock.tick(5)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        cell_size += 5
                        if thickness < 10:
                            thickness += 2

                    if event.key == pygame.K_DOWN and cell_size > 0:
                        cell_size -= 5
                        if thickness > 7:
                            thickness -= 2

                    if event.key == pygame.K_LEFT:
                        self.camera[0] -= 20
                    if event.key == pygame.K_RIGHT:
                        self.camera[0] += 20

            self.screen.fill("#00515E")

            self.draw_connection(cell_size, padding)
            self.draw_zone(cell_size, padding, thickness)
            self.draw_drone(cell_size, padding, drone_size, thickness)

            self.simulator.play()

            pygame.display.flip()

        pygame.quit()
