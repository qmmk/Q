from Core import Core
from Utilities import *
from rstr import xeger
import gc


class Portspoof(Core):
    class Signature:
        def __init__(self, filename, port):
            self.__signature = ''
            raw_signatures = []
            try:
                with open(filename, "r") as f:
                    raw_signatures = f.readlines()
                if len(raw_signatures) > 0:
                    #print(raw_signatures[self.__port_to_signature(port, len(raw_signatures))])
                    #print(xeger(raw_signatures[self.__port_to_signature(port, len(raw_signatures))]))
                    self.__signature = xeger(raw_signatures[self.__port_to_signature(port, len(raw_signatures))])
                    #print(len(raw_signatures))
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

    malicious_ip = ""

    def __init__(self, sock, port, active_sock, ip, malicious_ip):
        super().__init__(sock, port, active_sock, ip, malicious_ip)
        self.malicious_ip = malicious_ip
        self._sig = Portspoof.Signature('portspoof_signatures', port)
        self.answer = self._sig.get_signature()
        del self._sig

    def start(self, b):
        super().log(Core.WARNING, "PORTSPOOF" , "detected activity from IP {} - content: {}".format(self.malicious_ip, b))
        super().send(self.answer)
        super().shutdown()