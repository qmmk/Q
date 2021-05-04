import sys
import subprocess
from Environment import Environment


def main():
    env = Environment()

    while True:
        if input() == "":
            break


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("Shutdown requested...exiting\n")
    sys.exit(0)
