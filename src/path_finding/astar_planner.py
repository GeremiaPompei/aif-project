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

    def __init__(self, env: Env, profiler):
        self.env = env
        self.algorithm = AStar(env, is_valid_edge)
        self.profiler = profiler
        self.targets_list = [[Symbols.STAIR_UP_CHAR], [Symbols.KEY_CHAR],
                             Symbols.DOOR_OPEN_CHARS, Symbols.CORRIDOR_CHARS,
                             Symbols.DOOR_CLOSE_CHARS, [Symbols.OBSCURE_CHAR]]
        self.walkable_symbols = Symbols.DOOR_CLOSE_CHARS + Symbols.WALKABLE_SYMBOLS

    def get_target(self, already_visited_pos):
        for targets in self.targets_list:
            if not self.algorithm.reachable(targets):
                continue
            if targets[0] in Symbols.CORRIDOR_CHARS:
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

    def run(self, verbose: bool = True):
        self.env.reset()
        self.algorithm.refresh_graph()
        already_visited_pos, visited_edges, invalid_nodes = {}, {}, []
        if verbose:
            self.env.render()
        total_steps, steps_first_key, steps_first_door, steps_first_corridor = 0, None, None, None
        while not self.env.done:
            self.algorithm.find(self.get_target(set(already_visited_pos.keys())),
                                already_visited_pos=already_visited_pos, visited_edges=visited_edges,
                                invalid_nodes=invalid_nodes, verbose=verbose)
            total_steps += 1
            if steps_first_key is None and self.env.over_hero_symbol == Symbols.KEY_CHAR:
                steps_first_key = total_steps
            if steps_first_door is None and \
                    self.env.over_hero_symbol in Symbols.DOOR_OPEN_CHARS + Symbols.DOOR_CLOSE_CHARS:
                steps_first_door = total_steps
            if steps_first_corridor is None and self.env.over_hero_symbol in Symbols.CORRIDOR_CHARS:
                steps_first_corridor = total_steps
        return (self.env.over_hero_symbol == Symbols.STAIR_UP_CHAR), total_steps, steps_first_key, steps_first_door, steps_first_corridor
