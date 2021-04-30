from services import bwlist
from services.utils import *

MSG = "Connecting.."


class Honeyports(Core):
    def __init__(self):
        super().__init__()

    def run(self, writer, malicious_ip, msg):
        if MSG != "":
            try:
                writer.send(MSG.encode(Core.FORMAT))
            except BrokenPipeError as e:
                print(e)
        writer.shutdown(Core.SHUT_RDWR)
        writer.close()

        if not bwlist.is_whitelisted(malicious_ip):
            bwlist.add_to_blacklist(malicious_ip.encode(Core.FORMAT))  # TODO: the original version REJECTS instead of DROPPING
            log.sintetic_write(log.INFO, "HONEYPORTS", "IP {} has been blacklisted".format(malicious_ip))

        log.sintetic_write(log.WARNING, "HONEYPORTS",
                           "detected activity from IP {} - content: {}".format(malicious_ip, msg))
        return
