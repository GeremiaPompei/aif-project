from src.minihack.env import Env
from src.path_finding.astar_planner import AStarPlanner
from src.rl.rl_planner import RLPlanner

env = Env(all_visible=False)

algorithm = AStarPlanner(env)
#algorithm = RLPlanner(env)

algorithm.run()
