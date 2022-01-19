from typing import Tuple
import pygame
from enum import Enum

class ClickableState(Enum):
    IDLE    = 0
    HOVERED = 1
    CLICKED = 2

class ButtonProperties:

    def __init__(self, base_color, text_color, font: pygame.font.Font, hover_color=(0,0,0), clicked_color=(0,0,0)) -> None:
        self.base_color    : pygame.Color = base_color
        self.text_color    : pygame.Color = text_color

        self.hover_color = self.clicked_color = self.base_color

        if hover_color != (0,0,0):
            self.hover_color = hover_color
        
        if clicked_color != (0,0,0):
            self.clicked_color = clicked_color

        self.font : pygame.font.Font  = font

class Button():

    @property
    def x(self):
        return self.__rect.x

    @property
    def y(self):
        return self.__rect.x

    @property
    def width(self):
        return self.__rect.width

    @property
    def height(self):
        return self.__rect.height

    @property
    def position(self):
        return (self.x, self.y)

    @property
    def size(self):
        return (self.width, self.height)

    @position.setter
    def position(self, pos: Tuple[int, int]):
        self.__rect.x = pos[0]
        self.__rect.y = pos[1]

    @size.setter
    def size(self, size: Tuple[int, int]):
        self.__rect.width  = size[0]
        self.__rect.height = size[1]

    def __init__(self, x, y, width, height, props: ButtonProperties, text="") -> None:
        self.__rect      = pygame.Rect(x,y,width,height)
        self.properties  = props

        self.state: ClickableState = ClickableState.IDLE

        self.set_text(text)

    def _draw_text(self, surface:pygame.Surface) -> None:        
        text_surface     = self.properties.font.render(self.text, True, self.properties.text_color)
        text_rect        = text_surface.get_rect()
        text_rect.center = self.__rect.center
        surface.blit(text_surface, text_rect)

    def _draw_button(self, display:pygame.Surface):    

        if self.state == ClickableState.HOVERED:
            target_color = self.properties.hover_color
        elif self.state == ClickableState.CLICKED:
            target_color = self.properties.clicked_color
        else:
            target_color = self.properties.base_color

        pygame.draw.rect(
            display,
            target_color,
            self.__rect
        )

    def set_text(self, text:str):
        self.text = text

    def update(self, dt, mouse_x, mouse_y, is_clicked: bool):
        if self.__rect.collidepoint(mouse_x, mouse_y):
            self.state = ClickableState.HOVERED
            if is_clicked:
                self.state = ClickableState.CLICKED
        else:
            self.state = ClickableState.IDLE

    def render(self, display:pygame.Surface):
        self._draw_button(display)
        self._draw_text(display)

    def is_hovered(self) -> bool:
        return self.state == ClickableState.HOVERED

    def is_clicked(self) -> bool:
        return self.state == ClickableState.CLICKED