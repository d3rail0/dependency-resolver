import pygame
from src.states.state import *
from src.utils import util
import src.ui.colors as colors
from src.scanner import DependencyScanner
from src.ds.graph import DirectedGraph
from src.node_layering import *
from src.states.world import World

import os
from global_logger import Log
import threading

from enum import Enum

class ScanStage(Enum):

    DIRECTORY_SCAN  = 0
    CONSTRUCT_GRAPH = 1
    ALL_COMPLETED   = 2

class Scan(State):

    glob_log = Log.get_logger(name="ScanState", logs_dir=os.path.abspath("./log"))

    progress_lock = threading.Lock()

    def __init__(self, resolver, project_directory:str):
        super().__init__(resolver)

        if not project_directory or not os.path.exists(project_directory):
            raise Exception("Project directory was not set!")

        self.stage: ScanStage = ScanStage.DIRECTORY_SCAN

        self.dependencies: dict[str, list[str]] = {}
        self.digraph = DirectedGraph()

        self.scanner            = DependencyScanner(self.scan_progress_callback)
        self.target_project_dir = DependencyScanner.normalize_path(project_directory)

        self.top_text    = ""
        self.bottom_text = ""
        self.text_color  = colors.WHITE

        self.scan_progress_callback(0,0,"")

        self.th_scanner = util.ThreadWithRetVal(target=self.scanner.scan_dir, args=(self.target_project_dir,), daemon=True)
        self.th_scanner.start()
        
    def update_status(self, top_text:str, bottom_text:str, color:pygame.Color = colors.WHITE) -> None:
        with self.progress_lock:
            self.top_text = top_text
            self.bottom_text = bottom_text
            self.text_color = color

    def scan_progress_callback(self, curr_index: int, total_files: int, curr_file: str) -> None:
        self.update_status(f"File: {curr_index} / {total_files}", curr_file)

    def __prepare_and_sort_dag(self) -> None:

        self.update_status("GRAPH", "Converting dependencies into a graph structure...", colors.YELLOW)

        # Vertex represents an included file
        # Edge (u,v) means u was included by v.
        # u needs to be compiled first

        for source_file in self.dependencies:
            self.digraph.safe_add_vertex(source_file)
            for included_file in self.dependencies[source_file]:
                self.digraph.safe_add_vertex(included_file)

                # prevent files with improper includes or "self includes"
                if not included_file == source_file:
                    self.digraph.add_edge(included_file, source_file)

        self.update_status("GRAPH", "Removing cycles and applying toposort...", colors.YELLOW)

        # Get topological order for graph and prepare it for layering
        top_order =  self.digraph.remove_cycle_and_sort()

        self.update_status("GRAPH", "Finding longest path layering...", colors.MAGENTA)

        layering = Layering(self.digraph, top_order)
        layering.compute_layers()
        return layering

    def update(self, delta_time, actions):

        # Check if scanner thread has finished 
        # so that we can proceed onto the final state
        if self.th_scanner and not self.th_scanner.is_alive():

            if self.stage == ScanStage.DIRECTORY_SCAN:

                self.dependencies = self.th_scanner.join()

                # Start thread for converting the dependencies to a graph structure and applying layering algorithm
                self.th_scanner = util.ThreadWithRetVal(target=self.__prepare_and_sort_dag, args=(), daemon=True)
                self.th_scanner.start()

                self.stage = ScanStage.CONSTRUCT_GRAPH

            elif self.stage == ScanStage.CONSTRUCT_GRAPH:
                
                layering = self.th_scanner.join()

                self.th_scanner = None
                
                world_state = World(self.target_project_dir, self.resolver, self.digraph, layering)
                self.exit_state()
                world_state.enter_state()

                self.stage = ScanStage.ALL_COMPLETED
                
        self.resolver.reset_keys()

    def render(self, display):
        display.fill(colors.DARK_GREY)

        with self.progress_lock:
            self.resolver.draw_text(display, self.top_text, 
            self.text_color, self.resolver.VIEW_W/2, self.resolver.VIEW_H/2 - self.resolver.font.get_height(), True)

            self.resolver.draw_text(display, self.bottom_text, 
            self.text_color, self.resolver.VIEW_W/2, self.resolver.VIEW_H/2 + self.resolver.font.get_height(), True )