from src.ds.graph import *

class Node: 

    def __init__(self, node_id, is_dummy:bool = False) -> None:
        self.node_id = node_id
        self.is_dummy = is_dummy

class Layer:

    def __init__(self, layer_level) -> None:
        self.level = layer_level
        self.nodes: list[Node] = []        

class Layering:

    @property
    def raw_node_layers(self) -> list[int]:
        return self.__node2layer

    @property
    def layers(self) -> list[Layer]:
        """Returns: List of layer levels where item at index i represents
        a layer level of a vertex i. 
        """
        return self.__layers

    def __init__(self, graph: DirectedGraph, topological_order: list[int]) -> None:
          
        self.graph                   = graph
        self.topological_order       = topological_order
        self.__layers: list[Layer]   = []
        self.__node2layer: list[int] = []
        
        # vtx_id -> child_vtx -> single layer dummy vertex edges
        self.dummy_traversing_edges: dict[int, dict[list[int]]] = {}


    def compute_layers(self):
        """ Computes min-height layers for vertices sorted in topological order
        and.
        """
        self.__node2layer = [1]*(len(self.graph))

        for node in self.topological_order:

            for node_out in self.graph.get_neighbors_out(node):

                self.__node2layer[node_out] = max(
                    self.__node2layer[node_out],
                    self.__node2layer[node] + 1
                ) 
        
        # Convert raw node 2 layer list to list of Layer instances.
        highest_layer = max(self.__node2layer)
        for layer in range(1, highest_layer+1):
            self.__layers.append(
                Layer(layer)
            )

        for node_id, layer in enumerate(self.__node2layer):
            self.__layers[layer-1].nodes.append(node_id)

    def proper_layering(self):
        for current_layer in self.__layers:
            for vtx in current_layer.nodes:
                for child_vtx in self.graph.get_neighbors_out(vtx):
                    target_level = self.__node2layer[child_vtx]
                    if abs(target_level - current_layer.level) > 1:
                        if not vtx in self.dummy_traversing_edges:
                            self.dummy_traversing_edges[vtx] = {}

                        if not child_vtx in self.dummy_traversing_edges[vtx]:
                            self.dummy_traversing_edges[vtx][child_vtx] = []

                        for layer in range(
                            min(target_level, current_layer.level)+1,
                            max(target_level, current_layer.level)
                        ):

                            self.dummy_traversing_edges[vtx][child_vtx].append(len(self.__layers[layer-1].nodes))
                            self.__layers[layer-1].nodes.append(-1)
                        
        

    def layers_to_str(self) -> str:
        resp = ""
        for layer in self.__layers:
            resp += str(layer.level) + " => " + str(layer.nodes) + "\n"
        return resp