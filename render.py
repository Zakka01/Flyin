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
import random


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
        self.screen_width = 1350
        self.screen_height = 800
        self.zone_lookup = {z.name: z for z in self.zones}

        self.minheight = 0
        self.maxheight = 0
        self.minwidth = 0
        self.maxwidth = 0

        pygame.init()
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        self.clock = pygame.time.Clock()
        self.get_min_max()

        self.grid = []
        self.camera = [0, 0]
        self.drone_colors = {}

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
        offset_x = (self.screen_width - grid_width) // 2
        offset_y = (self.screen_height - grid_height) // 2

        if isinstance(zone, Zone):
            screen_x = offset_x + (zone.x - self.minwidth) * (cell_size + padding) + margin
            screen_y = offset_y + (zone.y - self.minheight) * (cell_size + padding) + margin
        else:
            screen_x = (offset_x + (zone.from_dst.x - self.minwidth) * (cell_size + padding) + margin) // 2 + \
                       (offset_x + (zone.to_dst.x - self.minwidth) * (cell_size + padding) + margin) // 2
            screen_y = (offset_y + (zone.from_dst.y - self.minheight) * (cell_size + padding) + margin) // 2 + \
                       (offset_y + (zone.to_dst.y - self.minheight) * (cell_size + padding) + margin) // 2

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
            elif zone.color is None:
                zone.color = (0, 120, 143)

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
                4,
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

        clear_colors = [
            "#FF6B6B", "#00BDB0", "#45B7D1", "#AC3100", "#6AFFDA",
            "#E4B600", "#BB8FCE", "#85C1E2", "#F8B88B", "#346D5B",
            "#E74C3C", "#0065A8", "#F39C12", "#9B59B6", "#1ABC9C",
            "#E67E22", "#00866C", "#2ECC71", "#D35400", "#8E44AD"
        ]
        for drone in self.drones:
            drone_num = int(drone.id[1:])  # extract number from "D1", "D2", etc
            self.drone_colors[drone.id] = clear_colors[drone_num % len(clear_colors)]

        for drone in self.drones:

            current = drone.current_zone()

            screen_x, screen_y = self.get_zone_screen_pos(current, cell_size, padding, margin)

            # Center drone inside zone
            drone_x = screen_x + (rect_size - drone_size) // 2
            drone_y = screen_y + (rect_size - drone_size) // 2

            drone_color = self.drone_colors[drone.id]
            pygame.draw.rect(
                self.screen,
                drone_color,
                [drone_x + 1 + self.camera[0], drone_y + 1 + self.camera[1], drone_size - 2, drone_size - 2],
                0,
                border_radius=100
            )
            pygame.draw.rect(
                self.screen,
                "white",
                [drone_x + self.camera[0], drone_y + self.camera[1], drone_size, drone_size],
                3,
                border_radius=100
            )

            font = pygame.font.Font(None, 20)
            text = font.render(drone.id, True, "white")
            text_rect = text.get_rect(center=(
                drone_x + drone_size // 2 + self.camera[0],
                drone_y + drone_size // 2 + self.camera[1]
            ))
            self.screen.blit(text, text_rect)

    def play(self):

        cell_size = 30
        drone_size = 30
        padding = 40
        thickness = 10

        running = True
        paused = False
        start = False

        while running:
            self.clock.tick(2)  # 2 FPS

            for event in pygame.event.get():
                if event.type == pygame.QUIT or \
                   (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                    running = False

                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE and start:
                        paused = not paused
                    
                    if event.key == pygame.K_RETURN:
                        start = True

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

            if not paused and start and self.simulator.is_running:
                turns = self.simulator.play()

            self.screen.fill("#003757")
            self.draw_connection(cell_size, padding)
            self.draw_zone(cell_size, padding, thickness)
            self.draw_drone(cell_size, padding, drone_size, thickness)

            pygame.display.flip()

        print(turns)
        pygame.quit()
