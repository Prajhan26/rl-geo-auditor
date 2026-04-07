from models import State, Action, Observation

class GeoEnv:
    def __init__(self):
        self.grid_size = 5
        self.start = (0, 0)
        self.goal = (4, 4)
        self.obstacles = {(1, 1), (1, 2), (2, 1), (3, 3)}

        self.state = State(position=self.start)

    def reset(self):
        self.state = State(position=self.start)
        return Observation(position=self.state.position)

    def step(self, action: Action):
        row, col = self.state.position

        if action.move == "up":
            row -= 1
        elif action.move == "down":
            row += 1
        elif action.move == "left":
            col -= 1
        elif action.move == "right":
            col += 1

        row = max(0, min(row, self.grid_size - 1))
        col = max(0, min(col, self.grid_size - 1))

        new_pos = (row, col)

        if new_pos in self.obstacles:
            reward = -5
            new_pos = self.state.position
        elif new_pos == self.goal:
            reward = 20
        else:
            reward = -1

        self.state = State(position=new_pos)

        done = new_pos == self.goal

        return Observation(position=new_pos), reward, done