from src.states.state import *

class World(State):

    def __init__(self, resolver):
        super().__init__(resolver)

    def update(self, delta_time, actions):
        self.resolver.reset_keys()

    def render(self, display):
        display.fill((0,0,0))
        self.resolver.draw_text(display, "World state", (255,255,255), self.resolver.VIEW_W/2, self.resolver.VIEW_H/2 )