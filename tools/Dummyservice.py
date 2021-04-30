from services.utils import *

MSG = "Protocol error.\n"


class Dummyservice(Core):
    def __init__(self):
        super().__init__()

    def run(self, writer, malicious_ip, msg):
        log.sintetic_write(log.INFO, "DUMMYSERVICE",
                           "detected activity from IP {} - content: {}".format(malicious_ip, msg))
        writer.write(MSG.encode(Core.FORMAT))
        writer.shutdown(Core.SHUT_RDWR)
        writer.close()
