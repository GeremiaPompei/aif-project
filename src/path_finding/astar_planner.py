from src.data_structure.graph import Node
from src.minihack.env import Env
from src.minihack.symbol import Symbols
from src.path_finding.astar import AStar


def is_valid_edge(node_from: Node, node_to: Node, blacklist=Symbols.WALL_CHARS,
                  obscurity_char=Symbols.OBSCURE_CHAR):
    return node_from.content not in blacklist and node_to.content not in blacklist and (
            (
                    node_to.content == Symbols.FLOOR_CHAR and node_from.content == obscurity_char
            ) or (
                    node_from.content == Symbols.FLOOR_CHAR and node_to.content == obscurity_char
            ) or (
                    node_from.content != obscurity_char and node_to.content != obscurity_char
            )
    )


class AStarPlanner:

    def __init__(self, env: Env):
        self.env = env
        self.algorithm = AStar(env, is_valid_edge)

    def get_target(self, already_visited_pos):
        targets_list = [Symbols.CORRIDOR_CHARS, [Symbols.STAIR_UP_CHAR], [Symbols.KEY_CHAR], Symbols.DOOR_OPEN_CHARS, Symbols.DOOR_CLOSE_CHARS,
                        [Symbols.OBSCURE_CHAR]]
        for targets in targets_list:
            if targets[0] in Symbols.CORRIDOR_CHARS:
                # TODO if we are in corridor and e neighbor is not corridor, walkable and not already visited this is
                #  the target
                corridor_not_visited = [pos for pos in self.env.find_all_chars_pos(Symbols.CORRIDOR_CHARS) if
                                        pos not in already_visited_pos]
                if len(corridor_not_visited) == 0:
                    continue
                else:
                    return corridor_not_visited
            else:
                poss = [p for p in self.env.find_all_chars_pos(targets) if p not in already_visited_pos]
                if len(poss) > 0:
                    return poss
        return None

    def run(self, times: int = 1, verbose: bool = True):
        for _ in range(times):
            self.env.reset()
            self.algorithm.refresh_graph()
            already_visited_pos, visited_edges, invalid_nodes = [], {}, []
            if verbose:
                self.env.render()
            while not self.env.done:
                self.algorithm.find(self.get_target(already_visited_pos), already_visited_pos=already_visited_pos,
                                    visited_edges=visited_edges, invalid_nodes=invalid_nodes, verbose=verbose)
