from src.minihack.env import Env
from src.path_finding.astar import AStar

env = Env(all_visible=True)
algorithm = AStar(env)

algorithm.run(">")
