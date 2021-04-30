from services.utils import *
from tools.rstr import xeger

SIGNATURES = "persistent/portspoof_signatures"


class Portspoof(Core):
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

    def __init__(self, port):
        super().__init__()
        self._sig = Portspoof.Signature(SIGNATURES, port)
        self.answer = self._sig.get_signature()
        del self._sig

    def run(self, writer, malicious_ip, msg):
        log.sintetic_write(log.WARNING, "PORTSPOOF",
                           "detected activity from IP {} - content: {}".format(malicious_ip, msg))
        writer.send(self.answer.encode(Core.FORMAT))
        writer.shutdown(Core.SHUT_RDWR)
        writer.close()
