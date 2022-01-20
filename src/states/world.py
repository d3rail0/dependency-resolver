from src.ds.graph import DirectedGraph
from src.states.state import *
from src.ui import colors
import math
import pygame
from pygame import gfxdraw
from pygame.math import Vector2
from src.camera import Camera

class World(State):

    def world_to_screen(self, world_x, world_y) -> pygame.Vector2:
        return pygame.Vector2(
            int((world_x - self.camera.world_offset.x) * self.camera.zoom_factor),
            int((world_y - self.camera.world_offset.y) * self.camera.zoom_factor)
        )

    def screen_to_world(self, scr_x, scr_y) -> pygame.Vector2:
        return pygame.Vector2(
            scr_x / self.camera.zoom_factor + self.camera.world_offset.x,
            scr_y / self.camera.zoom_factor + self.camera.world_offset.y
        )

    def __init__(self, resolver, digraph: DirectedGraph, topological_ordering: list[int], layerings: list[int]):
        super().__init__(resolver)

        self.digraph = digraph
        self.topological_ordering = topological_ordering
        self.layerings = layerings

        # vertex_id - point
        self.node_positons: dict[int, Vector2] = {}

        self.rel_mouse_x, self.rel_mouse_y = 0, 0
        self.start_pan_x, self.start_pan_y = 0, 0

        self.is_panning = False
        self.camera     = Camera(self.resolver.VIEW_W, self.resolver.VIEW_H, 0.1)

        self.__init_layers()

    def __init_layers(self):
        self.node_positons = {
            0: Vector2(0, 0),
            1: Vector2(self.resolver.VIEW_W, 0),
            2: Vector2(0, self.resolver.VIEW_H),
            3: Vector2(self.resolver.VIEW_W, self.resolver.VIEW_H),
        }

    def update(self, delta_time, actions):

        self.rel_mouse_x, self.rel_mouse_y = self.screen_to_world(self.resolver.scr_mouse_x, self.resolver.scr_mouse_y).xy

        if actions['m_up']:
            self.is_panning = False
        if actions['m_down'] and not self.is_panning:
            self.is_panning = True
            self.start_pan_x, self.start_pan_y = self.resolver.scr_mouse_x, self.resolver.scr_mouse_y 

        if not math.isclose(self.resolver.zoom_delta, 0.0):
            bf_zoom_x, bf_zoom_y = self.rel_mouse_x, self.rel_mouse_y
            self.camera.zoom(self.resolver.zoom_delta)
            after_zoom_x, after_zoom_y = self.screen_to_world(self.resolver.scr_mouse_x, self.resolver.scr_mouse_y)
            self.camera.move(
                (bf_zoom_x - after_zoom_x),
                (bf_zoom_y - after_zoom_y) 
            )

        if actions.get('escape'):
            self.exit_state()
        elif self.is_panning:

            self.camera.move(
                -(self.resolver.scr_mouse_x - self.start_pan_x) / self.camera.zoom_factor,
                -(self.resolver.scr_mouse_y - self.start_pan_y) / self.camera.zoom_factor    
            )

        if self.is_panning:
             self.start_pan_x, self.start_pan_y = self.resolver.scr_mouse_x, self.resolver.scr_mouse_y 

    def render(self, display):
        rel_mouse_pos = (self.rel_mouse_x, self.rel_mouse_y)
        # print(rel_mouse_pos)
        display.fill(colors.DARK_GREY)
        self.resolver.draw_text(display, "topol = " + str(self.topological_ordering), 
            colors.WHITE, self.camera.VIEW_WIDTH/2, self.camera.VIEW_HEIGHT/2 - self.resolver.font.get_height())

        for node, pos in self.node_positons.items():
            translated_pos = self.world_to_screen(*pos)
            is_hovered = (
            rel_mouse_pos[0] > pos.x - 20 and
            rel_mouse_pos[0] < pos.x + 20 and
            rel_mouse_pos[1] > pos.y - 20 and 
            rel_mouse_pos[1] < pos.y + 20)
            self.draw_circle(display, int(translated_pos.x), int(translated_pos.y), int(20 * self.camera.zoom_factor), colors.RED if not is_hovered else colors.YELLOW)

        # self.resolver.draw_text(display, "layers = " + str(self.layerings), 
        #     colors.WHITE, self.resolver.VIEW_W/2, self.resolver.VIEW_H/2 + self.resolver.font.get_height() )

        # self.resolver.draw_text(display, "reversed = " + str(self.digraph.reversed_edges), 
        #     colors.WHITE, self.resolver.VIEW_W/2, self.resolver.VIEW_H/2 + 2*self.resolver.font.get_height() )

    def draw_circle(self, surface, x, y, radius, color):
        """ Draws antialiased circle.
        """
        gfxdraw.aacircle(surface, x, y, radius, color)
        gfxdraw.filled_circle(surface, x, y, radius, color)