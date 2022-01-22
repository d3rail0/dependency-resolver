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

class LineColors:

    def __init__(self) -> None:
        self.l_default   = colors.CYAN
        self.l_cycle     = colors.YELLOW
        self.arw_default = colors.GREEN
        self.arw_cycle   = colors.YELLOW
        self.highlight   = colors.MAGENTA

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
        
        # Warning for cycle
        self.warning_message = ""
        self.warning_image   = pygame.image.load(os.path.join(self.resolver.images_dir, "warning_32_32.png"))
        self.show_warning    = False
        self.is_full_cycle   = False

        self.bends_enabled = True
        self.line_colors = LineColors()

        self.__init_warning()
        self.__init_nodes()

        # Return graph back to its initial state (with cycle if it had one)
        self.digraph.undo_reversed_edges()
        # Perform a proper layering on initial graph state
        layering.proper_layering()

    def __init_nodes(self):

        common_props = ButtonProperties(
                colors.DARK_CYAN,
                colors.WHITE,
                self.resolver.font,
                colors.BLUE
            )

        self.horizontal_step = 300
        self.vertical_step   = 400
        self.node_width      = 150
        self.node_height     = 50
        
        print(f"Total vertices = {len(self.digraph)}")
        print(f"order len = {len(self.layering.topological_order)}")
        
        print(f"{self.reversed_edges=}")
        print(f"layers:\n{self.layering.layers_to_str()}")
        print(f"{self.layering.topological_order=}")
        print(f"{self.layering.dummy_traversing_edges=}")

        if self.is_full_cycle:
            return

        for layer in self.layering.layers:
            layer: Layer

            # Create initial nodes and leave empty spaces in places of dummy vertices
            for i, vtx_id in enumerate(layer.nodes):
                
                if vtx_id == -1:
                    continue

                node_text = self.digraph.get_vertex_name(vtx_id)

                if self.project_dir in node_text:
                    node_text = node_text.replace(self.project_dir, "")
                else:
                    node_text = os.path.basename(node_text)

                self.nodes[vtx_id] = Button(
                    i*self.horizontal_step + self.node_width/2, layer.level*self.vertical_step + self.node_height/2,
                    self.node_width, self.node_height, common_props, node_text
                )

                print(f"{i}. {node_text} {layer.level=} => {self.nodes[vtx_id].x} & {self.nodes[vtx_id].y} | size: {self.nodes[vtx_id].size}")
        
        self.camera.move_to(
            *self.nodes[self.layering.topological_order[-1]].center
        )

    def __init_warning(self) -> None:
        if len(self.digraph) != 0 and len(self.layering.topological_order) == 0:
            # Graph is a fully cycle, turn on the warning.
            self.warning_message = "All vertices are in the cycle"
            self.show_warning  = True
            self.is_full_cycle = True 
        elif len(self.reversed_edges) != 0:
            # Some edges were reversed in order to remove a cycle from the graph
            self.warning_message = "Cyclic dependency detected"
            self.show_warning  = True
            self.is_full_cycle = False
            
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
        elif actions['m_down'] and not self.is_panning:
            self.is_panning = True
            self.start_pan_x, self.start_pan_y = self.resolver.scr_mouse_x, self.resolver.scr_mouse_y 
        elif actions['space']:
            self.bends_enabled = not self.bends_enabled
            actions['space'] = False

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
            to_wy   += dest_node.height/2
        else:
            from_wy += src_node.height/2
            to_wy   -= dest_node.height/2

        return (from_wx, from_wy), (to_wx, to_wy)

    def draw_traversal_line(self, display, node_start_id:int, node_end_id:int, is_cyclic = False):
        line_color  = self.line_colors.l_default if not is_cyclic else self.line_colors.l_cycle
        arrow_color = self.line_colors.arw_default if not is_cyclic else self.line_colors.arw_cycle


        start_node, end_node = self.nodes[node_start_id], self.nodes[node_end_id]
        pos_start, pos_end = self.choose_pivot_points(start_node, end_node)

        if self.holding_node is start_node or self.holding_node is end_node:
            line_color = self.line_colors.highlight

        if self.bends_enabled:
            neg_factor = -1 if is_cyclic else 1
            
            if (node_start_id in self.layering.dummy_traversing_edges and 
                node_end_id in self.layering.dummy_traversing_edges.get(node_start_id)):

                # Draw lines in between dummy vertexes and finally, draw the arrow to the destination vertex.   
                new_pos = (int(pos_start[0]), int(pos_start[1] - neg_factor * start_node.height/2))
                
                for dummy_vertex_out in self.layering.dummy_traversing_edges[node_start_id][node_end_id]:
                    new_pos = (
                        dummy_vertex_out * self.horizontal_step + start_node.width, 
                        new_pos[1] + self.vertical_step * neg_factor
                    )

                    pygame.draw.line( display, line_color, self.world_to_screen(*pos_start), self.world_to_screen(*new_pos), 2)

                    pos_start = new_pos
                
        self.draw_arrow(display, line_color, arrow_color, pos_start, pos_end, 10, 2, 0, not is_cyclic)


    def render_nodes(self, display):
        for node_id in self.nodes:
            node: Button = self.nodes.get(node_id)
            node.render(display, 
                        self.camera.world_offset.x, 
                        self.camera.world_offset.y, 
                        self.camera.zoom_factor)

            # Draw outward lines
            for vtx_out in self.digraph.get_neighbors_out(node_id):

                if (node_id, vtx_out) in self.reversed_edges:
                    if not node_id in self.digraph.get_neighbors_out(vtx_out):
                        continue
                elif (vtx_out, node_id) in self.reversed_edges:
                    continue

                self.draw_traversal_line(
                    display,
                    node_id, vtx_out,
                    False
                )

        for rev_edge in self.reversed_edges:
            if rev_edge[0] in self.digraph.get_neighbors_out(rev_edge[1]):
                self.draw_traversal_line(display, rev_edge[1], rev_edge[0], True)
            else:
                self.draw_traversal_line(display, rev_edge[0], rev_edge[1], True)
    
    def render_warning(self, display: pygame.Surface):
        if not self.show_warning:
            return

        offset_y = (20 + self.warning_image.get_height())

        self.resolver.draw_text(
            display, self.warning_message, colors.YELLOW,
            64, self.camera.VIEW_HEIGHT - offset_y + 4
        )

        display.blit(self.warning_image, (20, self.camera.VIEW_HEIGHT - offset_y))

    def render(self, display):
        display.fill(colors.DARK_GREY)
        self.render_nodes(display)
        self.render_warning(display)

        self.resolver.draw_text(display, "SPACE - enable/disable line bends", colors.WHITE, self.camera.VIEW_WIDTH - 170, self.camera.VIEW_HEIGHT - 32, True)

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