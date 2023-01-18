from src.path_finding import PathFindingRunner, Heuristics
from src.metrics import Analyzer
from src.rl import RLRunner

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
