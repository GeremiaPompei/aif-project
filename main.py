from src.minihack.env import Env
from src.path_finding.astar_planner import AStarPlanner

env = Env(all_visible=False)
algorithm = AStarPlanner(env)

algorithm.run()
