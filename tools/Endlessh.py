import threading
from services.utils import *

DATABASE = "persistent/endlessh.db"
MSG = "SSH-2.0-OpenSSH_7.9p1 Debian-10+deb10u2" + "\n"


class Endlessh(Core):
    def __init__(self):
        super().__init__()

    async def run(self, writer, port, malicious_ip, msg, mode):
        mode = Core.WAIT if mode == "delayed_action" else Core.IMMEDIATE
        if msg[0:4] != "SSH-":
            log.sintetic_write(log.WARNING, "ENDLESSH",
                               "detected activity from IP {} - content: {}".format(malicious_ip, msg))
            writer.write(MSG.encode(Core.FORMAT))
            writer.close()

            if is_first_time(DATABASE, malicious_ip, port):
                # remember that this IP had been already deceived..
                update_db(DATABASE, malicious_ip, port)
        else:
            log.sintetic_write(log.WARNING, "ENDLESSH",
                               "detected SSH connection from IP {} - content: {}".format(malicious_ip, msg))

        delay = 1  # how many seconds before two consecutive garbage messages
        count = 0  # keep track of how many messages had been sent..

        start = time.time()
        event = threading.Event()

        while not writer.is_closing():
            # make believable a port scan by sending just the first time this banner
            if mode == Core.WAIT and count == 0 and is_first_time(DATABASE, malicious_ip, port):
                writer.write(MSG.encode(Core.FORMAT))
                # remember that this IP had been already deceived..
                update_db(DATABASE, malicious_ip, port)
                log.sintetic_write(log.INFO, "ENDLESSH",
                                   "Added IP {} for the port {} to endlessh.db".format(malicious_ip, port))
            else:
                garbage = str(hex(random.randint(1, 10000))[2:]) + "\n"
                writer.write(garbage.encode(Core.FORMAT))

            if writer.is_closing():
                break
            event.wait(delay)  # wait before sending another message

            count = count + 1
            if count == 10:  # after 10 messages, send a message every 5 seconds..
                delay = 5
            if count == 15:  # after 15 messages, send a message every 10 seconds..
                delay = 10

        end = time.time()
        elapsed_time = end - start - delay
        log.sintetic_write(log.INFO, "ENDLESSH",
                           "IP {} stopped activity after {} seconds".format(malicious_ip, int(elapsed_time)))
        writer.close()
        return
