import random
import hashlib
import subprocess
import re
from collections import defaultdict
import sqlite3
import os
import signal
import tarfile
import os.path
import calendar
import time
#import scripts.userlocker
from tools.Core import Core


# ------ Utility methods ----------------------------------

# this function is used by filesystem-based tools to execute custom actions
def execute_action(self, toolname, action, ppid, user, source_filename):
    if action & Core.SHUTDOWN_HOST:
        self.log(Core.CRITICAL, toolname, "shutting down host...")
        os.system('systemctl poweroff')

    if action & Core.KILL_USER:
        if user is not None and user != "admin" and user != "root":  # insert your exceptions...
            self.log(Core.CRITICAL, toolname, "killing user {}".format(user))
            try:
                os.system("pkill -KILL -u {}".format(user))
                # subprocess.run(['pkill', '-KILL -u {}'.format(user)], check = True)
                self.log(Core.INFO, toolname, "user {} killed!".format(user))
            except subprocess.CalledProcessError:
                self.log(Core.ERROR, toolname, "can't kill user {}".format(user))

    if action & Core.LOCK_USER:
        if user is not None and user != "admin" and user != "root":  # insert your exceptions...
            self.log(Core.CRITICAL, toolname, "locking user {}".format(user))
            try:
                # os.system("usermod --lock {}".format(user))
                # scripts.userlocker.lockuser(user)
                self.log(Core.INFO, toolname, "user {} locked!".format(user))
            except subprocess.CalledProcessError:
                self.log(Core.ERROR, toolname, "can't lock user {}".format(user))

    if action & Core.SAVE_DATA:
        title = source_filename.replace("/", "")
        output_filename = "/var/adarch/" + title + "-" + str(calendar.timegm(time.gmtime())) + ".tar.gz"
        self.log(Core.DEBUG, toolname, "saving {}...".format(output_filename))
        with tarfile.open(output_filename, "w:gz") as tar:
            tar.add(source_filename, arcname=os.path.basename(source_filename))
            tar.close()
            self.log(Core.INFO, toolname, "saved compressed file {}".format(output_filename))

    if action & Core.KILL_PID:
        if ppid is not None:
            ppid = re.sub("[^0-9]", "", ppid)
            mypid = os.getpid()
            result1 = subprocess.check_output("ps -o ppid={}".format(mypid), shell=True)
            record1 = [str(x.strip()) for x in result1.decode().split("\n")]
            print("check", ppid, mypid)
            result = subprocess.check_output("ps -o ppid={}".format(ppid), shell=True)
            record = [str(x.strip()) for x in result.decode().split("\n")]
            print("record", record, "record1", record1)
            clean = []
            for el in record:
                if el not in record1:
                    clean.append(el)
            print("clean", clean)

            self.log(Core.CRITICAL, toolname, "killing PID {} and its parents: {}".format(ppid, record))
            for r in clean:
                malicious_pid = int(r)
                try:
                    if int(r) != mypid:
                        print("check2", malicious_pid, mypid)
                        os.kill(int(r), signal.SIGKILL)  # or signal.SIGKILL
                        self.log(Core.INFO, toolname, "Parent PID {} killed!".format(r))
                except Exception as e:
                    self.log(Core.ERROR, toolname, "can't kill malicious parent process {}! {}".format(r, e))
            try:
                os.kill(int(ppid), signal.SIGKILL)  # or signal.SIGKILL
                self.log(Core.INFO, toolname, "Original PPID {} killed!".format(ppid))
            except Exception as e:
                self.log(Core.ERROR, toolname, "can't kill malicious parent process! {}".format(e))
        else:
            self.log(Core.ERROR, toolname, "can't kill malicious process, no ppid available!")


def is_valid_ipv4(ip):
    # if IP is cidr, strip net
    if "/" in ip:
        ipparts = ip.split("/")
        ip = ipparts[0]
    if not ip.startswith("#"):
        pattern = re.compile(r"""
    ^
    (?:
      # Dotted variants:
      (?:
        # Decimal 1-255 (no leading 0's)
        [3-9]\d?|2(?:5[0-5]|[0-4]?\d)?|1\d{0,2}
      |
        0x0*[0-9a-f]{1,2}  # Hexadecimal 0x0 - 0xFF (possible leading 0's)
      |
        0+[1-3]?[0-7]{0,2} # Octal 0 - 0377 (possible leading 0's)
      )
      (?:                  # Repeat 0-3 times, separated by a dot
        \.
        (?:
          [3-9]\d?|2(?:5[0-5]|[0-4]?\d)?|1\d{0,2}
        |
          0x0*[0-9a-f]{1,2}
        |
          0+[1-3]?[0-7]{0,2}
        )
      ){0,3}
    |
      0x0*[0-9a-f]{1,8}    # Hexadecimal notation, 0x0 - 0xffffffff
    |
      0+[0-3]?[0-7]{0,10}  # Octal notation, 0 - 037777777777
    |
      # Decimal notation, 1-4294967295:
      429496729[0-5]|42949672[0-8]\d|4294967[01]\d\d|429496[0-6]\d{3}|
      42949[0-5]\d{4}|4294[0-8]\d{5}|429[0-3]\d{6}|42[0-8]\d{7}|
      4[01]\d{8}|[1-3]\d{0,9}|[4-9]\d{0,8}
    )
    $
    """, re.VERBOSE | re.IGNORECASE)
        return pattern.match(ip) is not None


def file_integrity(filename, hash):
    try:
        if file_exists(filename):
            fi = open(filename, 'r')
            data = fi.read()
            _hash = hashlib.md5(data.encode('utf-8')).hexdigest()
            return hash == _hash
    except Exception as e:
        print(e)


def get_file_digest(filename):
    try:
        if file_exists(filename) and not os.path.isdir(filename):
            fi = open(filename, 'r')
            data = fi.read()
            _hash = hashlib.md5(data.encode('utf-8')).hexdigest()
            return _hash
    except Exception as e:
        print(e)
    return -1


def create_file(filename, content, hash):
    try:
        fi = open(filename, 'w')
        os.chmod(filename, 0o666)
        fi.write(content)
        fi.close()
        if hash is not None:
            if not file_integrity(filename, hash):
                print("File {} just created has integrity problems".format(filename))
    except Exception as e:
        print("File {} could be not created, excpetion: {}".format(filename, e))


def rand_data():
    dat = ''
    for i in range(random.randrange(150)):
        dat = dat + str(random.randint(1, 10000))
    return dat


def file_exists(filename):
    return os.path.isfile(filename)


def destroy_file(filename):
    try:
        os.remove(filename)
    except:
        print("File {} could be not deleted".format(filename))


def generate_digest(content):
    return hashlib.md5(content.encode('utf-8')).hexdigest()


def create_connection(db_file):
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except sqlite3.Error as e:
        print(e)
    return conn


def check_audit(filename):
    try:
        result = subprocess.check_output("ausearch -f {} -i".format(filename), shell=True)
    except Exception as e:
        print("Check audit exception {}".format(e))
        return "(no audit log available)", None, None, None
    record = result.decode().split("----")
    idx = len(record) - 1
    d = {}
    d = defaultdict(lambda: "", d)
    attributes = ["proctitle", "syscall", "ppid", "euid", "comm", "exe"]
    if idx >= 1:
        elements = record[idx].split(" ")
        for element in elements:
            for attribute in attributes:
                if re.search(attribute + "=", element):
                    d[attribute] = element.split("=", 1)[1]
        audit_info = "(last audit record: proctitle={} | comm={} | exe={} | euid={} | ppid={})".format(d['proctitle'],
                                                                                                       d['comm'],
                                                                                                       d['exe'],
                                                                                                       d['euid'],
                                                                                                       d['ppid'])
        return audit_info, d['ppid'], d['comm'], d['euid']
    return "", None, None, None
