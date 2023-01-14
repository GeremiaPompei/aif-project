from src.path_finding.astar_runner import AStarRunner
from src.metrics import AlgorithmProfiler
from src.path_finding.heuristics import Heuristics

profiler = AlgorithmProfiler(
    algorithm=AStarRunner(heuristic=Heuristics.walkable_steps_in_matrix),
    n=10
)

profiler.profile()
metrics = profiler.compute_metrics()

print(metrics)
