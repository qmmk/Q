import threading
from Environment.services import bwlist
from Environment.services.utils import *


# The ports to show up to the attacker after he triggered the defenses by connecting to port specified in config

# As soon as Invisiport detects a connection, it then drops connections to all listening ports except to 'port'.
# Essentially, when an attacker triggers Invisiport, all he sees is 'port' and Invisiport ports.
# The legitimate ports are no more visible.
# ...what the attacker is going to think after seeing different profiles before and after a scan?

# sock, port, active_sock, ip, malicious_ip


def run_invisiport(writer, port, malicious_ip, msg, mode):
    mode = core.WAIT if mode == "delayed_action" else core.IMMEDIATE
    log.sintetic_write(core.WARNING, "INVISIPORT",
                       "detectected activity by the following IP: {} - content: {}".format(malicious_ip, msg))
    try:
        writer.send(core.MSG_inviports.encode(core.FORMAT))
        writer.shutdown(core.SHUT_RDWR)
        writer.close()
    except BrokenPipeError as e:
        print(e)

    if mode == core.WAIT:
        if not bwlist.is_whitelisted(malicious_ip) and not bwlist.is_blacklisted(malicious_ip):
            log.sintetic_write(core.INFO, "INVISIPORT",
                               "waiting 180 seconds before blacklisting..".format(malicious_ip))
            event = threading.Event()
            event.wait(180)

    # function act()
    if not bwlist.is_whitelisted(malicious_ip) and not bwlist.is_blacklisted(malicious_ip):
        bwlist.add_to_blacklist(malicious_ip.encode(core.FORMAT))
        log.sintetic_write(core.INFO, "INVISIPORT", "blacklisted the following IP: {}".format(malicious_ip))
        try:
            subprocess.check_output("iptables -A ADARCH_EXCEPTION -s {} -p tcp --destination-port {} -j ACCEPT"
                                    .format(malicious_ip, port), shell=True)
        except subprocess.CalledProcessError as e:
            print(e)
        log.sintetic_write(core.INFO, "INVISIPORT", "added 'exception rule': allow {} for dst_port {}"
                           .format(malicious_ip, port))

        for _p in core.PORTS:
            try:
                subprocess.check_output("iptables -t nat -A ADARCH -s {} -p tcp --dport {} -j "
                                        "REDIRECT --to-port {} -m comment --comment \"{}\""
                                        .format(malicious_ip, _p, port, "added by INVISIPORT"), shell=True)
            except subprocess.CalledProcessError as e:
                print(e)
            log.sintetic_write(core.INFO, "INVISIPORT", "added 'prerouting rule' for {}".format(malicious_ip))
    return
