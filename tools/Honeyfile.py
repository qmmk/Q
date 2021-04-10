from core.pool import CancellablePool
from tools import Core
from tools.Utilities import *
import inotify.adapters
import inotify.constants
import concurrent.futures
import asyncio


class Honeyfile(Core):
    def __init__(self, paths):
        super().__init__(paths)
        self.fd = inotify.adapters.Inotify()
        self.const = inotify.constants
        self.paths = paths

        for path in paths:
            try:
                print("auditing", path)
                subprocess.check_output("auditctl -w {} -p war".format(path), shell=True)
                self.add_watch(path)
            except subprocess.CalledProcessError as e:
                super().log(Core.DEBUG, "HONEYFILE", "auditctl error: {} for '{}'".format(e.output, path))
        super().log(Core.INFO, "HONEYFILE", "finished initialization")

    def add_watch(self, path):
        wd = self.fd.add_watch(path)
        if wd == -1:
            super().log(Core.INFO, "HONEYFILE", "Couldn't add watch to {0}".format(path))
        else:
            super().log(Core.INFO, "HONEYFILE", "Added inotify watch to: {0}, value: {1}".format(path, wd))
        return

    def run(self, loop, tools):
        output = loop.run_until_complete(asyncio.gather(self.start(tools)))

    async def start(self, tools):
        while True:
            try:
                for event in self.fd.event_gen():
                    if event is not None:
                        (header, type, target, name) = event

                        mask = header.mask
                        action = self.return_action(mask)
                        super().log(Core.DEBUG, "HONEYFILE", "start called because of'{}/{}' and mask 0x{:8X} - [{}]"
                                    .format(target, name, mask, action))

                        if mask & Core.IN_ISDIR or len(name) == 0:
                            print("auditing", target)
                            audit_info, ppid, comm, user = check_audit(target)
                        if len(name) > 0:
                            # TODO: should be target, but ausearch sometimes doesnt work when providing entire path
                            audit_info, ppid, comm, user = check_audit(name)

                        # execute action only if the event was not caused by adarch itself
                        if comm != "adarch":
                            # if name has content, it means that it is a file inside a monitored directory
                            if len(name) > 1:
                                super().log(Core.WARNING, "HONEYFILE",
                                            "file '{}/{}' has been {}! {}".format(target, name, action, audit_info))
                                filename = target + '/' + name
                            else:
                                super().log(Core.WARNING, "HONEYFILE",
                                            "{} '{}' has been {}! {}".format(type, target, action, audit_info))
                                print("HONEYFILE {} '{}' has been {}! {}".format(type, target, action, audit_info))
                                filename = target

                            if self.action == Core.SAVE_DATA:  # we save data only when the file has been closed
                                if action == "CLOSED" and (
                                        not mask & Core.IN_ISDIR):  # and when it's not the entire directory
                                    execute_action(self, "HONEYFILE", self.action, ppid, user, filename)
                            else:
                                execute_action(self, "HONEYFILE", self.action, ppid, user, filename)
            finally:
                time.sleep(1)

    # <editor-fold desc="ACTION">

    def save_data(self, mask, name, target):
        self.action = Core.LOG_EVENT | Core.SAVE_DATA
        self.start(mask, name, target)

    def shutdown_host(self, mask, name, target):
        self.action = Core.LOG_EVENT | Core.SHUTDOWN_HOST
        self.start(mask, name, target)

    def kill_pid(self, mask, name, target):
        self.action = Core.LOG_EVENT | Core.KILL_PID
        self.start(mask, name, target)

    def kill_user(self, mask, name, target):
        self.action = Core.LOG_EVENT | Core.KILL_USER
        self.start(mask, name, target)

    def lock_user(self, mask, name, target):
        self.action = Core.LOG_EVENT | Core.LOCK_USER
        self.start(mask, name, target)

    def kill_pid_kill_user(self, mask, name, target):
        self.action = Core.LOG_EVENT | Core.KILL_USER | Core.KILL_PID
        self.start(mask, name, target)

    def kill_pid_lock_user(self, mask, name, target):
        self.action = Core.LOG_EVENT | Core.LOCK_USER | Core.KILL_USER | Core.KILL_PID
        self.start(mask, name, target)

    def just_log(self, mask, name, target):
        self.action = Core.LOG_EVENT
        self.start(mask, name, target)

    def return_action(self, mask):
        if mask & self.const.IN_ISDIR:
            return "DIRECTORY"
        if mask & self.const.IN_MODIFY:
            return "MODIFIED"
        if mask & self.const.IN_ACCESS:
            return "ACCESSED"
        if mask & self.const.IN_CREATE:
            return "CREATED"
        if mask & self.const.IN_OPEN:
            return "OPENED"
        if (mask & self.const.IN_MOVED_TO) or (mask & self.const.IN_MOVED_FROM):
            return "MOVED"
        if mask & self.const.IN_CLOSE:
            return "CLOSED"
        if mask & self.const.IN_DELETE:
            return "DELETED"
        if mask & self.const.IN_DELETE_SELF:
            return "DELETED (SELF)"
        if mask & self.const.IN_ATTRIB:
            return "ATTRIBUTE CHANGED"

    # </editor-fold>





