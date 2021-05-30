import sys
import time
from Agent.agent import Agent
from Environment.environment import Environment
from Environment.services.bwlist import load_obs_data


def main():
    # env = Environment()
    agent = Agent()

    while True:
        obs = load_obs_data()
        action, _ = agent.model.predict(obs)
        obs, rewards, dones, info = agent.env.step(action)
        # update_state
        time.sleep(10)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("Shutdown requested...exiting\n")
    sys.exit(0)
