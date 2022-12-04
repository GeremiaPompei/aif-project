from time import sleep
from typing import Callable

from src.data_structure.graph import EOS
from src.minihack.env import Env
from src.minihack.mh_graph import MHNode


class GraphSearch:

    def __init__(self, env: Env, search_func: Callable):
        self.env = env
        self.search_func = search_func

    def run(self, targets: list[str], times: int = 1, verbose: bool = False):
        targets = [ord(trg) for trg in targets]
        for _ in range(times):
            self.env.reset()
            self.env.render()
            self.env.refresh_graph()
            curr = self.env.graph.root
            visited_edges = []

            while not self.env.done and not self.end_match(targets):
                self.clear_weights()
                self.set_edges_weight(targets)
                edges = [e for e in curr.edges_to if e.weight is not None and e not in visited_edges]
                if len(edges) == 0:
                    break
                edges.sort(key=lambda e: e.weight)
                edge = edges[0]
                step = curr.action_move(edge)
                if step is None:
                    break
                self.env.step(step)
                visited_edges.append(edge)
                self.env.refresh_graph()
                curr = self.env.graph.root

                if verbose:
                    sleep(1)
                    self.env.render()

            self.env.render()

    def end_match(self, trgs: list[int]):
        return not self.search_func(self.env.graph)(lambda n: [True, EOS] if n.content in trgs else None)

    def clear_weights(self):
        nodes = []

        def f(node: MHNode):
            nodes.append(node)
            for edge in node.edges_from:
                edge.weight = 0

        self.search_func(self.env.graph)(f)

    def set_edges_weight(self, trgs: list[int]):
        nodes = []

        def f(n: MHNode):
            if n.content in trgs:
                nodes.append(n)

        self.search_func(self.env.graph)(f)
        old_nodes = nodes.copy()
        new_nodes = nodes.copy()
        weight = 0
        while len(old_nodes) > 0:
            weight += 1
            for node in old_nodes:
                for edge in node.edges_from:
                    edge.weight = weight
                    if edge.node_from not in nodes:
                        nodes.append(edge.node_from)
                        new_nodes.append(edge.node_from)

            old_nodes = new_nodes
            new_nodes = []


class DFS(GraphSearch):
    def __init__(self, env: Env):
        super().__init__(env, lambda g: g.dfs)


class BFS(GraphSearch):
    def __init__(self, env: Env):
        super().__init__(env, lambda g: g.bfs)
