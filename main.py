import sys
import time
from Agent.agent import Agent
from Environment.environment import Environment


def main():
    env = Environment()
    agent = Agent()

    while True:
        time.sleep(15)

        # PREDICT ACTION
        action = agent.predict()

        # UPDATE STATE
        env.update_state(action)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("Shutdown requested...exiting\n")
    sys.exit(0)
