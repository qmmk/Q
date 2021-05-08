import os.path
from services.utils import *

N_TENTACTLES = 5
MAX_WORKERS = 5
DATABASE = "persistent/stealthcryptolocked.db"


def init_stealth_cryptolocked(paths):
    filenames = {}
    files = []
    # create a list of random filenames in the given paths
    for path in paths:
        if os.path.isdir(path):
            log.sintetic_write(log.DEBUG, "STEALTH CRYPTOLOCKED", "will monitor '{}'".format(path))
            for i in range(N_TENTACTLES):
                # while for no duplicate
                while True:
                    name = "." + str(hex(random.randint(1, 10000))[2:])
                    filename = path + '/' + name
                    if name not in filenames:
                        filenames[name] = filename
                        break
        else:
            log.sintetic_write(log.ERROR, "STEALTH CRYPTOLOCKED", "error, '{}' is not a directory".format(path))

    # DB initialization
    conn = create_connection(DATABASE)
    if conn is not None:
        create_table_files(conn)
    else:
        log.sintetic_write(log.ERROR, "STEALTH CRYPTOLOCKED", "error, cannot create the DB connection")

    # Clean previous trip files and DB
    cryptolocked_clean(conn)

    # Place trip files
    for name, filename in filenames.items():
        restore_file(filename)
        try:
            subprocess.check_output("auditctl -w {} -p war".format(filename), shell=True)
        except subprocess.CalledProcessError as e:
            log.sintetic_write(log.DEBUG, "STEALTH CRYPTOLOCKED", "auditctl error: {}".format(e.output))
        db_insert_file_entry(conn, filename)
        files.append(filename)

    log.sintetic_write(log.INFO, "STEALTH CRYPTOLOCKED", "finished initialization")
    return files


def run_stealth_cryptolocked(event, meth):
    (header, types, target, name) = event
    mask = header.mask

    action = get_action(mask)
    method = get_method(meth)

    if not (mask & Core.IN_ISDIR):
        if check_mask(mask):
            conn = create_connection(DATABASE)
            if conn is None:
                log.sintetic_write(log.ERROR, "STEALTH CRYPTOLOCKED", "error, cannot create the DB connection")

            filename = str(target + '/' + name)
            if is_in_file(conn, filename):
                audit_info, ppid, comm, user = check_audit(name)
                # TODO: check audit should look for path+name,
                #  but for unknown reasons sometimes it doesn't work by providing the entire path
                if method & Core.LOG_EVENT:
                    log.sintetic_write(log.CRITICAL, "STEALTH CRYPTOLOCKED", "file '{}/{}' has been {}! {}"
                                       .format(target, name, action, audit_info))
                # execute action only if the event was not caused by adarch itself
                if comm != "adarch":
                    execute_action("STEALTH CRYPTOLOCKED", method, ppid, user, filename)
    return

