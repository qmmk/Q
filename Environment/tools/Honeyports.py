from Environment.services import bwlist
from Environment.services.utils import *


def run_honeyports(writer, malicious_ip, msg):
    if core.MSG_honeyports != "":
        try:
            writer.send(core.MSG_honeyports.encode(core.FORMAT))
        except BrokenPipeError as e:
            print(e)
    writer.shutdown(core.SHUT_RDWR)
    writer.close()

    log.sintetic_write(core.WARNING, "HONEYPORTS",
                       "detected activity from IP {} - content: {}".format(malicious_ip, msg))

    if not bwlist.is_whitelisted(malicious_ip):
        # TODO: the original version REJECTS instead of DROPPING
        bwlist.add_to_blacklist(malicious_ip.encode(core.FORMAT))
        log.sintetic_write(core.INFO, "HONEYPORTS", "IP {} has been blacklisted".format(malicious_ip))
    return
