from typing import TypeVar

from nle import nethack

from src.data_structure.graph import Graph, Node, Edge
from src.minihack.actions import ACTIONS_DICT

MHNode = TypeVar("MHNode")
MHEdge = TypeVar("MHEdge")


class MHEdge(Edge):
    def __init__(self, node: MHNode, value: int = 0):
        super(MHNode, self).__init__(node, value)


class MHNode(Node):
    def __init__(self, value: int, coords: tuple[int, int]):
        super(MHNode, self).__init__(value)
        self.x, self.y = coords

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def action_move(self, edge: MHEdge):
        node: MHNode = edge.node
        diff_x = node.x - self.x
        diff_y = node.y - self.y
        if diff_x == -1 and diff_y == -1:
            return ACTIONS_DICT[nethack.CompassIntercardinalDirection.NW]
        if diff_x == -1 and diff_y == 0:
            return ACTIONS_DICT[nethack.CompassCardinalDirection.N]
        if diff_x == -1 and diff_y == 1:
            return ACTIONS_DICT[nethack.CompassIntercardinalDirection.NE]
        if diff_x == -1 and diff_y == 0:
            return ACTIONS_DICT[nethack.CompassCardinalDirection.W]
        if diff_x == -1 and diff_y == 0:
            return ACTIONS_DICT[nethack.CompassCardinalDirection.E]
        if diff_x == 1 and diff_y == -1:
            return ACTIONS_DICT[nethack.CompassIntercardinalDirection.SW]
        if diff_x == 1 and diff_y == 0:
            return ACTIONS_DICT[nethack.CompassCardinalDirection.S]
        if diff_x == 1 and diff_y == 1:
            return ACTIONS_DICT[nethack.CompassIntercardinalDirection.SE]


class MHGraph(Graph):
    def __init__(self, env):
        self.env = env
        x_max, y_max = self.env.shape
        blacklist = [ord(v) for v in ["-", "|", "+"]]
        frontier = []

        nodes: list[MHNode] = []
        self.env.iter(lambda c, coords: nodes.append(MHNode(c, coords)))

        def create_edge(node: MHNode, pcoords, kcoords):
            px, py = pcoords
            kx, ky = kcoords
            kx += px
            ky += py
            neighbor: MHNode = nodes[kx * y_max + ky]
            if node.value not in blacklist and neighbor.value not in blacklist and (
                    node.value != ord(" ") and node.value != ord(" ")):
                node.add(neighbor)

        for node in nodes:
            self.env.iter_neighbors(node.x, node.y, lambda v, pcoords, kcoords: create_edge(node, pcoords, kcoords))

        root = list(filter(lambda v: v.value == ord("@"), nodes))[0]

        super(MHGraph, self).__init__(root)
