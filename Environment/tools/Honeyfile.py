from Environment.services.utils import *


def init_honeyfile(paths):
    for path in paths:
        try:
            log.sintetic_write(core.DEBUG, "HONEYFILE", "Auditing {}".format(path))
            subprocess.check_output("auditctl -w {} -p war".format(path), shell=True)
        except subprocess.CalledProcessError as e:
            log.sintetic_write(core.DEBUG, "HONEYFILE", "auditctl error: {} for '{}'".format(e.output, path))
    log.sintetic_write(core.INFO, "HONEYFILE", "finished initialization")
    return


def run_honeyfile(event, meth, tool_id):
    start = time.time()
    (header, types, target, name) = event

    mask = header.mask
    action = get_action(mask)
    method = get_method(meth)
    type = " - ".join(types)

    log.sintetic_write(core.DEBUG, "HONEYFILE", "{} called because of'{}/{}' and mask 0x{:8X} - [{}]"
                       .format(method, target, name, mask, action))

    if mask & core.IN_ISDIR or len(name) == 0:
        log.sintetic_write(core.DEBUG, "HONEYFILE", "Auditing {}".format(target))
        audit_info, ppid, comm, user = check_audit(target)
    if len(name) > 0:
        # TODO: should be target, but ausearch sometimes doesnt work when providing entire path
        audit_info, ppid, comm, user = check_audit(name)

    # execute action only if the event was not caused by adarch itself
    if comm != "adarch":
        # if name has content, it means that it is a file inside a monitored directory
        if len(name) > 1:
            log.sintetic_write(core.WARNING, "HONEYFILE", "file '{}/{}' has been {}! {}"
                               .format(target, name, action, audit_info))
            filename = target + '/' + name
        else:
            log.sintetic_write(core.WARNING, "HONEYFILE",
                               "{} '{}' has been {}! {}".format(type, target, action, audit_info))
            filename = target

        # we save data only when the file has been closed
        if method == core.SAVE_DATA:
            # and when it's not the entire directory
            if action == "CLOSED" and (not mask & core.IN_ISDIR):
                execute_action("HONEYFILE", method, ppid, user, filename)
        else:
            execute_action("HONEYFILE", method, ppid, user, filename)
        end = time.time()
        elapsed_time = end - start
        log.detail_write(tool_id, core.EXTERNAL, elapsed_time)
    return
