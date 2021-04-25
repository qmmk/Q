from datetime import datetime
import socket

LOG_FILE = "persistent/log.txt"

# Log levels ---------------------
DEBUG = 0
INFO = 1
WARNING = 2
ERROR = 3
CRITICAL = 4


def translate_severity(lv):
    if lv == DEBUG:
        return "DEBUG"
    if lv == ERROR:
        return "ERROR"
    if lv == INFO:
        return "INFO"
    if lv == CRITICAL:
        return "CRITICAL"
    if lv == WARNING:
        return "WARNING"
    return "DEFAULT"


def sintetic_write(lv, tool, s):
    hostname = socket.gethostname()
    log = "{0} - [{1}] :: [{2}]: {3}: {4}\n".format(datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
                                                    translate_severity(lv), hostname, tool, s)
    print(log.strip("\n"))
    try:
        with open(LOG_FILE, "a") as f:
            f.write(log)
    except FileNotFoundError as e:
        print(e)
    return


def detail_write(lv, ip, port, tool, s):
    hostname = socket.gethostname()
    log = "{0} - [{1}] :: [{2} {3}:{4}]: {5}: {6}\n".format(datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
                                                            translate_severity(lv), hostname, ip, port, tool, s)
    print(log.strip("\n"))
    try:
        with open(LOG_FILE, "a") as f:
            f.write(log)
    except FileNotFoundError as e:
        print(e)
    return


def destroy():
    return


# from google.cloud import logging
# Google Cloud Logging  -----------
"""

google_logs = False
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "./adarch_persistent/adarchloggerkey.json"
logging_client = logging.Client()
logger = logging_client.logger('adarch-log')

        # if lv != self.DEBUG and self.google_logs:
        #     self.google_cloud_logging(lv, tool, s, hostname, self.ip, self.port)

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
