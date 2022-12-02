from src.minihack.env_gen import gen_minihack_env

env = gen_minihack_env()

env.reset()  # each reset generates a new environment instance
env.step(1)  # move agent '@' north
env.render()
