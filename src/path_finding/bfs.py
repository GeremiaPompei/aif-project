from src.data_structure.graph import EOS
from src.minihack.env import Env
from src.minihack.mh_graph import MHNode


class BFS:

    def __init__(self, env: Env):
        self.env = env

    def run(self, times: int = 1):
        for _ in range(times):
            self.env.reset()
            curr = self.env.graph.root
            self.env.render()
            while not self.end_match():
                self.clear_weights()
                self.set_edges_weight()
                curr.edges.sort(key=lambda e: e.value)
                edge = curr.edges[0]
                if edge.value == 0:
                    break
                step = curr.action_move(edge)
                self.env.step(step)
            self.env.render()

    def end_match(self):

        def f(node: MHNode):
            flag = node.value == ord(" ")
            return [True, EOS] if flag else None

        flag = self.env.graph.bfs(f)
        return not flag

    def clear_weights(self):
        nodes = []

        def f(node: MHNode):
            nodes.append(node)
            for edge in node.edges:
                edge.value = 0

        self.env.graph.bfs(f)

    def set_edges_weight(self):
        nodes = []

        def f(node: MHNode):
            if node.value == ord(" "):
                nodes.append(node)  # TODO fix

        self.env.graph.bfs(f)

        for node in nodes:
            for edge in node.edges:
                if node.value != ord(" ") and edge.value > 0:
                    edge.value += 1
                    nodes.append(edge.node)
