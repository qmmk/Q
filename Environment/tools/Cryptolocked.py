import ntpath
import os.path
from Environment.services.utils import *


def init_cryptolocked(paths):
    filenames = {}
    files = []

    # create a list of random filenames in the given paths
    for path in paths:
        if os.path.isdir(path):
            log.sintetic_write(core.DEBUG, "CRYPTOLOCKED", "will monitor '{}'".format(path))
            for i in range(core.N_TENTACTLES):
                # why while loop? we do not want to have duplicates in dict, so if duplicate do it again
                while True:
                    name = str(hex(random.randint(1, 10000))[2:])
                    filename = path + '/' + name
                    if name not in filenames:
                        filenames[name] = filename
                        break
        else:
            log.sintetic_write(core.ERROR, "CRYPTOLOCKED", "error, '{}' is not a directory".format(path))

    # DB initialization
    conn = create_connection(core.DB_Cryptolocked)
    if conn is not None:
        create_table_files(conn)
    else:
        log.sintetic_write(core.ERROR, "CRYPTOLOCKED", "error, cannot create the DB connection")

    # Clean previous trip files and DB
    cryptolocked_clean(conn)

    # Place trip files
    for name, filename in filenames.items():
        restore_file(filename)
        try:
            subprocess.check_output("auditctl -w {} -p war".format(filename), shell=True)
        except subprocess.CalledProcessError as e:
            log.sintetic_write(core.DEBUG, "CRYPTOLOCKED", "auditctl error: {}".format(e.output))
        db_insert_file_entry(conn, filename)
        files.append(filename)
    log.sintetic_write(core.INFO, "CRYPTOLOCKED", "finished initialization")
    return files


def run_cryptolocked(event, meth):
    (header, types, target, name) = event
    mask = header.mask

    action = get_action(mask)
    method = get_method(meth)

    if not (mask & core.IN_ISDIR):
        if check_mask(mask):
            conn = create_connection(core.DB_Cryptolocked)
            if conn is None:
                log.sintetic_write(core.ERROR, "CRYPTOLOCKED", "error, cannot create the DB connection")

            if len(name) == 0:
                _, name = ntpath.split(target)

            if is_in_file(conn, target):
                audit_info, ppid, comm, user = check_audit(target)
                # TODO: check audit should look for path+name, but for unknown reasons sometimes
                #  it doesn't work by providing the entire path

                if method & core.LOG_EVENT:
                    log.sintetic_write(core.CRITICAL, "CRYPTOLOCKED", "file '{}' has been {}! {}"
                                       .format(target, action, audit_info))
                # execute action only if the event was not caused by adarch itself
                if comm != "adarch":
                    execute_action("CRYPTOLOCKED", method, ppid, user, target)
    return
