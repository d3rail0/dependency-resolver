from typing import Union
from abc import ABC, abstractmethod

class Graph(ABC):

    def __init__(self, size) -> None:
        self._name2node = {}
        self._node2name = []
        self._adj_matrix = []

        for _ in range(size):
            self._adj_matrix.append([0]*size)

        self.__size = size

    @abstractmethod
    def add_vertex(self, name: str):
        raise NotImplementedError()

    @abstractmethod
    def add_edge(self, id_u: Union[int, str], id_v: Union[int, str]):
        raise NotImplementedError()

    def get_vertex_name(self, vertex:int) -> str:
        return self._node2name[vertex]

    def __str__(self) -> str:
        return ("{\n" +
           "\n".join(
               [f'"{name}"' + ": [" + ",".join(
                   [str(vrtx) for vrtx,is_neighbour in enumerate(self._adj_matrix[node_id]) if is_neighbour!=0]
                   ) + "]" for name,node_id in self._name2node.items()]
               )
           + 
        "\n}")

    def __repr__(self) -> str:
        return self.__str__()

    def __len__(self) -> int:
        return self.__size
    
    def __getitem__(self, vertex: int) -> list[int]:
        return self._adj_matrix[vertex]

class DirectedGraph(Graph):

    def __init__(self, size:int) -> None:
        super().__init__(size)        
    
    def add_vertex(self, name: str) -> int:
        """ Adds new vertex to the graph
        and returns its index.
        """
        if name in self._name2node:
            raise RuntimeError(f"Vertex {name} already exists")

        self._name2node[name] = len(self._node2name)
        self._node2name.append(name)
        
        return self._name2node.get(name)

    def add_edge(self, id_u: Union[int, str], id_v: Union[int, str]) -> None:
        u = self._name2node.get(id_u) if type(id_u) is str else id_u
        v = self._name2node.get(id_v) if type(id_v) is str else id_v
        self[u][v] = 1
