from src.path_finding.astar_runner import AStarRunner
from src.metrics import Analyzer
from src.path_finding.heuristics import Heuristics

analyzer = Analyzer(
    algorithms=[
        AStarRunner(heuristic=Heuristics.euclidean),
        AStarRunner(heuristic=Heuristics.walkable_steps_in_matrix),
    ],
    env_n=3,
    max_episode_steps=2,
)

analyzer.analyze()

print(analyzer.metrics)
