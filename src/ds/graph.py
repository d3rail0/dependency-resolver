import enum
from typing import Union
from abc import ABC, abstractmethod
from queue import Queue, LifoQueue

class Graph(ABC):

    def __init__(self, capacity) -> None:
        self._name2node = {}
        self._node2name = []
        self._adj_matrix = []

        for _ in range(capacity):
            self._adj_matrix.append([0]*capacity)

        self.__capacity = capacity

    @abstractmethod
    def add_vertex(self, name: str):
        raise NotImplementedError()

    @abstractmethod
    def add_edge(self, id_u: Union[int, str], id_v: Union[int, str]):
        raise NotImplementedError()

    def get_vertex_name(self, vertex:int) -> str:
        return self._node2name[vertex]

    def get_capacity(self) -> int:
        return self.__capacity

    def get_matrix_str(self) -> str:
        return str(self._adj_matrix)

    def __str__(self) -> str:
        return ("{\n" +
           "\n".join(
               [f'"{name}"' + ": [" + ",".join(
                   [str(vrtx) for vrtx in self.get_neighbors_out(node_id)]
                   ) + "]" for name,node_id in self._name2node.items()]
               )
           + 
        "\n}")

    def __repr__(self) -> str:
        return self.__str__()

    def __len__(self) -> int:
        return len(self._node2name)
    
    def __getitem__(self, vertex: int) -> list[int]:
        return self._adj_matrix[vertex]

    def get_neighbors_out(self, vertex:int) -> list[int]:
        return [vrtx for vrtx, is_neighbour in enumerate(self[vertex]) if is_neighbour!=0]

    def get_neighbors_in(self, vertex:int) -> list[int]:
        return [
            vrtx 
            for vrtx in range(0, len(self)) 
            if self[vrtx][vertex] != 0
        ]

class DirectedGraph(Graph):

    def __init__(self, capacity:int) -> None:
        super().__init__(capacity)        
    
    def add_vertex(self, name: str) -> int:
        """ Adds new vertex to the graph
        and returns its index.
        """
        if name in self._name2node:
            raise RuntimeError(f"Vertex {name} already exists")

        if len(self) >= self.get_capacity():
            raise MemoryError("Not enough capacity to store another vertex")

        self._name2node[name] = len(self)
        self._node2name.append(name)
        
        return self._name2node.get(name)

    def add_edge(self, id_u: Union[int, str], id_v: Union[int, str]) -> None:        
        u = self._name2node.get(id_u) if type(id_u) is str else id_u
        v = self._name2node.get(id_v) if type(id_v) is str else id_v
        self[u][v] = 1

    def reverse_edge(self, u:int, v:int) -> None:
        self[u][v], self[v][u] = self[v][u], self[u][v]

    def remove_cycle_and_sort(self):
        """ Removes a cycle (if present) from a graph, creates a topological order 
        for the acyclic graph.
        Returns: 2-tuple of topological order and all edges reversed for cycle removal
        """
        rev_edges  = LifoQueue(maxsize=len(self))

        if len(self) == 0:
            return [], rev_edges

        source_vts = Queue(maxsize=len(self))
        temp_vts   = Queue(maxsize=len(self))
        is_done    = [False] * len(self)
        indeg      = [0]     * len(self)
        outdeg     = [0]     * len(self)
        V          = range(len(self))

        for vtx_id in V:
            for vx_out in self.get_neighbors_out(vtx_id):
                indeg[vx_out] += 1
                outdeg[vtx_id]  += 1
        
        for vtx_id in V:
            if indeg[vtx_id] == 0:
                source_vts.put(vtx_id)

        topological_order = []
        
        if source_vts.qsize()==0:
            # no source vertices were found, hence
            # the graph is a complete cycle (ring)
            return [], rev_edges

        try:

            while source_vts.qsize() or temp_vts.qsize():
                
                while source_vts.qsize():

                    source_vertex          = source_vts.get()
                    is_done[source_vertex] = True

                    topological_order.append(source_vertex)

                    for vx_out in self.get_neighbors_out(source_vertex):
                        indeg[vx_out] -= 1
                        if indeg[vx_out] == 0:
                            source_vts.put(vx_out)                        
                        else:
                            temp_vts.put(vx_out)
                
                if temp_vts.qsize():
                    temp_vtx=-1
                    while temp_vts.qsize():
                        temp_vtx = temp_vts.get()
                        if not is_done[temp_vtx] and outdeg[temp_vtx]>0:
                            break
                    
                    if not is_done[temp_vtx] and outdeg[temp_vtx]>0:

                        for vx_out in self.get_neighbors_in(temp_vtx):
                            if not is_done[vx_out]:
                                self.reverse_edge(vx_out,temp_vtx)
                                rev_edges.put((vx_out, temp_vtx))
                                indeg[vx_out] += 1
                        
                        source_vts.put(temp_vtx)

        except Exception as ex:
            # Fix graph state first by reverse all edges
            # back to their initial state
            while rev_edges.qsize():
                self.reverse_edge(*rev_edges.get())

            raise ex

        return topological_order, rev_edges