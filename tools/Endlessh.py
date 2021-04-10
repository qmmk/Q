from Core import Core
from Utilities import *
import threading
import random
import time

def update_db(ip, port):
    with open("adarch_persistent/endlessh.db", "r+") as file:
        for line in file:
            x = line.split(";")
            if ip == x[0] and str(port) == x[1]:
                break
        else: # not found, we are at the eof
            file.write("{};{};\n".format(ip, port))


def is_first_time(ip, port):
    open("adarch_persistent/endlessh.db", 'a').close() # create file if it does not exist
    with open("adarch_persistent/endlessh.db", "r+") as file:
        for line in file:
            x = line.split(";")
            print(x, ip, port, ip == x[0], port == x[1])
            if ip == x[0] and str(port) == x[1]:

                print("have seen", ip, "on ", port)
                return False
        print("haven't seen", ip, "on ", port)
        return True


class Endlessh(Core):


    mode = Core.IMMEDIATE

    MSG = ""
    malicious_ip = ""
    port=-1

    def __init__(self, sock, port, active_sock, ip, malicious_ip):
        super().__init__(sock, port, active_sock, ip, malicious_ip)
        self.malicious_ip = malicious_ip
        self.port = port

    def start(self, msg):

        if msg[0:4]!= "SSH-":
            super().log(Core.WARNING, "ENDLESSH" , "detected activity from IP {} - content: {}".format(self.malicious_ip, msg))
            super().send("SSH-2.0-OpenSSH_7.9p1 Debian-10+deb10u2"+"\n")
            super().shutdown()
            if is_first_time(self.malicious_ip, self.port):
                update_db(self.malicious_ip, self.port) # remember that this IP had been already deceived..
        else:
            super().log(Core.WARNING, "ENDLESSH" , "detected SSH connection from IP {} - content: {}".format(self.malicious_ip, msg))

        delay = 1 # how many seconds before two consecutive garbage messages
        count = 0 # keep track of how many messages had been sent..

        start = time.time()
        event = threading.Event()

        while not super().is_stopped():

            if self.mode == Core.WAIT and count == 0 and is_first_time(self.malicious_ip, self.port): #make believable a port scan by sending just the first time this banner
                super().send("SSH-2.0-OpenSSH_7.9p1 Debian-10+deb10u2"+"\n")
                update_db(self.malicious_ip, self.port) # remember that this IP had been already deceived..
                super().log(Core.INFO, "ENDLESSH" , "Added IP {} for the port {} to endlessh.db".format(self.malicious_ip, self.port))
            else:
                super().send(str(hex(random.randint(1,10000))[2:])+"\n") # send garbage


            if super().is_stopped():
                break
            event.wait(delay) # wait before sending another message

            count = count + 1
            if count == 10: # after 10 messages, send a message every 5 seconds..
                delay = 5
            if count == 15: # after 15 messages, send a message every 10 seconds..
                delay = 10



        end = time.time()
        elapsed_time = end-start-delay
        super().log(Core.INFO, "ENDLESSH" , "IP {} stopped activity after {} seconds".format(self.malicious_ip, int(elapsed_time)))
        super().shutdown()

    def delayed_action(self, b):
        self.mode = Core.WAIT
        self.start(b)