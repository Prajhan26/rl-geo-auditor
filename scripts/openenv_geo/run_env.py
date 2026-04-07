from env import GeoEnv
from models import Action

env = GeoEnv()

obs = env.reset()
print("start:", obs)

actions = ["up", "down", "left", "right"]

for step in range(10):
    action = Action(move=actions[step % 4])

    obs, reward, done = env.step(action)

    print(f"step {step}: {obs.position}, reward={reward}")

    if done:
        print("reached goal!")
        break