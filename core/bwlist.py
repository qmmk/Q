import subprocess
import mmap

BLACKLIST = "persistent/blacklist.txt"
WHITELIST = "persistent/whitelist.txt"


def blacklist_element(ip_address):
    # TODO: validate input, also inside script
    subprocess.call(['sh', './scripts/blacklist_element.sh', ip_address])
    return


def load_blacklist(filename):
    # TODO: validate input, also inside script
    subprocess.call(['sh', './scripts/load_blacklist_rules.sh', filename])
    return


def exists(file, ip_address):
    try:
        with open(file) as f:
            s = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)
            if s.find(format(b"{0}", ip_address)) != -1:
                return True
    except FileNotFoundError as e:
        print(e)
    return False


def add(file, ip_address):
    if not exists(file, ip_address):
        write(file, ip_address)
        return True
    return False


def remove(file, ip_address):
    lines = []
    try:
        with open(file, "a") as f:
            lines = f.readlines()
    except FileNotFoundError as e:
        print(e)

    for index, line in enumerate(lines):
        if line.strip("\n") == ip_address:
            del lines[index]
    return


def write(file, ip_address):
    try:
        with open(file, 'a') as f:
            f.write(format("{0}\n", ip_address))
    except FileNotFoundError as e:
        print(e)
    return
