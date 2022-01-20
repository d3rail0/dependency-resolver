import pygame
from pygame import gfxdraw
from pygame.math import Vector2
import math

class Camera:

    @property
    def world_offset(self) -> Vector2:
        return self.__world_pos_i

    @property
    def VIEW_WIDTH(self) -> int:
        return self.__view_width

    @property
    def VIEW_HEIGHT(self) -> int:
        return self.__view_height

    @property
    def zoom_factor(self) -> float:
        return self.__zoom_factor

    def __init__(self, view_width, view_height, zoom_step:float) -> None:
        
        self.__world_pos_f   = Vector2(0,0)
        self.__world_pos_i   = Vector2(0,0)

        self.__view_width  = view_width
        self.__view_height = view_height
        self.__zoom_factor = 1.

        # zoom properties
        self.zoom_in_speed  = 1 - zoom_step
        self.zoom_out_speed = 1 + zoom_step
        self.lower_bound    = zoom_step
        self.upper_bound    = 5

        self.__CENTER = Vector2(-view_width/2, -view_height/2)

    def __update_int_offset(self) -> None:
        self.__world_pos_i.x, self.__world_pos_i.y = int(self.__world_pos_f.x), int(self.__world_pos_f.y)
    
    def move(self, dx, dy) -> None:
        self.__world_pos_f.x += dx
        self.__world_pos_f.y += dy
        self.__update_int_offset()

    def move_to(self, x, y) -> None:
        self.__world_pos_f.x += (x - self.__world_pos_f.x + self.__CENTER.x)
        self.__world_pos_f.y += (y - self.__world_pos_f.y + self.__CENTER.y)
        self.__update_int_offset()

    def zoom_in(self):
        if self.__zoom_factor * self.zoom_in_speed < self.lower_bound:
            self.__zoom_factor = self.lower_bound
        else:
            self.__zoom_factor *= self.zoom_in_speed

    def zoom_out(self):
        if self.__zoom_factor * self.zoom_out_speed > self.upper_bound:
            self.__zoom_factor = self.upper_bound
        else:
            self.__zoom_factor *= self.zoom_out_speed

    def zoom(self, scroll_dy):
        """ Applies appropriate zoom depending on
        scroll direction. 
        """
        if scroll_dy < 0:
            self.zoom_in()
        else:
            self.zoom_out()