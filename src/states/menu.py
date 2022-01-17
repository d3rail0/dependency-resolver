from __future__ import annotations
from src.states.state import *
from src.states.world import World

class Menu(State):

    def __init__(self, resolver):
        super().__init__(resolver)

    def update(self, delta_time, actions):
        if actions["action1"]:
            new_state = World(self.resolver)
            new_state.enter_state()
        self.resolver.reset_keys()

    def render(self, display):
        display.fill((255,255,255))
        self.resolver.draw_text(display, "Menu state", (0,0,0), self.resolver.VIEW_W/2, self.resolver.VIEW_H/2 )