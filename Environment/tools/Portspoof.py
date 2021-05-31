from Environment.services.utils import *
from Environment.tools.rstr import xeger


class Signature:
    def __init__(self, filename, port):
        self.__signature = ''
        raw_signatures = []
        try:
            with open(filename, "r") as f:
                raw_signatures = f.readlines()
            if len(raw_signatures) > 0:
                # print(raw_signatures[self.__port_to_signature(port, len(raw_signatures))])
                # print(xeger(raw_signatures[self.__port_to_signature(port, len(raw_signatures))]))
                self.__signature = xeger(raw_signatures[self.__port_to_signature(port, len(raw_signatures))])
                # print(len(raw_signatures))
            t = self.__signature.encode('utf-8')
        except (IOError, OSError, ValueError) as ex:
            self.__signature = ''
        finally:
            del raw_signatures

    def __port_to_signature(self, key, signatures):
        # Robert Jenkins' 32 bit Mix Function
        key += (key << 12)
        key ^= (key >> 22)
        key += (key << 4)
        key ^= (key >> 9)
        key += (key << 10)
        key ^= (key >> 2)
        key += (key << 7)
        key ^= (key >> 12)

        # Knuth's Multiplicative Method
        key = (key >> 3) * 2654435761
        return key % signatures

    def get_signature(self):
        return self.__signature


def run_portspoof(writer, port, malicious_ip, msg, tool_id):
    start = time.time()
    sig = Signature(core.SIGNATURES, port)
    answer = sig.get_signature()
    del sig

    log.sintetic_write(core.WARNING, "PORTSPOOF",
                       "detected activity from IP {} - content: {}".format(malicious_ip, msg))
    try:
        writer.send(answer.encode(core.FORMAT))
        writer.shutdown(core.SHUT_RDWR)
        writer.close()
    except BrokenPipeError as e:
        print(e)

    end = time.time()
    elapsed_time = end - start
    log.detail_write(tool_id, core.DISCOVERY, elapsed_time)
    return
