from datetime import datetime

LOG_FILE = "persistent/log.txt"


def write(lv, info):
    log = "{0} - [{1}] :: {2}\n".format(datetime.now().strftime("%d/%m/%Y %H:%M:%S"), lv, info)
    print(log.strip("\n"))
    try:
        with open(LOG_FILE, "a") as f:
            f.write(log)
    except FileNotFoundError as e:
        print(e)
    return


def destroy():
    return
