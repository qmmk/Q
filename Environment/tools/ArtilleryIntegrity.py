from Environment.services.utils import *
from os import listdir
from os.path import isfile, join


def init_artillery_integrity(paths):
    # DB initialization
    files = []
    conn = create_connection(core.DB_Artillery)
    if conn is not None:
        create_table_files(conn)
    else:
        log.sintetic_write(core.ERROR, "ARTILLERY INTEGRITY", "error, cannot create the DB connection")

    # Clean previous associations and DB
    artillery_clean(conn)

    # Create digests for each file in path
    for path in paths:
        if os.path.isdir(path):
            log.sintetic_write(core.INFO, "ARTILLERY INTEGRITY", "will monitor '{}'".format(path))
            onlyfiles = [f for f in listdir(path) if isfile(join(path, f))]
            for name in onlyfiles:
                filename = path + '/' + name
                try:
                    subprocess.check_output("auditctl -w {} -p wa".format(filename), shell=True)
                except subprocess.CalledProcessError as e:
                    log.sintetic_write(core.DEBUG, "ARTILLERY INTEGRITY",
                                       "auditctl error: {} for '{}'".format(e.output, name))
                db_insert_file_entry(conn, filename)
                files.append(filename)
        else:
            log.sintetic_write(core.ERROR, "ARTILLERY INTEGRITY", "error, '{}' is not a directory".format(path))
    log.sintetic_write(core.INFO, "ARTILLERY INTEGRITY", "finished initialization")
    return files


def run_artillery_integrity(event, meth, tool_id):
    start = time.time()
    (header, types, target, name) = event
    mask = header.mask

    if not (mask & core.IN_ISDIR):
        if check_mask(mask):
            conn = create_connection(core.DB_Artillery)
            if conn is None:
                log.sintetic_write(core.ERROR, "ARTILLERY INTEGRITY", "error, cannot create the DB connection")

            filename = target + '/' + name
            method = get_method(meth)

            if is_in_file(conn, filename):
                action = get_action(mask)

                audit_info, ppid, comm, user = check_audit(name)
                # TODO: check audit should look for path+name, but for unknown reasons sometimes it doesn't work
                #  by providing the entire path

                if comm != "adarch":  # execute action only if the event was not caused by adarch itself
                    log.sintetic_write(core.CRITICAL, "ARTILLERY INTEGRITY",
                                       "file '{}/{}' has been {}! {}".format(target, name, action, audit_info))
                    execute_action("ARTILLERY INTEGRITY", method, ppid, user, filename)
                    end = time.time()
                    elapsed_time = end - start
                    log.detail_write(tool_id, core.INTRUSIVE, elapsed_time)

            if mask & core.IN_CREATE:
                audit_info, ppid = check_audit(name)  # TODO: same as above
                log.sintetic_write(core.CRITICAL, "ARTILLERY INTEGRITY",
                                   "file '{}/{}' has been CREATED! {}".format(target, name, audit_info))
                # TODO: da verificare che azione effettuava
                # self.execute_action(ppid, filename)
                execute_action("ARTILLERY INTEGRITY", method, ppid, None, filename)
                end = time.time()
                elapsed_time = end - start
                log.detail_write(tool_id, core.INTRUSIVE, elapsed_time)
    return
