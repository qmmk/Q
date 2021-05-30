
import socket
import psutil
from datetime import datetime
from Environment.services import core


def translate_severity(lv):
    if lv == core.DEBUG:
        return "DEBUG"
    if lv == core.ERROR:
        return "ERROR"
    if lv == core.INFO:
        return "INFO"
    if lv == core.CRITICAL:
        return "CRITICAL"
    if lv == core.WARNING:
        return "WARNING"
    return "DEFAULT"


def sintetic_write(lv, tool, s):
    hostname = socket.gethostname()
    log = "{0} - [{1}] :: [{2}]: {3}: {4}\n".format(datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
                                                    translate_severity(lv), hostname, tool, s)
    print(log.strip("\n"))
    try:
        with open(core.LOG_FILE, "a") as f:
            f.write(log)
    except FileNotFoundError as e:
        print(e)
    return


def detail_write(tool_id, lv, t_exec):
    # CSV format --> DATE, TOOL ID, STATUS, SEC LVL, RES. USAGE, T.EXEC
    info = "{0},{1},{2},{3},{4},{5}\n".format(
        datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
        tool_id,
        0,
        lv,
        psutil.getloadavg()[0],
        t_exec)
    try:
        with open(core.CSV_FILE, "a") as f:
            f.write(info)
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
