from src.path_finding.astar_planner import AStarPlanner
from src.metrics import AlgorithmProfiler

profiler = AlgorithmProfiler(
    algorithm=AStarPlanner,
    n=10
)

profiler.profile()
