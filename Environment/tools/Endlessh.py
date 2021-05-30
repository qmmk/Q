import threading
from Environment.services.utils import *


def run_endlessh(writer, port, malicious_ip, msg, tool):
    start = time.time()
    is_closing = False
    mode = core.WAIT if tool.method == "delayed_action" else core.IMMEDIATE
    if msg[0:4] != "SSH-":
        log.sintetic_write(core.WARNING, "ENDLESSH",
                           "detected activity from IP {} - content: {}".format(malicious_ip, msg))
        try:
            writer.send(core.MSG_endlessh.encode(core.FORMAT))
            writer.shutdown(core.SHUT_RDWR)
            writer.close()
            is_closing = True
        except BrokenPipeError as e:
            print(e)

        if is_first_time(core.DB_Endlessh, malicious_ip, port):
            # remember that this IP had been already deceived..
            update_db(core.DB_Endlessh, malicious_ip, port)
        return
    else:
        log.sintetic_write(core.WARNING, "ENDLESSH",
                           "detected SSH connection from IP {} - content: {}".format(malicious_ip, msg))

    delay = 1  # how many seconds before two consecutive garbage messages
    count = 0  # keep track of how many messages had been sent..
    event = threading.Event()

    while not is_closing:
        # make believable a port scan by sending just the first time this banner
        if mode == core.WAIT and count == 0 and is_first_time(core.DB_Endlessh, malicious_ip, port):
            try:
                writer.send(core.MSG_endlessh.encode(core.FORMAT))
            except BrokenPipeError as e:
                is_closing = True
                print(e)
            # remember that this IP had been already deceived..
            update_db(core.DB_Endlessh, malicious_ip, port)
            log.sintetic_write(core.INFO, "ENDLESSH",
                               "Added IP {} for the port {} to endlessh.db".format(malicious_ip, port))
        else:
            garbage = str(hex(random.randint(1, 10000))[2:]) + "\n"
            try:
                writer.send(garbage.encode(core.FORMAT))
            except BrokenPipeError as e:
                is_closing = True
                print(e)

        if is_closing:
            writer.close()
            break

        event.wait(delay)  # wait before sending another message

        count = count + 1
        if count == 10:  # after 10 messages, send a message every 5 seconds..
            delay = 5
        if count == 15:  # after 15 messages, send a message every 10 seconds..
            delay = 10

    end = time.time()
    elapsed_time = end - start - delay
    log.sintetic_write(core.INFO, "ENDLESSH",
                       "IP {} stopped activity after {} seconds".format(malicious_ip, int(elapsed_time)))
    log.detail_write(tool.id, core.BRUTE, elapsed_time)
    return
