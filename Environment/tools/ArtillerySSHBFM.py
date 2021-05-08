from Environment.services.utils import *
from Environment.services import bwlist


def run_artillery_sshbfm(event):
    (header, types, target, name) = event
    mask = header.mask

    if mask & core.IN_MODIFY:

        failed_attempts = {}
        failed_attempts = defaultdict(lambda: 0, failed_attempts)

        if os.path.isfile(target):
            fileopen = open(core.FILELOG, "r")

            try:
                for line in fileopen:
                    line = line.rstrip()
                    match = re.search("Failed password for", line)

                    if match:
                        line = line.split(" ")
                        ipaddress = line[-4]

                        if is_valid_ipv4(ipaddress):
                            failed_attempts[ipaddress] = failed_attempts[ipaddress] + 1

                for address, count in failed_attempts.items():
                    # print("{} attempted {} times in total".format(address, count))
                    if count >= core.ADMISSIBLE_ATTEMPTS:
                        if not bwlist.is_whitelisted(address) and not bwlist.is_blacklisted(address):
                            bwlist.add_to_blacklist(address.encode(core.FORMAT))
                            log.sintetic_write(core.WARNING, "ARTILLERY [SSH BF monitor]",
                                               "noticed {} SSH brute force attempts from {}".format(count, address))
                            log.sintetic_write(core.INFO, "ARTILLERY [SSH BF monitor]",
                                               "IP {} has been blacklisted".format(address))

            except Exception as e:
                log.sintetic_write(core.ERROR, "ARTILLERY [SSH BF monitor]", "error {}".format(str(e)))
        else:
            log.sintetic_write(core.ERROR, "ARTILLERY [SSH BF monitor]",
                               "Can't open configuration file {}".format(core.FILELOG))
    return
