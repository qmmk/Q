import concurrent.futures
import inotify.adapters
import inotify.constants
from services.core import *
from services.utils import *
import subprocess
from os import listdir
from os.path import isfile, join
import os.path


MAX_WORKERS = 5
DATABASE = "persistent/artillery_integrity.db"


class ArtilleryIntegrity(Core):
    def __init__(self, tool):
        super().__init__()
        self.files = []
        self.paths = tool.attr
        self.method = get_method(tool.method)
        self.action = ""

        # DB initialization
        conn = create_connection(DATABASE)
        if conn is not None:
            create_table_files(conn)
        else:
            log.sintetic_write(log.ERROR, "ARTILLERY INTEGRITY", "error, cannot create the DB connection")

        # Clean previous associations and DB
        artillery_clean(conn)

        # Create digests for each file in path
        for path in self.paths:
            if os.path.isdir(path):
                # super().log(Core.INFO, "ARTILLERY INTEGRITY will monitor '{}'".format(path))
                onlyfiles = [f for f in listdir(path) if isfile(join(path, f))]
                for name in onlyfiles:
                    filename = path + '/' + name
                    try:
                        subprocess.check_output("auditctl -w {} -p wa".format(filename), shell=True)
                    except subprocess.CalledProcessError as e:
                        log.sintetic_write(log.DEBUG, "ARTILLERY INTEGRITY",
                                           "auditctl error: {} for '{}'".format(e.output, name))
                    db_insert_file_entry(conn, filename)
                    self.files.append(filename)
            else:
                log.sintetic_write(log.ERROR, "ARTILLERY INTEGRITY", "error, '{}' is not a directory".format(path))
        log.sintetic_write(log.INFO, "ARTILLERY INTEGRITY", "finished initialization")

    def run(self, loop, shared):
        with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            try:
                i = inotify.adapters.Inotify()
                for filename in self.files:
                    wd = i.add_watch(filename)
                    if wd == -1:
                        log.sintetic_write(log.INFO, "ARTILLERY INTEGRITY", "Couldn't add watch to {0}".format(filename))
                    else:
                        log.sintetic_write(log.INFO, "ARTILLERY INTEGRITY",
                                           "Added inotify watch to: {0}, value: {1}".format(filename, wd))

                for event in i.event_gen():
                    if event is not None:
                        loop.run_in_executor(executor, self.process(event))
            finally:
                time.sleep(1)

    def process(self, event):
        (header, types, target, name) = event
        mask = header.mask

        if not (mask & Core.IN_ISDIR):
            if check_mask(mask):
                conn = create_connection(DATABASE)
                if conn is None:
                    log.sintetic_write(log.ERROR, "ARTILLERY INTEGRITY", "error, cannot create the DB connection")

                filename = target + '/' + name

                if is_in_file(conn, filename):
                    self.action = get_action(mask)

                    audit_info, ppid, comm, user = check_audit(name)
                    # TODO: check audit should look for path+name, but for unknown reasons sometimes it doesn't work
                    #  by providing the entire path

                    log.sintetic_write(log.CRITICAL, "ARTILLERY INTEGRITY",
                                       "file '{}/{}' has been {}! {}".format(target, name, self.action, audit_info))
                    if comm != "adarch":  # execute action only if the event was not caused by adarch itself
                        execute_action("ARTILLERY INTEGRITY", self.method, ppid, user, filename)

                if mask & Core.IN_CREATE:
                    audit_info, ppid = check_audit(name)  # TODO: same as above
                    log.sintetic_write(log.CRITICAL, "ARTILLERY INTEGRITY",
                                       "file '{}/{}' has been CREATED! {}".format(target, name, audit_info))
                    # TODO: da verificare che azione effettuava
                    # self.execute_action(ppid, filename)
                    execute_action("ARTILLERY INTEGRITY", self.method, ppid, None, filename)
        return
