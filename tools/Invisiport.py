import threading
from services import bwlist
from services.utils import *

PORTS = [21, 80, 445]


class Invisiport(Core):
    # The ports to show up to the attacker after he triggered the defenses by connecting to port specified in config

    # As soon as Invisiport detects a connection, it then drops connections to all listening ports except to 'port'.
    # Essentially, when an attacker triggers Invisiport, all he sees is 'port' and Invisiport ports.
    # The legitimate ports are no more visible.
    # ...what the attacker is going to think after seeing different profiles before and after a scan?

    # sock, port, active_sock, ip, malicious_ip
    def __init__(self):
        super().__init__()

    async def run(self, writer, port, malicious_ip, msg, mode):
        mode = Core.WAIT if mode == "delayed_action" else Core.IMMEDIATE
        log.sintetic_write(log.WARNING, "INVISIPORT",
                           "detectected activity by the following IP: {} - content: {}".format(malicious_ip, msg))
        writer.write("Protocol mismatch.\n".encode(Core.FORMAT))
        writer.close()

        print("Conn lost:", writer.transport._conn_lost)

        if mode == Core.WAIT:
            if not bwlist.is_whitelisted(malicious_ip) and not bwlist.is_blacklisted(malicious_ip):
                log.sintetic_write(log.INFO, "INVISIPORT",
                                   "waiting 180 seconds before blacklisting..".format(malicious_ip))
                event = threading.Event()
                event.wait(180)

        # function act()
        if not bwlist.is_whitelisted(malicious_ip) and not bwlist.is_blacklisted(malicious_ip):
            bwlist.add_to_blacklist(malicious_ip.encode(Core.FORMAT))
            log.sintetic_write(log.INFO, "INVISIPORT", "blacklisted the following IP: {}".format(malicious_ip))
            try:
                subprocess.check_output("iptables -A ADARCH_EXCEPTION -s {} -p tcp --destination-port {} -j ACCEPT"
                                        .format(malicious_ip, port), shell=True)
            except subprocess.CalledProcessError as e:
                print(e)
            log.sintetic_write(log.INFO, "INVISIPORT", "added 'exception rule': allow {} for dst_port {}"
                               .format(malicious_ip, port))

            for _p in PORTS:
                try:
                    subprocess.check_output("iptables -t nat -A ADARCH -s {} -p tcp --dport {} -j "
                                            "REDIRECT --to-port {} -m comment --comment \"{}\""
                                            .format(malicious_ip, _p, port, "added by INVISIPORT"), shell=True)
                except subprocess.CalledProcessError as e:
                    print(e)
                log.sintetic_write(log.INFO, "INVISIPORT", "added 'prerouting rule' for {}".format(malicious_ip))
        return
