import random

# grid settings
grid_size = 5
start = (0, 0)
goal = (4, 4)
obstacles = {(1, 1), (1, 2), (2, 1), (3, 3)}

actions = ["up", "down", "left", "right"]

# q-table
q_table = {}
for row in range(grid_size):
    for col in range(grid_size):
        q_table[(row, col)] = {action: 0.0 for action in actions}

# learning settings
alpha = 0.1
gamma = 0.9
epsilon = 0.3
episodes = 500

def take_action(state, action):
    row, col = state

    if action == "up":
        row -= 1
    elif action == "down":
        row += 1
    elif action == "left":
        col -= 1
    elif action == "right":
        col += 1

    row = max(0, min(row, grid_size - 1))
    col = max(0, min(col, grid_size - 1))

    new_state = (row, col)

    if new_state in obstacles:
        return state, -5

    if new_state == goal:
        return new_state, 20

    return new_state, -1

# training
for episode in range(episodes):
    state = start
    total_reward = 0

    for step in range(50):
        if random.random() < epsilon:
            action = random.choice(actions)
        else:
            action = max(q_table[state], key=q_table[state].get)

        next_state, reward = take_action(state, action)
        total_reward += reward

        old_q = q_table[state][action]
        best_next_q = max(q_table[next_state].values())

        new_q = old_q + alpha * (reward + gamma * best_next_q - old_q)
        q_table[state][action] = new_q

        state = next_state

        if state == goal:
            break

    if (episode + 1) % 50 == 0:
        print(f"episode {episode + 1}: total_reward = {total_reward}")

# learned policy
print("\nlearned policy:")
for row in range(grid_size):
    for col in range(grid_size):
        state = (row, col)

        if state == goal:
            print(f"{state}: GOAL")
        elif state in obstacles:
            print(f"{state}: OBSTACLE")
        else:
            best_action = max(q_table[state], key=q_table[state].get)
            print(f"{state}: {best_action}")

# follow learned path
print("\nlearned path from start:")
state = start
path = [state]

for _ in range(20):
    if state == goal:
        break

    action = max(q_table[state], key=q_table[state].get)
    next_state, _ = take_action(state, action)

    if next_state == state or next_state in path:
        break

    path.append(next_state)
    state = next_state

print(path)

# visual grid
print("\nvisual grid:")
path_set = set(path)

for row in range(grid_size):
    cells = []
    for col in range(grid_size):
        state = (row, col)

        if state == start:
            cells.append("S")
        elif state == goal:
            cells.append("G")
        elif state in obstacles:
            cells.append("X")
        elif state in path_set:
            cells.append("*")
        else:
            cells.append(".")
    print(" ".join(cells))