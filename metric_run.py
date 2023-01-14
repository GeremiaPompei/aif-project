from src.path_finding.astar_runner import AStarPlanner
from src.metrics import AlgorithmProfiler

profiler = AlgorithmProfiler(
    algorithm=AStarPlanner,
    n=10
)

profiler.profile()
