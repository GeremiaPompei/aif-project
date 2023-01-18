from src.path_finding.path_finding_runner import PathFindingRunner
from src.metrics import Analyzer

profiler = Analyzer(
    algorithm=PathFindingRunner,
    n=10
)

profiler.profile()
