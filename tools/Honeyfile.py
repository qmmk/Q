from tools import Core
from tools.Utilities import *
import inotify.adapters
import inotify.constants
import concurrent.futures
import asyncio

MAX_WORKERS = 5


class Honeyfile(Core):
    def __init__(self, tool):
        super().__init__(tool)
        self.fd = inotify.adapters.Inotify()
        self.paths = tool.attr
        self.method = get_method(tool.method)
        self.action = ""

        for path in self.paths:
            try:
                print("auditing", path)
                self.add_watch(path)
                subprocess.check_output("auditctl -w {} -p war".format(path), shell=True)
            except subprocess.CalledProcessError as e:
                super().log(Core.DEBUG, "HONEYFILE", "auditctl error: {} for '{}'".format(e.output, path))
        super().log(Core.INFO, "HONEYFILE", "finished initialization")

    def __del__(self):
        for path in self.paths:
            self.fd.remove_watch(path)

    def add_watch(self, path):
        wd = self.fd.add_watch(path)
        if wd == -1:
            super().log(Core.INFO, "HONEYFILE", "Couldn't add watch to {0}".format(path))
        else:
            super().log(Core.INFO, "HONEYFILE", "Added inotify watch to: {0}, value: {1}".format(path, wd))
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
        type = " - ".join(types)

        super().log(Core.DEBUG, "HONEYFILE", "{} called because of'{}/{}' and mask 0x{:8X} - [{}]"
                    .format(self.method, target, name, mask, self.action))

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
                super().log(Core.WARNING, "HONEYFILE", "file '{}/{}' has been {}! {}"
                            .format(target, name, self.action, audit_info))
                filename = target + '/' + name
            else:
                super().log(Core.WARNING, "HONEYFILE",
                            "{} '{}' has been {}! {}".format(type, target, self.action, audit_info))
                print("HONEYFILE {} '{}' has been {}! {}".format(type, target, self.action, audit_info))
                filename = target

            if self.method == Core.SAVE_DATA:  # we save data only when the file has been closed
                # and when it's not the entire directory
                if self.action == "CLOSED" and (not mask & Core.IN_ISDIR):
                    execute_action(self, "HONEYFILE", self.method, ppid, user, filename)
            else:
                execute_action(self, "HONEYFILE", self.method, ppid, user, filename)
