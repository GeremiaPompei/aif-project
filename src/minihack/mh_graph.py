from math import inf
from typing import TypeVar

from nle.nethack import CompassDirection as directions, CompassIntercardinalDirection as inter_directions

from src.data_structure.graph import Graph, Node, Edge
from src.minihack.actions import ACTIONS_DICT

MHNode = TypeVar("MHNode")


class MHNode(Node):
    def __init__(self, id_node: tuple[int, int], content: int):
        super(MHNode, self).__init__(id_node)
        self.x, self.y = id_node
        self.content = content

    def action_move(self, edge: Edge):
        node: MHNode = edge.node_to
        diff_x = node.x - self.x
        diff_y = node.y - self.y
        if diff_x == -1 and diff_y == -1:
            return ACTIONS_DICT[inter_directions.NW]
        if diff_x == -1 and diff_y == 0:
            return ACTIONS_DICT[directions.N]
        if diff_x == -1 and diff_y == 1:
            return ACTIONS_DICT[inter_directions.NE]
        if diff_x == 0 and diff_y == -1:
            return ACTIONS_DICT[directions.W]
        if diff_x == 0 and diff_y == 1:
            return ACTIONS_DICT[directions.E]
        if diff_x == 1 and diff_y == -1:
            return ACTIONS_DICT[inter_directions.SW]
        if diff_x == 1 and diff_y == 0:
            return ACTIONS_DICT[directions.S]
        if diff_x == 1 and diff_y == 1:
            return ACTIONS_DICT[inter_directions.SE]

    def __str__(self):
        return f"MHNode(id_node: {self.id_node}, content: \"{chr(self.content)}\", edges_to: {len(self.edges_to)}" \
               f", edges_from: {len(self.edges_from)})"


def is_valid_edge(n: Node, neighbor: Node, blacklist=["-", "|", "+", " "], obscurity_char=" "):
    blacklist = [ord(v) for v in blacklist]
    return n.content not in blacklist and neighbor.content not in blacklist  # and (
    # n.content != ord(obscurity_char) or neighbor.content != ord(obscurity_char))


class MHGraph(Graph):
    def __init__(self, env, hero_char="@", valid_edge_func=is_valid_edge):
        self.env = env
        x_max, y_max = self.env.shape

        self.nodes: list[MHNode] = []
        self.env.iter(lambda c, coords: self.nodes.append(MHNode(coords, c)))

        def create_edge(n: MHNode, pc, kc):
            px, py = pc
            kx, ky = kc
            kx += px
            ky += py
            neighbor: MHNode = self.nodes[kx * y_max + ky]
            if valid_edge_func(n, neighbor):
                n.add(neighbor)

        for node in self.nodes:
            self.env.iter_neighbors(node.x, node.y, lambda v, pc, kc: create_edge(node, pc, kc))

        hero_chars = list(filter(lambda v: v.content == ord(hero_char), self.nodes))
        root = hero_chars[0] if len(hero_chars) > 0 else None
        super(MHGraph, self).__init__(root)

    def __str__(self):
        return f"MHGraph(root: {self.root})"
