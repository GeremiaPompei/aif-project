from src.path_finding.path_finding_runner import PathFindingRunner
from src.metrics import Analyzer
from src.path_finding.heuristics import Heuristics
from src.rl.rl_runner import RLRunner

analyzer = Analyzer(
    algorithms=[
        RLRunner(),
        PathFindingRunner(),
        PathFindingRunner(heuristic=Heuristics.manhattan),
        PathFindingRunner(heuristic=Heuristics.euclidean),
        PathFindingRunner(heuristic=Heuristics.walkable_steps_in_matrix),
    ],
    env_n=1000,
    max_episode_steps=1000,
)

analyzer.analyze()

print(analyzer.metrics)
