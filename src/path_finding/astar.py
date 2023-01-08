from typing import Callable

from nle import nethack

from src.data_structure.graph import EOS, Node, Edge
from src.minihack.actions import ACTIONS_DICT
from src.minihack.env import Env
from src.minihack.mh_graph import MHNode, MHGraph
from src.minihack.symbol import Symbols


class AStar:

    def __init__(self, env: Env, valid_edge_func: Callable):
        self.env = env
        self.valid_edge_func = valid_edge_func
        self.graph = MHGraph(self.env, self.valid_edge_func)

    def refresh_graph(self, invalid_nodes=[]):
        self.graph = MHGraph(self.env, self.valid_edge_func, invalid_nodes=invalid_nodes)

    def find(self, targets_pos, already_visited_pos: list[Node] = [], visited_edges: dict[Edge, int] = {}, invalid_nodes: list[Node] = [], verbose: bool = True):
        curr = self.graph.root
        previous_pos = (curr.x, curr.y)
        while not self.end_match(targets_pos):
            self.set_edges_weight(targets_pos)
            edges = [e for e in curr.edges_to if e.weight is not None]
            if len(edges) == 0:
                break
            for edge in edges:
                if edge in visited_edges:
                    edge.weight += visited_edges[edge]
            edges.sort(key=lambda e: e.weight)
            edge = edges[0]
            step = curr.action_move(edge)
            if step is None:
                break
            if edge.node_to.content in Symbols.DOOR_CLOSE_CHARS:
                self.env.step(ACTIONS_DICT[nethack.Command.APPLY])
            self.env.over_hero_symbol = edge.node_to.content
            self.env.step(step)
            already_visited_pos.append((curr.x, curr.y))
            inv_edge = Edge(edge.node_from, edge.node_to, edge.weight)
            if inv_edge in visited_edges:
                visited_edges[inv_edge] += 1
            else:
                visited_edges[inv_edge] = 1
            self.refresh_graph(invalid_nodes=invalid_nodes)
            if edge.node_to.content not in Symbols.DOOR_CLOSE_CHARS and previous_pos[0] == curr.x and \
                    previous_pos[1] == curr.y and edge.node_to.content == Symbols.OBSCURE_CHAR:
                invalid_nodes.append(edge.node_to)
            previous_pos = (curr.x, curr.y)
            curr = self.graph.root

            if verbose:
                self.env.render()
            break

    def end_match(self, targets_pos: list[tuple[int, int]]):
        def func(n):
            if (n.x, n.y) in targets_pos and n.content != Symbols.HERO_CHAR:
                return [True, EOS]
            else:
                return None

        return not self.graph.bfs(func)

    def set_edges_weight(self, targets_pos: list[tuple[int, int]]):
        nodes = []

        def f(n: MHNode):
            if (n.x, n.y) in targets_pos:
                nodes.append(n)

        self.graph.bfs(f)
        old_nodes = nodes.copy()
        new_nodes = []
        weight = 0
        while len(old_nodes) > 0:
            for node in old_nodes:
                for edge in node.edges_from:
                    edge.weight = weight
                    if edge.node_from not in nodes:
                        nodes.append(edge.node_from)
                        new_nodes.append(edge.node_from)
            old_nodes = new_nodes
            new_nodes = []
            weight += 1
