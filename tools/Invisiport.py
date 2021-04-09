from Core import Core
from Utilities import *
import subprocess
import threading




class Invisiport(Core):


    IMMEDIATE = 0
    WAIT = 1
    action = IMMEDIATE

    malicious_ip = ""
    port = -1

    # The ports to show up to the attacker after he triggered the defenses by connecting to port specified in config
    PORTS = [21, 80, 445]

    # As soon as Invisiport detects a connection, it then drops connections to all listening ports except to 'port'.
    # Essentially, when an attacker triggers Invisiport, all he sees is 'port' and Invisiport ports.
    # The legitimate ports are no more visible.
    # ...what the attacker is going to think after seeing different profiles before and after a scan?


    def __init__(self, sock, port, active_sock, ip, malicious_ip):

        super().__init__(sock, port, active_sock, ip, malicious_ip)
        self.malicious_ip = malicious_ip
        self.port = port


    def act(self):

        if not super().is_whitelisted(self.malicious_ip) and not super().is_blacklisted(self.malicious_ip):

            super().add_to_blacklist(self.malicious_ip)
            super().log(Core.INFO, "INVISIPORT" , "blacklisted the following IP: {}".format(self.malicious_ip))

            subprocess.check_output("iptables -A ADARCH_EXCEPTION -s {} -p tcp --destination-port {} -j ACCEPT"
                                    .format(self.malicious_ip, self.port), shell=True)
            super().log(Core.INFO, "INVISIPORT" , "added 'exception rule': allow {} for dst_port {}"
                        .format(self.malicious_ip, self.port))

            for _PORT in self.PORTS:
                subprocess.check_output(
                    "iptables -t nat -A ADARCH -s {} -p tcp --dport {} -j REDIRECT --to-port {} -m comment --comment \"{}\"".
                        format(self.malicious_ip, _PORT, self.port, "added by INVISIPORT"), shell=True)
                super().log(Core.INFO, "INVISIPORT" , "added 'prerouting rule' for {}".format(self.malicious_ip))


    def start(self, b):
        super().log(Core.WARNING, "INVISIPORT" , "detectected activity by the following IP: {} - content: ".format(self.malicious_ip, b))
        super().send("Protocol mismatch.\n")
        super().shutdown()
        if self.action == self.WAIT:
            if not super().is_whitelisted(self.malicious_ip) and not super().is_blacklisted(self.malicious_ip):
                super().log(Core.INFO, "INVISIPORT" , "waiting 180 seconds before blacklisting..".format(self.malicious_ip))
                event = threading.Event()
                event.wait(180)
        self.act()

    def immediate_action(self, b):
        self.action = self.IMMEDIATE
        self.start(b)

    def delayed_action(self, b):
        self.action = self.WAIT
        self.start(b)
