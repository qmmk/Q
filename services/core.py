class Core:
    def __init__(self):
        pass

    # <editor-fold desc="FIELD">
    FORMAT = 'utf-8'

    # Inotify masks ------------------
    IN_ACCESS = 0x00000001  # File was accessed
    IN_MODIFY = 0x00000002  # File was modified
    IN_ATTRIB = 0x00000004  # Metadata changed
    IN_CLOSE_WRITE = 0x00000008  # Writtable file was closed
    IN_CLOSE_NOWRITE = 0x00000010  # Unwrittable file closed
    IN_OPEN = 0x00000020  # File was opened
    IN_MOVED_FROM = 0x00000040  # File was moved from X
    IN_MOVED_TO = 0x00000080  # File was moved to Y
    IN_CREATE = 0x00000100  # Subfile was created
    IN_DELETE = 0x00000200  # Subfile was deleted
    IN_DELETE_SELF = 0x00000400  # Self was deleted
    IN_ISDIR = 0x40000000  # event occurred against dir
    IN_MOVE = IN_MOVED_FROM | IN_MOVED_TO
    IN_CLOSE = IN_CLOSE_WRITE | IN_CLOSE_NOWRITE

    # Actions masks ------------------
    LOG_EVENT = 0x00000001  # log the event
    SAVE_DATA = 0x00000002  # save to /var/adarch the file which called the event
    KILL_PID = 0x00000004  # kill the pid that generated the event
    KILL_USER = 0x00000008  # kill the user that generated the event
    LOCK_USER = 0x00000010  # lock the user account
    SHUTDOWN_HOST = 0x00000020  # shutdown host

    # Active mode ----------------------
    IMMEDIATE = 0
    WAIT = 1

    # Socket shutdown mode -----------------
    SHUT_RD = 0
    SHUT_WR = 1
    SHUT_RDWR = 2

    # </editor-fold>
