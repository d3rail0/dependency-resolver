from src.ds.graph import *

class Node: 

    def __init__(self, node_id, is_dummy:bool = False) -> None:
        self.node_id = node_id
        self.is_dummy = is_dummy

class Layer:

    def __init__(self, layer_level) -> None:
        self.__layer_level = layer_level
        self.__nodes: list[Node] = []

    def add_node(self, node_id):
        self.__nodes.append(
            Node(node_id, False)
        )
    

class Layering:

    @property
    def layers(self) -> list[int]:
        """Returns: List of layer levels where item at index i represents
        a layer level of a vertex i. 
        """
        return self.__layers

    def __init__(self, graph: DirectedGraph, topological_order: list[int]) -> None:
          
        self.graph = graph
        self.topological_order = topological_order
        self.__layers: list[int] = []

    def compute_layers(self):
        """ Computes min-height layers for vertices sorted in topological order
        and.
        """
        self.__layers = [1]*(len(self.graph)+1)

        for node in self.topological_order:

            for node_out in self.graph.get_neighbors_out(node):

                min_length = 1

                self.__layers[node_out] = max(
                    self.__layers[node_out],
                    self.__layers[node] + min_length
                ) 
        

    def proper_layering(graph: DirectedGraph, layerings: list[int]) -> list[int]:
        pass