from random import randint
from Environment.services.utils import *


def run_tcprooter(writer, malicious_ip, msg):
    log.sintetic_write(core.WARNING, "TCPROOTER",
                       "detected activity from IP {} - content: {}".format(malicious_ip, msg))

    # Random version
    writer.write(core.PAYLOADS[randint(0, len(core.PAYLOADS) - 1)].encode(core.FORMAT))

    # Static version
    # writer.write(Tcprooter.PAYLOADS[1].encode(Core.FORMAT))

    writer.shutdown(core.SHUT_RDWR)
    writer.close()
    return
