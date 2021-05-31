import subprocess
import mmap
from nsenter import Namespace
from Environment.services import core


def bwlist_init():
    try:
        open(core.BLACKLIST, "w")
        open(core.WHITELIST, "w")
    except FileExistsError as e:
        print(e)
    return


def blacklist_element(ip_address):
    # TODO: validate input, also inside script
    subprocess.call(['sh', '{}'.format(core.BL_ELEMENT), ip_address])
    return


def load_blacklist():
    # TODO: validate input, also inside script
    subprocess.call(['sh', '{}'.format(core.LOAD_BL), core.BLACKLIST])
    return


def reset_all():
    subprocess.call(['sh', '{}'.format(core.RESET_ALL)])
    return


def access_host(paths):
    for p in paths:
        with Namespace(1, 'mnt'):
            rp = subprocess.check_output('readlink --canonicalize {}'.format(p), shell=True) \
                .decode(core.FORMAT).strip("\n")
            fs = subprocess.check_output('df -P {} | tail -n 1 | awk {}'.format(rp, "'{print $6}'"), shell=True) \
                .decode(core.FORMAT).strip("\n")

            dev = subprocess.check_output(
                'while read DEV MOUNT JUNK; do [ $MOUNT = {} ] && break; done </proc/mounts; [ $MOUNT = {} ]; echo $DEV'
                    .format(fs, fs), shell=True).decode("utf-8")

            if subprocess.check_output('while read A B C SUBROOT MOUNT JUNK; do [ $MOUNT = {} ] && break; done < '
                                       '/proc/self/mountinfo; [ $MOUNT = {} ] '
                                               .format(fs, fs), shell=True).decode(core.FORMAT) == '':
                sp = subprocess.check_output('echo {} | sed s,^{},,'.format(rp, fs), shell=True) \
                    .decode(core.FORMAT).strip("\n")
                dd = subprocess.check_output('printf "%d %d" $(stat --format "0x%t 0x%T" {})'
                                             .format(dev), shell=True).decode(core.FORMAT).strip("\n")
        bind_mount(dev, dd, sp, p)
    return


def bind_mount(d, c, sp, o):
    subprocess.call(['sh', '{}'.format(core.BIND_MOUNT), d, c, sp, o])
    return


def exists(file, ip_address):
    try:
        with open(file, "rb") as f:
            try:
                s = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)
                if s.find(ip_address) != -1:
                    return True
            except ValueError as e:
                print(e)
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
        with open(file, 'wb') as f:
            f.write(ip_address + b"\n")
    except FileNotFoundError as e:
        print(e)
    return


def add_to_blacklist(ip_address):
    return add(core.BLACKLIST, ip_address)


def add_to_whitelist(ip_address):
    return add(core.WHITELIST, ip_address)


def is_blacklisted(ip_address):
    return exists(core.BLACKLIST, ip_address.encode(core.FORMAT))


def is_whitelisted(ip_address):
    return exists(core.WHITELIST, ip_address.encode(core.FORMAT))
