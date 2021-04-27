from services.utils import *


class Dummyservice(Core):
    def __init__(self):
        super().__init__()

    async def run(self, writer, malicious_ip, msg):
        log.sintetic_write(log.INFO, "DUMMYSERVICE",
                           "detected activity from IP {} - content: {}".format(malicious_ip, msg))
        writer.write("Protocol error\n".encode(Core.FORMAT))
        writer.close()
