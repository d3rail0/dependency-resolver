import enum
from typing import Tuple, Union
from abc import ABC, abstractmethod
from queue import Queue, LifoQueue

class Graph(ABC):

    def __init__(self) -> None:
        self._name2node = {}
        self._node2name = []
        self._adj_nodes = []

    @abstractmethod
    def add_vertex(self, name: str):
        raise NotImplementedError()

    @abstractmethod
    def add_edge(self, id_u: Union[int, str], id_v: Union[int, str]):
        raise NotImplementedError()

    def get_vertex_id(self, vertex_name: str) -> int:
        """ Returns an index of the specified vertex name.
        If the vertex doesn't exist, -1 is returned.
        """
        return self._name2node.get(vertex_name, -1)
        
    def get_vertex_name(self, vertex:int) -> str:
        return self._node2name[vertex]
    
    def __repr__(self) -> str:
        return self.__str__()

    def __len__(self) -> int:
        return len(self._node2name)

    def __getitem__(self, vertex: int) -> list[int]:
        return self._adj_nodes[vertex]
    
    def safe_add_vertex(self, name: str) -> int:
        """ Adds new vertex to the graph only
        if it doesn't exist already.
        Returns index of the new (or existing) vertex.
        """
        v_id = self.get_vertex_id(name)
        if v_id == -1:
            return self.add_vertex(name)
        return v_id

    def _base_add_vertex(self, name: str) -> int:
        """ Adds new vertex to the graph
        and returns its index.
        """
        if name in self._name2node:
            raise RuntimeError(f"Vertex {name} already exists")

        self._name2node[name] = len(self)
        self._node2name.append(name)
        
        return self._name2node.get(name)

class GraphMatrix(Graph):

    def __init__(self, capacity) -> None:
        super().__init__()

        for _ in range(capacity):
            self._adj_nodes.append([0]*capacity)

        self.__capacity = capacity

    def get_capacity(self) -> int:
        return self.__capacity

    def get_matrix_str(self) -> str:
        return str(self._adj_nodes)

    def __str__(self) -> str:
        return ("{\n" +
           "\n".join(
               [f'"{name}" | {node_id}' + ": [" + ",".join(
                   [str(vrtx) for vrtx in self.get_neighbors_out(node_id)]
                   ) + "]" for name,node_id in self._name2node.items()]
               )
           + 
        "\n}")
    
    def get_neighbors_out(self, vertex:int) -> list[int]:
        return [vrtx for vrtx, is_neighbour in enumerate(self[vertex]) if is_neighbour!=0]

    def get_neighbors_in(self, vertex:int) -> list[int]:
        return [
            vrtx 
            for vrtx in range(0, len(self)) 
            if self[vrtx][vertex] != 0
        ]

    def add_vertex(self, name: str) -> int:

        if len(self) >= self.get_capacity():
            raise MemoryError("Not enough capacity to store another vertex")

        super()._base_add_vertex(name)

        return self._name2node.get(name)

    def _final_add_edge(self, u:int, v:int):
        self._adj_nodes[u][v] = 1

    def reverse_edge(self, u:int, v:int) -> None:
        self[u][v], self[v][u] = self[v][u], self[u][v]

class GraphAdjList(Graph):

    def __init__(self) -> None:
        super().__init__()
        self._adj_nodes:list[list[int]] = []

    def __str__(self) -> str:
        return ("{\n" +
            "\n".join(
                [f'"{name}"' + ": [" + ",".join(
                    [str(edge) for edge in self._adj_nodes[node_id]]
                    ) + "]" for name,node_id in self._name2node.items()]
                )
            + 
        "\n}")

    def add_vertex(self, name: str) -> int:
        super()._base_add_vertex(name)
        self._adj_nodes.append([])
        return self._name2node.get(name)

    def _final_add_edge(self, u:int, v:int):
        self._adj_nodes[u].append(v)

    def reverse_edge(self, u:int, v:int) -> None:
        if not u in self._adj_nodes[v]:
            self._adj_nodes[v].append(u)
            self._adj_nodes[u].remove(v)
        else:
            self._adj_nodes[u].append(v)
            self._adj_nodes[v].remove(u)

    def get_neighbors_out(self, vertex:int) -> list[int]:
        return self._adj_nodes[vertex]

    def get_neighbors_in(self, vertex:int) -> list[int]:
        return [
            vrtx 
            for vrtx in range(0, len(self)) 
            if vertex in self[vrtx]
        ]

class DirectedGraph(GraphAdjList):

    @property
    def reversed_edges(self):
        return self.__reversed_edges

    def __init__(self) -> None:
        super().__init__()
        self.__reversed_edges: list[Tuple[int, int]] = []        
    
    def undo_reversed_edges(self) -> None:
        """ Fix graph state by returning reversed edges
        back to their exact initial state. The only edges
        that it affects are those caused by calling 
        remove_cycle_and_sort() method.
        """
        while len(self.__reversed_edges):
            self.reverse_edge(*self.__reversed_edges.pop())

    def add_edge(self, id_u: Union[int, str], id_v: Union[int, str]) -> None:        
        u = self._name2node.get(id_u) if type(id_u) is str else id_u
        v = self._name2node.get(id_v) if type(id_v) is str else id_v
        self._final_add_edge(u, v)

    def remove_cycle_and_sort(self) -> list[int]:
        """ Removes a cycle (if present) from a graph, then creates a topological order 
        for the acyclic graph. Calling this method can alter graph in presence of cycles
        by reversing a couple of edges.
        All state changes will be saved into "reversed_edges" list. Graph can return to its
        initial state by calling undo_reversed_edges() method.
        Returns: topological order of the (non-)altered graph.
        """

        if len(self) == 0:
            return []

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
        
        if source_vts.qsize()==0:
            # no source vertices were found, hence
            # the graph is a complete cycle (ring)
            return []
        
        topological_order = []

        try:

            while source_vts.qsize() or temp_vts.qsize():
                
                while source_vts.qsize():

                    source_vertex = source_vts.get()

                    if not is_done[source_vertex]:
                        topological_order.append(source_vertex)
                    
                    is_done[source_vertex] = True

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
                                self.__reversed_edges.append((vx_out, temp_vtx))
                                indeg[vx_out] += 1
                        
                        source_vts.put(temp_vtx)

        except Exception as ex:
            self.undo_reversed_edges()
            raise ex

        return topological_order