# import log
# import connection
# import bwlist


import socket
from datetime import datetime

import os.path

from services import bwlist, log


class Core:


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

    IMMEDIATE = 0
    WAIT = 1

    # </editor-fold>

    def __init__(self, sock=None, port=None, active_sock=None, ip=None, malicious_ip=None, data=None):
        self.__sock = -1
        self.__port = -1
        self.__active_sock = -1
        self.__ip = ''
        self.__malicious_ip = ''
        self.__data = []
        self.sock = sock
        self.port = port
        self.active_sock = active_sock
        self.ip = ip
        self.malicious_ip = malicious_ip
        self.data = data

    # <editor-fold desc="PROPERTY">

    @property
    def sock(self):
        return self.__sock

    @property
    def port(self):
        return self.__port

    @property
    def active_sock(self):
        return self.__active_sock

    @property
    def ip(self):
        return self.__ip

    @property
    def malicious_ip(self):
        return self.__malicious_ip

    @sock.setter
    def sock(self, val):
        if self.__sock < 0:
            self.__sock = val

    @port.setter
    def port(self, val):
        if self.__port < 0:
            self.__port = val

    @active_sock.setter
    def active_sock(self, val):
        if self.__active_sock < 0:
            self.__active_sock = val

    @ip.setter
    def ip(self, val):
        if self.__ip == '':
            self.__ip = val

    @malicious_ip.setter
    def malicious_ip(self, val):
        if self.__malicious_ip == '':
            self.__malicious_ip = val

    @property
    def data(self):
        return self.__data

    @data.setter
    def data(self, val):
        if not self.__data:
            self.__data = val

    # </editor-fold>
