from time import sleep

from src.data_structure.graph import EOS
from src.minihack.env import Env
from src.minihack.mh_graph import MHNode


class AStar:

    def __init__(self, env: Env):
        self.env = env

    def run(self, targets: list[str], times: int = 1, verbose: bool = True):
        targets = [ord(trg) for trg in targets]
        for _ in range(times):
            self.env.reset()
            while self.end_match(targets):
                self.env.reset()
                self.env.refresh_graph()
            curr = self.env.graph.root
            visited_edges = []

            while not self.env.done and not self.end_match(targets):
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
                    sleep(0.5)
                    self.env.render()

    def end_match(self, trgs: list[int]):
        return not self.env.graph.bfs(lambda n: [True, EOS] if n.content in trgs else None)

    def set_edges_weight(self, trgs: list[int]):
        nodes = []

        def f(n: MHNode):
            if n.content in trgs:
                nodes.append(n)

        self.env.graph.bfs(f)
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
