from src.ds.graph import DirectedGraph
from src.states.state import *
from src.ui import colors

class World(State):

    def __init__(self, resolver, digraph: DirectedGraph, topological_ordering: list[int], layerings: list[int]):
        super().__init__(resolver)

        self.digraph = digraph
        self.topological_ordering = topological_ordering
        self.layerings = layerings

        self.__init_layers()

    def __init_layers(self):
        pass

    def update(self, delta_time, actions):
        
        if actions.get('escape'):
            self.exit_state()

        self.resolver.reset_keys()

    def render(self, display):
        display.fill(colors.DARK_GREY)
        self.resolver.draw_text(display, "topol = " + str(self.topological_ordering), 
            colors.WHITE, self.resolver.VIEW_W/2, self.resolver.VIEW_H/2 - self.resolver.font.get_height())

        self.resolver.draw_text(display, "layers = " + str(self.layerings), 
            colors.WHITE, self.resolver.VIEW_W/2, self.resolver.VIEW_H/2 + self.resolver.font.get_height() )

        self.resolver.draw_text(display, "reversed = " + str(self.digraph.reversed_edges), 
            colors.WHITE, self.resolver.VIEW_W/2, self.resolver.VIEW_H/2 + 2*self.resolver.font.get_height() )