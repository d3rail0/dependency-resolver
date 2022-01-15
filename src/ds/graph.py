from typing import Union
from abc import ABC, abstractmethod

class Graph(ABC):

    def __init__(self) -> None:
        self._name2node = {}
        self._node2name = []
        self._adj_list: list[list[int]] = []

    @abstractmethod
    def add_vertex(self, name: str):
        raise NotImplementedError()

    @abstractmethod
    def add_edge(self, id_u: Union[int, str], id_v: Union[int, str]):
        raise NotImplementedError()

    def __str__(self) -> str:
        return ("{\n" +
           "\n".join(
               [f'"{name}"' + ": [" + ",".join(
                   [str(edge) for edge in self._adj_list[node_id]]
                   ) + "]" for name,node_id in self._name2node.items()]
               )
           + 
        "\n}")

    def __repr__(self) -> str:
        return self.__str__()

    def __len__(self) -> int:
        return len(self._node2name)
    
    def __getitem__(self, vertex: int) -> list[int]:
        return self._adj_list[vertex]

class DirectedGraph(Graph):

    def __init__(self) -> None:
        super().__init__()        
    
    def add_vertex(self, name: str) -> int:
        """ Adds new vertex to the graph
        and returns its index.
        """
        if name in self._name2node:
            raise RuntimeError(f"Vertex {name} already exists")

        self._name2node[name] = len(self._node2name)
        self._node2name.append(name)
        self._adj_list.append([])

        return self._name2node.get(name)

    def add_edge(self, id_u: Union[int, str], id_v: Union[int, str]) -> None:
        u = self._name2node.get(id_u) if type(id_u) is str else id_u
        v = self._name2node.get(id_v) if type(id_v) is str else id_v
        self._adj_list[u].append(v)
