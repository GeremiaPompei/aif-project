from src.path_finding import PathFindingRunner, Heuristics
from src.metrics import Analyzer
from src.path_finding.astar import AStar
from src.path_finding.greedy import Greedy
from src.rl import RLRunner

analyzer = Analyzer(
    algorithms=[
        PathFindingRunner(algorithm=Greedy(heuristic=Heuristics.manhattan)),
        PathFindingRunner(algorithm=Greedy(heuristic=Heuristics.euclidean)),
        PathFindingRunner(algorithm=Greedy(heuristic=Heuristics.walkable_steps_in_matrix)),
        PathFindingRunner(algorithm=AStar()),
        PathFindingRunner(algorithm=AStar(heuristic=Heuristics.manhattan)),
        PathFindingRunner(algorithm=AStar(heuristic=Heuristics.euclidean)),
        PathFindingRunner(algorithm=AStar(heuristic=Heuristics.walkable_steps_in_matrix)),
        RLRunner(),
    ],
    env_n=1000,
    max_episode_steps=1000,
)

analyzer.analyze()

print(analyzer.metrics)
