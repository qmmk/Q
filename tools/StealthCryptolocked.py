import asyncio
import inotify.constants
import inotify.adapters
from tools import Core
from tools.Utilities import *
import concurrent.futures
import random
import subprocess
import os
import os.path
import time
from datetime import datetime, timedelta


N_TENTACTLES = 5
MAX_WORKERS = 5
DATABASE = "persistent/stealthcryptolocked.db"


class StealthCryptolocked(Core):
    def __init__(self, tool):
        super().__init__(tool)
        self.fd = inotify.adapters.Inotify()
        self.paths = tool.attr
        self.method = get_method(tool.method)
        self.action = ""

        filenames = {}
        # create a list of random filenames in the given paths
        for path in self.paths:
            if os.path.isdir(path):
                super().log(Core.DEBUG, "STEALTH CRYPTOLOCKED", "will monitor '{}'".format(path))
                for i in range(N_TENTACTLES):
                    # while for no duplicate
                    while True:
                        name = "." + str(hex(random.randint(1, 10000))[2:])
                        filename = path + '/' + name
                        if name not in filenames:
                            filenames[name] = filename
                            break
            else:
                super().log(Core.ERROR, "STEALTH CRYPTOLOCKED", "error, '{}' is not a directory".format(path))

        # DB initialization
        conn = create_connection(DATABASE)
        if conn is not None:
            create_table_files(conn)
        else:
            super().log(Core.ERROR, "STEALTH CRYPTOLOCKED", "error, cannot create the DB connection")

        # Clean previous trip files and DB
        cryptolocked_clean(conn)

        # Place trip files
        for name, filename in filenames.items():
            if file_exists(filename):
                destroy_file(filename)
            content = rand_data()
            create_file(filename, content, None)
            date = random_date(datetime.now() - timedelta(days=120), datetime.now(), random.random())
            modTime = time.mktime(date.timetuple())
            os.utime(filename, (modTime, modTime))
            try:
                subprocess.check_output("auditctl -w {} -p war".format(filename), shell=True)
            except subprocess.CalledProcessError as e:
                super().log(Core.DEBUG, "STEALTH CRYPTOLOCKED", "auditctl error: {}".format(e.output))
            db_insert_file_entry(conn, filename)
            self.add_watch(filename)

        super().log(Core.INFO, "STEALTH CRYPTOLOCKED", "finished initialization")

    def add_watch(self, filename):
        wd = self.fd.add_watch(filename)
        if wd == -1:
            super().log(Core.INFO, "STEALTH CRYPTOLOCKED", "Couldn't add watch to {0}".format(filename))
        else:
            super().log(Core.INFO, "STEALTH CRYPTOLOCKED", "Added inotify watch to: {0}, value: {1}".format(filename, wd))
        return

    def run(self, loop, shared):
        output = loop.run_until_complete(asyncio.gather(self.start(shared)))

    async def start(self, shared):
        with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            try:
                for event in self.fd.event_gen():
                    if event is not None:
                        executor.submit(self.process, event)
            finally:
                time.sleep(1)

    def process(self, event):
        (header, types, target, name) = event
        mask = header.mask
        self.action = get_action(mask)

        if not (mask & Core.IN_ISDIR):
            if check_mask(mask):
                conn = create_connection(DATABASE)
                if conn is None:
                    super().log(Core.ERROR, "STEALTH CRYPTOLOCKED", "error, cannot create the DB connection")

                filename = str(target + '/' + name)
                if is_trip_file(conn, filename):
                    audit_info, ppid, comm, user = check_audit(name)
                    # TODO: check audit should look for path+name,
                    #  but for unknown reasons sometimes it doesn't work by providing the entire path
                    if self.method & Core.LOG_EVENT:
                        super().log(Core.CRITICAL, "STEALTH CRYPTOLOCKED", "file '{}/{}' has been {}! {}"
                                    .format(target, name, self.action, audit_info))
                    # execute action only if the event was not caused by adarch itself
                    if comm != "adarch":
                        execute_action(self, "STEALTH CRYPTOLOCKED", self.method, ppid, user, filename)