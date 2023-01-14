from typing import TypeVar, Callable

NodeId = TypeVar("NodeId")
Edge = TypeVar("Edge")
Node = TypeVar("Node")

EOS = "EOS"


class Edge:

    def __init__(self, node_from: Node, node_to: Node, weight: float = 0):
        self.weight = weight
        self.node_from = node_from
        self.node_to = node_to

    def __str__(self):
        return f"MHEdge(weight: {self.weight}, node_from: {self.node_from}, node_to: {self.node_to})"

    def __hash__(self) -> int:
        return hash((self.node_from, self.node_to))

    def __eq__(self, o: object) -> bool:
        return self.__hash__() == o.__hash__()


class Node:

    def __init__(self, id_node: NodeId, weight: float = 0):
        self.id_node = id_node
        self.weight = weight
        self.edges_from: list[Edge] = []
        self.edges_to: list[Edge] = []

    def add(self, node_to: Node, weight: float = 0):
        edge = Edge(self, node_to, weight)
        self.edges_to.append(edge)
        node_to.edges_from.append(edge)

    def remove(self, edge: Edge):
        new_edges = []
        for e in self.edges_to:
            if e != edge:
                new_edges.append(e)
            else:
                e.node_from.remove_from()
        self.edges_to = new_edges

    def remove_from(self, edge: Edge):
        new_edges = []
        for e in self.edges_from:
            if e != edge:
                new_edges.append(e)
            else:
                e.node_to.remove_to()
        self.edges_from = new_edges

    def dfs(self, stored: list[Node], callback: Callable):
        for edge in self.edges_to:
            node = edge.node_to
            if node in stored:
                continue
            else:
                stored.append(node)
            rn = node.dfs(stored, callback)
            if rn is not None and rn[-1] == EOS:
                return rn
            rc = callback(node)
            if rc is not None and rc[-1] == EOS:
                return rc

    def bfs(self, stored: list[Node], callback: Callable):
        for edge in self.edges_to:
            node = edge.node_to
            if node in stored:
                continue
            else:
                stored.append(node)
            rc = callback(node)
            if rc is not None and rc[-1] == EOS:
                return rc
            rn = node.bfs(stored, callback)
            if rn is not None and rn[-1] == EOS:
                return rn

    def __hash__(self) -> int:
        return hash(self.id_node)

    def __eq__(self, o: object) -> bool:
        return self.__hash__() == o.__hash__()

    def __str__(self):
        return f"MHNode(coords: id_node: {self.id_node}, edges_to: {self.edges_to}, edges_from: {self.edges_from})"


class Graph:

    def __init__(self, root: Node):
        self.root = root

    def dfs(self, callback: Callable):
        stored = []
        res = self.root.dfs(stored, callback)
        if res is not None:
            return res[0]

    def bfs(self, callback: Callable):
        stored = []
        res = self.root.bfs(stored, callback)
        if res is not None:
            return res[0]

    def __str__(self):
        return f"MHGraph(root: {self.root})"
