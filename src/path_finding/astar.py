import numpy as np

from src.minihack.env import Env


class AStar:

    def __init__(self, env: Env):
        self.env = env

    def run(self, times: int = 1):
        for _ in range(times):
            self.env.reset()
            while not self.env.done:
                self.search()
            self.env.render()



    def heuristic(self, a, b) -> float:
        (x1, y1) = a
        (x2, y2) = b
        return abs(x1 - x2) + abs(y1 - y2)


    def search(self):
        goal = self.env.find_first_char_pos('>')
        frontier = []
        start = self.env.find_first_char_pos('@')
        frontier.put(start, 0)
        came_from = {}
        cost_so_far = np.array(self.env.shape)
        came_from[start] = None
        cost_so_far[start] = 0

        while not frontier.empty():
            current = self.env.find_first_char_pos('@')

            if current == goal:
                break

            for next in self.graph["neighbors"](current):
                new_cost = cost_so_far[current] + self.graph["neighbors"].cost(current, next)
                if next not in cost_so_far or new_cost < cost_so_far[next]:
                    cost_so_far[next] = new_cost
                    priority = new_cost + self.heuristic(next, goal)
                    frontier.put(next, priority)
                    came_from[next] = current

        return came_from, cost_so_far
