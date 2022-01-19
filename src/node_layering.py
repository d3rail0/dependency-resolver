from src.ds.graph import *

def longest_path_layering(graph: DirectedGraph, topological_order: list[int]) -> list[int]:
    """ Computes min-height layers for vertices sorted in topological order
    and.
    Returns: List of layer levels where item at index i represents
    a layer level of a vertex i. 
    """

    layers = [1]*len(topological_order)

    for node in topological_order:

        for node_out in graph.get_neighbors_out(node):

            min_length = 1

            layers[node_out] = max(
                layers[node_out],
                layers[node] + min_length
            ) 

    return layers