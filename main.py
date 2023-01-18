from src.minihack.env import Env
from src.path_finding.path_finding_runner import PathFindingRunner
from src.metrics import Analyzer
from src.path_finding.heuristics import Heuristics

analyzer = Analyzer(
    algorithms=[
        PathFindingRunner(),
        PathFindingRunner(heuristic=Heuristics.manhattan),
        PathFindingRunner(heuristic=Heuristics.euclidean),
        PathFindingRunner(heuristic=Heuristics.walkable_steps_in_matrix),
    ],
    env_n=1,
    max_episode_steps=1000,
)

analyzer.analyze()

print(analyzer.metrics)