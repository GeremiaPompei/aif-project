from src.path_finding.astar_runner import AStarRunner
from src.metrics import Analyzer

profiler = Analyzer(
    algorithm=AStarRunner,
    n=10
)

profiler.profile()
