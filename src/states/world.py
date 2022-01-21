from hmac import digest
from src.node_layering import *
from src.ds.graph import DirectedGraph
from src.states.state import *
from src.ui import colors
import math, os
import pygame
from pygame import gfxdraw
from pygame.math import Vector2
from src.camera import Camera
from src.ui.button import *

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

    def __init__(self, 
                project_dir, 
                resolver, 
                digraph: DirectedGraph, 
                layering: Layering):

        super().__init__(resolver)

        self.project_dir          = project_dir
        self.digraph              = digraph

        self.layering = layering

        self.camera = Camera(self.resolver.VIEW_W, self.resolver.VIEW_H, 0.1)

        self.reversed_edges = self.digraph.reversed_edges.copy()
        
        # vertex_id - point
        self.node_positons: dict[int, Vector2] = {}
        self.nodes: dict[int, Button] = {}

        self.rel_mouse_x, self.rel_mouse_y = 0, 0
        self.start_pan_x, self.start_pan_y = 0, 0

        self.holding_node  = None
        self.is_panning    = False
        
        self.__init_nodes()

        self.digraph.undo_reversed_edges()

    def __init_nodes(self):

        common_props = ButtonProperties(
                colors.DARK_CYAN,
                colors.WHITE,
                self.resolver.font,
                colors.BLUE
            )

        offset_x        = 0
        horizontal_step = 300
        vertical_step   = 400
        node_width      = 150
        node_height     = 50
        
        print(f"Total vertices = {len(self.digraph)}")
        print(f"order len = {len(self.layering.topological_order)}")
        print(f"{self.reversed_edges=}")
        print(f"{self.layering.layers=}")
        print(f"{self.layering.topological_order=}")

        missing_nodes = []

        for vtx_id in range(len(self.digraph)):

            if vtx_id not in self.layering.topological_order:
                missing_nodes.append(vtx_id)
                print(f"missing node {vtx_id} => {self.digraph.get_vertex_name(vtx_id)}")

                for out_vtx_id in range(len(self.digraph.get_neighbors_out(vtx_id))):
                    print(f"\t -> {self.digraph.get_vertex_name(out_vtx_id)}")

        print(f"{missing_nodes=}")

        elements_in_layer = [0] * (max(self.layering.layers)+1)

        for vtx_id in self.layering.topological_order:

            curr_layer = self.layering.layers[vtx_id]
            elements_in_layer[curr_layer] += 1
            
            node_text = self.digraph.get_vertex_name(vtx_id)

            if self.project_dir in node_text:
                node_text = node_text.replace(self.project_dir, "")
            else:
                node_text = os.path.basename(node_text)

            self.nodes[vtx_id] = Button(
                elements_in_layer[curr_layer]*horizontal_step + node_width/2, curr_layer*vertical_step + node_height/2,
                node_width, node_height, common_props, node_text
            )

            #print(f"{node_text} {curr_layer=} => {self.nodes[vtx_id].x} & {self.nodes[vtx_id].y} | size: {self.nodes[vtx_id].size}")
        
        self.camera.move_to(
            *self.nodes[self.layering.topological_order[-1]].center
        )


    def update_nodes(self, dt, actions):
        for node_id in self.nodes:
            node: Button = self.nodes.get(node_id)
            node.update(dt, self.rel_mouse_x, self.rel_mouse_y, actions["m_up"])

            if not self.holding_node and actions['m_down'] and node.is_hovered() and not self.is_panning:
                self.holding_node = node

        if self.holding_node:
            self.holding_node.set_pos(
                    self.rel_mouse_x - node.width/2,
                    self.rel_mouse_y - node.height/2
                )

        if actions['m_up']:
            self.holding_node = None

    def update(self, delta_time, actions):
        self.rel_mouse_x, self.rel_mouse_y = self.screen_to_world(self.resolver.scr_mouse_x, self.resolver.scr_mouse_y).xy

        self.update_nodes(delta_time, actions)

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
        elif self.is_panning and not self.holding_node:

            self.camera.move(
                -(self.resolver.scr_mouse_x - self.start_pan_x) / self.camera.zoom_factor,
                -(self.resolver.scr_mouse_y - self.start_pan_y) / self.camera.zoom_factor    
            )

        if self.is_panning:
             self.start_pan_x, self.start_pan_y = self.resolver.scr_mouse_x, self.resolver.scr_mouse_y 

    def choose_pivot_points(self, src_node: Button, dest_node: Button) -> Tuple[Tuple[int,int], Tuple[int,int]]:

        from_wx, from_wy = src_node.center
        to_wx, to_wy     = dest_node.center
    
        if from_wy > to_wy:
            from_wy -= src_node.height/2
            to_wy += dest_node.height/2
        else:
            from_wy += src_node.height/2
            to_wy -= dest_node.height/2

        return (from_wx, from_wy), (to_wx, to_wy)

    def render_nodes(self, display):
        for node_id in self.nodes:
            node: Button = self.nodes.get(node_id)
            node.render(display, 
                        self.camera.world_offset.x, 
                        self.camera.world_offset.y, 
                        self.camera.zoom_factor)

            # Draw outward lines
            for vtx_out in self.digraph.get_neighbors_out(node_id):

                start, end = self.choose_pivot_points(node, self.nodes[vtx_out])

                self.draw_arrow(display, colors.CYAN, colors.GREEN, start, end, 10, 2, 0, True)

        for rev_edge in self.reversed_edges:
            node0 = self.nodes[rev_edge[0]]
            node1 = self.nodes[rev_edge[1]]

            if rev_edge[0] in self.digraph.get_neighbors_out(rev_edge[1]):
                start, end = self.choose_pivot_points(node1, node0)
            else:
                start, end = self.choose_pivot_points(node0, node1)

            self.draw_arrow(display, colors.YELLOW, colors.YELLOW, start, end, 10, 3, 0, False)
            
    def render(self, display):
        display.fill(colors.DARK_GREY)
        self.render_nodes(display)

    def draw_circle(self, display, x, y, radius, color):
        """ Draws antialiased circle.
        """
        gfxdraw.aacircle(display, x, y, radius, color)
        gfxdraw.filled_circle(display, x, y, radius, color)

    def draw_arrow(self, display, lcolor, tricolor, start, end, trirad, lwidth = 2, ah_width = 2, arrow_from_start: bool = False):
        pygame.draw.line(display,
                        lcolor,
                        self.world_to_screen(*start),
                        self.world_to_screen(*end),
                        lwidth)

        rotation = math.degrees(math.atan2(start[1]-end[1], end[0]-start[0]))+90

        arrow_start_x = end[0]
        arrow_start_y = end[1]

        if arrow_from_start:
            arrow_start_x, arrow_start_y = (
                (end[0]+start[0])/2, 
                (start[1]+end[1])/2
            )

        p1 = self.world_to_screen(
            arrow_start_x+trirad*math.sin(math.radians(rotation)),
            arrow_start_y+trirad*math.cos(math.radians(rotation))
        )

        p2 = self.world_to_screen(
            arrow_start_x+trirad*math.sin(math.radians(rotation-120)), 
            arrow_start_y+trirad*math.cos(math.radians(rotation-120))
        )

        p3 = self.world_to_screen(
            arrow_start_x+trirad*math.sin(math.radians(rotation+120)), 
            arrow_start_y+trirad*math.cos(math.radians(rotation+120))
        )

        pygame.draw.polygon(
            display, 
            tricolor,
            [p1,p2,p3], 
            ah_width
        )