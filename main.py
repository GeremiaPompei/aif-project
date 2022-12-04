from src.minihack.env import Env
from src.path_finding.bfs import BFS

env = Env()
algorithm = BFS(env)

algorithm.run()
