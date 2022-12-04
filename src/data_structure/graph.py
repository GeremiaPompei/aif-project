from typing import TypeVar, Callable

NodeValue = TypeVar("NodeValue")
EdgeValue = TypeVar("EdgeValue")
Edge = TypeVar("Edge")
Node = TypeVar("Node")

EOS = "EOS"


class Edge:

    def __init__(self, node: Node, value: EdgeValue = None):
        self.value = value
        self.node = node


class Node:

    def __init__(self, value: NodeValue):
        self.value = value
        self.edges: list[Edge] = []

    def add(self, neighbor: Node, edge_value: EdgeValue = None):
        self.edges.append(Edge(neighbor, edge_value))

    def remove(self, neighbor: NodeValue):
        self.edges = filter(lambda e: e.node != neighbor, self.edges)

    def dfs(self, stored: list[Node], callback: Callable):
        for edge in self.edges:
            node = edge.node
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
        for edge in self.edges:
            node = edge.node
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
