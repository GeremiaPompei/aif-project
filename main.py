from src.minihack.env import Env
from src.path_finding.graph_search import BFS, DFS

env = Env(all_visible=False)
algorithm = BFS(env)

algorithm.run(" ")
