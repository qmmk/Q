# import log
# import connection
# import bwlist


import socket
from datetime import datetime
# from google.cloud import logging
import os.path

from core import bwlist, log


def translate_severity(lv):
    if lv == Core.DEBUG:
        return "DEBUG"
    if lv == Core.ERROR:
        return "ERROR"
    if lv == Core.INFO:
        return "INFO"
    if lv == Core.CRITICAL:
        return "CRITICAL"
    if lv == Core.WARNING:
        return "WARNING"
    return "DEFAULT"


class Core:
    # Google Cloud Logging-----------
    """
    google_logs = False
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "./adarch_persistent/adarchloggerkey.json"
    logging_client = logging.Client()
    logger = logging_client.logger('adarch-log')
    """

    # <editor-fold desc="FIELD">

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

    # Log levels ---------------------
    DEBUG = 0
    INFO = 1
    WARNING = 2
    ERROR = 3
    CRITICAL = 4

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

    """
    def google_cloud_logging(self, lv, tool, s, hostname, ip, port):
        google_lv = translate_severity(lv)
        try:
            if ip is None and port is None:
                self.logger.log_struct({
                    'hostname': hostname,
                    'tool': tool,
                    'message': s}, severity=google_lv)
            else:
                self.logger.log_struct({
                    'hostname': hostname,
                    'ip': ip,
                    'port': port,
                    'tool': tool,
                    'message': s}, severity=google_lv)
        except:
            log(Core.DEBUG, "Could not send log to Google Cloud")
    """

    # <editor-fold desc="METHOD">

    def log(self, lv, tool, s):
        hostname = socket.gethostname()
        if self.ip is None and self.port is None:
            log.write(translate_severity(lv), "[{}]: {}: {}".format(hostname, tool, s))
        else:
            log.write(translate_severity(lv), "[{} {}:{}]: {}: {}".format(hostname, self.ip, self.port, tool, s))

        # if lv != self.DEBUG and self.google_logs:
        #     self.google_cloud_logging(lv, tool, s, hostname, self.ip, self.port)

    def shutdown(self):
        print("connection shutdown")
        return
        # connection.shutdown(self.sock, self.active_sock)

    def is_stopped(self):
        print("connection is stopped")
        return
        # if connection.is_stopped(self.sock, self.active_sock) == 1:
        #    return True
        # else:
        #    return False

    def send(self, s):
        x = s.encode('utf-8')
        try:
            print("connection send")
            # connection.send(self.sock, self.active_sock, x, len(x))
        except TypeError:
            print('TypeError:\n\t{}\t{}'.format(x, type(x)))

    @staticmethod
    def add_to_blacklist(ip_address):
        bwlist.add(bwlist.BLACKLIST, ip_address.encode('utf-8'))

    @staticmethod
    def add_to_whitelist(ip_address):
        bwlist.add(bwlist.WHITELIST, ip_address.encode('utf-8'))

    @staticmethod
    def is_blacklisted(ip_address):
        if bwlist.exists(bwlist.BLACKLIST, ip_address.encode('utf-8')):
            return True
        return False

    @staticmethod
    def is_whitelisted(ip_address):
        if bwlist.exists(bwlist.WHITELIST, ip_address.encode('utf-8')):
            return True
        return False

    # </editor-fold>
