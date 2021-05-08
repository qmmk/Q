import random
import hashlib
import subprocess
import re
import sqlite3
import os
import signal
import tarfile
import os.path
import calendar
import time
import scripts.userlocker
import inotify.constants
from sqlite3 import Error
from services.core import Core
from services import log
from collections import defaultdict
from datetime import datetime, timedelta


# <editor-fold desc="GENERAL">

def get_method(method):
    if method == "save_data":
        return Core.LOG_EVENT | Core.SAVE_DATA
    if method == "shutdown_host":
        return Core.LOG_EVENT | Core.SHUTDOWN_HOST
    if method == "kill_pid":
        return Core.LOG_EVENT | Core.KILL_PID
    if method == "kill_user":
        return Core.LOG_EVENT | Core.KILL_USER
    if method == "lock_user":
        return Core.LOG_EVENT | Core.LOCK_USER
    if method == "kill_pid_kill_user":
        return Core.LOG_EVENT | Core.KILL_USER | Core.KILL_PID
    if method == "kill_pid_lock_user":
        return Core.LOG_EVENT | Core.LOCK_USER | Core.KILL_USER | Core.KILL_PID
    if method == "just_log":
        return Core.LOG_EVENT


def get_action(mask):
    if mask & inotify.constants.IN_MODIFY:
        return "MODIFIED"
    if mask & inotify.constants.IN_ACCESS:
        return "ACCESSED"
    if mask & inotify.constants.IN_CREATE:
        return "CREATED"
    if mask & inotify.constants.IN_OPEN:
        return "OPENED"
    if (mask & inotify.constants.IN_MOVED_TO) or (mask & inotify.constants.IN_MOVED_FROM):
        return "MOVED"
    if mask & inotify.constants.IN_CLOSE:
        return "CLOSED"
    if mask & inotify.constants.IN_DELETE:
        return "DELETED"
    if mask & inotify.constants.IN_DELETE_SELF:
        return "DELETED (SELF)"
    if mask & inotify.constants.IN_ATTRIB:
        return "ATTRIBUTE CHANGED"
    if mask & inotify.constants.IN_CLOSE_WRITE:
        return "CLOSED AFTER BEING MODIFIED"
    if (mask & inotify.constants.IN_MOVED_TO) or (mask & inotify.constants.IN_MOVED_FROM):
        return "MOVED"
    if (mask & inotify.constants.IN_DELETE) or (mask & inotify.constants.IN_DELETE_SELF):
        return "DELETED"
    if mask & inotify.constants.IN_ATTRIB:
        return "subject to an ATTRIBUTE CHANGE"
    if mask & inotify.constants.IN_ISDIR:
        return "DIRECTORY"


def check_mask(mask):
    return (mask & (Core.IN_MODIFY | Core.IN_ACCESS | Core.IN_CLOSE_WRITE | Core.IN_ATTRIB | Core.IN_DELETE |
                    Core.IN_DELETE_SELF | Core.IN_MOVE))


# </editor-fold>

# <editor-fold desc="DATABASE">

def create_connection(db_file):
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except sqlite3.Error as e:
        print(e)
    return conn


def random_date(start, end, prop):
    stime = start
    etime = end
    ptime = stime + prop * (etime - stime)
    return ptime


def create_table_files(conn):
    create_table_sql = ''' CREATE TABLE IF NOT EXISTS files (
                                        filename text NOT NULL
                    ); '''
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except Error as e:
        print(e)


def db_insert_file_entry(conn, filename):
    cur = conn.cursor()
    cur.execute('INSERT INTO files VALUES(?)', [filename])
    conn.commit()
    return cur.lastrowid


def cryptolocked_clean(conn):
    cur = conn.cursor()
    cur.execute("SELECT * FROM files")

    rows = cur.fetchall()

    for row in rows:
        if file_exists(row[0]):
            destroy_file(row[0])

    cur = conn.cursor()
    cur.execute('DELETE FROM files')
    conn.commit()


def is_in_file(conn, filename):
    cur = conn.cursor()
    cur.execute("SELECT * FROM files WHERE filename=?", (filename,))
    if len(cur.fetchall()) > 0:
        return True
    return False


def update_db(db, ip, port):
    with open(db, "r+") as file:
        for line in file:
            x = line.split(";")
            if ip == x[0] and str(port) == x[1]:
                break
        else:  # not found, we are at the eof
            file.write("{};{};\n".format(ip, port))


def is_first_time(db, ip, port):
    open(db, 'a').close()  # create file if it does not exist
    with open(db, "r+") as file:
        for line in file:
            x = line.split(";")
            print(x, ip, port, ip == x[0], port == x[1])
            if ip == x[0] and str(port) == x[1]:
                print("MATCHED", ip, "on", port)
                return False
        print("NEVER FOUND", ip, "on", port)
        return True


def artillery_clean(conn):
    cur = conn.cursor()
    cur.execute('DELETE FROM files')
    conn.commit()


def db_get_file_digest(conn, filename):
    cur = conn.cursor()
    cur.execute("SELECT * FROM files WHERE filename=?", (filename,))

    rows = cur.fetchall()
    if len(rows) > 0:
        return rows[0][1]
    return None


# </editor-fold>

# <editor-fold desc="FIXED ACTION">

def execute_action(toolname, action, ppid, user, source_filename):
    if action & Core.SHUTDOWN_HOST:
        log.sintetic_write(log.CRITICAL, toolname, "shutting down host...")
        os.system('systemctl poweroff')

    if action & Core.KILL_USER:
        if user is not None and user != "admin" and user != "root":  # insert your exceptions...
            log.sintetic_write(log.CRITICAL, toolname, "killing user {}".format(user))
            try:
                os.system("pkill -KILL -u {}".format(user))
                subprocess.run(['pkill', '-KILL -u {}'.format(user)], check=True)
                log.sintetic_write(log.INFO, toolname, "user {} killed!".format(user))
            except subprocess.CalledProcessError:
                log.sintetic_write(log.ERROR, toolname, "can't kill user {}".format(user))

    if action & Core.LOCK_USER:
        if user is not None and user != "admin" and user != "root":  # insert your exceptions...
            log.sintetic_write(log.CRITICAL, toolname, "locking user {}".format(user))
            try:
                os.system("usermod --lock {}".format(user))
                scripts.userlocker.lockuser(user)
                log.sintetic_write(log.INFO, toolname, "user {} locked!".format(user))
            except subprocess.CalledProcessError:
                log.sintetic_write(log.ERROR, toolname, "can't lock user {}".format(user))

    if action & Core.SAVE_DATA:
        title = source_filename.replace("/", "")
        output_filename = "/var/adarch/" + title + "-" + str(calendar.timegm(time.gmtime())) + ".tar.gz"
        log.sintetic_write(log.DEBUG, toolname, "saving {}...".format(output_filename))
        with tarfile.open(output_filename, "w:gz") as tar:
            tar.add(source_filename, arcname=os.path.basename(source_filename))
            tar.close()
            log.sintetic_write(log.INFO, toolname, "saved compressed file {}".format(output_filename))

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

            log.sintetic_write(log.CRITICAL, toolname, "killing PID {} and its parents: {}".format(ppid, record))
            for r in clean:
                malicious_pid = int(r)
                try:
                    if int(r) != mypid:
                        print("check2", malicious_pid, mypid)
                        os.kill(int(r), signal.SIGKILL)  # or signal.SIGKILL
                        log.sintetic_write(log.INFO, toolname, "Parent PID {} killed!".format(r))
                except Exception as e:
                    log.sintetic_write(log.ERROR, toolname, "can't kill malicious parent process {}! {}".format(r, e))
            try:
                os.kill(int(ppid), signal.SIGKILL)  # or signal.SIGKILL
                log.sintetic_write(log.INFO, toolname, "Original PPID {} killed!".format(ppid))
            except Exception as e:
                log.sintetic_write(log.ERROR, toolname, "can't kill malicious parent process! {}".format(e))
        else:
            log.sintetic_write(log.ERROR, toolname, "can't kill malicious process, no ppid available!")


def check_audit(filename):
    try:
        result = subprocess.check_output("ausearch -f {} -i".format(filename), shell=True)
    except subprocess.SubprocessError as e:
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
        audit_info = "(last audit record: proctitle={} | comm={} | exe={} | euid={} | ppid={})" \
            .format(d['proctitle'], d['comm'], d['exe'], d['euid'], d['ppid'])
        return audit_info, d['ppid'], d['comm'], d['euid']
    return "", None, None, None


# </editor-fold>

# <editor-fold desc="FILE MANAGER">

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


def restore_file(filename):
    if file_exists(filename):
        destroy_file(filename)
    content = rand_data()
    create_file(filename, content, None)
    date = random_date(datetime.now() - timedelta(days=120), datetime.now(), random.random())
    modTime = time.mktime(date.timetuple())
    os.utime(filename, (modTime, modTime))


# </editor-fold>

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
