import sys
import traceback
import subprocess
from Environment import Environment


def main():
    print("Exec subprocess")
    #r = subprocess.Popen("ausearch -f /home/kali/Q_Testing/data/426 -i", shell=True, stdout=subprocess.PIPE)

    p = subprocess.Popen("ausearch -f /home/kali/Q_Testing/data/426 -i", shell=True, stdout=subprocess.PIPE)
    res = p.stdout.read().decode()
    print(res)

    #env = Environment()

    while True:
        if input() == "":
            break


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("Shutdown requested...exiting\n")
    sys.exit(0)
