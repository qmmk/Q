from services.utils import *


MAX_WORKERS = 5


class Honeyfile(Core):
    def __init__(self, tool):
        super().__init__()
        self.paths = tool.paths
        self.method = get_method(tool.method)
        self.action = ""

        for path in self.paths:
            try:
                # print("auditing", path)
                log.sintetic_write(log.DEBUG, "HONEYFILE", "Auditing {}".format(path))
                subprocess.check_output("auditctl -w {} -p war".format(path), shell=True)
            except subprocess.CalledProcessError as e:
                log.sintetic_write(log.DEBUG, "HONEYFILE", "auditctl error: {} for '{}'".format(e.output, path))
        log.sintetic_write(log.INFO, "HONEYFILE", "finished initialization")

    def process(self, event):
        (header, types, target, name) = event

        mask = header.mask
        self.action = get_action(mask)
        type = " - ".join(types)

        log.sintetic_write(log.DEBUG, "HONEYFILE", "{} called because of'{}/{}' and mask 0x{:8X} - [{}]"
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
                log.sintetic_write(log.WARNING, "HONEYFILE", "file '{}/{}' has been {}! {}"
                                   .format(target, name, self.action, audit_info))
                filename = target + '/' + name
            else:
                log.sintetic_write(log.WARNING, "HONEYFILE",
                                   "{} '{}' has been {}! {}".format(type, target, self.action, audit_info))
                print("HONEYFILE {} '{}' has been {}! {}".format(type, target, self.action, audit_info))
                filename = target

            if self.method == Core.SAVE_DATA:  # we save data only when the file has been closed
                # and when it's not the entire directory
                if self.action == "CLOSED" and (not mask & Core.IN_ISDIR):
                    execute_action("HONEYFILE", self.method, ppid, user, filename)
            else:
                execute_action("HONEYFILE", self.method, ppid, user, filename)
        return
