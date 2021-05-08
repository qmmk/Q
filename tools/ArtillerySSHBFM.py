from services.utils import *
from services import bwlist

ADMISSIBLE_ATTEMPTS = 10
MAX_WORKERS = 5
FILELOG = "/var/log/auth.log"


def run_artillery_sshbfm(event):
    (header, types, target, name) = event
    mask = header.mask

    if mask & Core.IN_MODIFY:

        failed_attempts = {}
        failed_attempts = defaultdict(lambda: 0, failed_attempts)

        if os.path.isfile(target):
            fileopen = open(FILELOG, "r")

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
                    if count >= ADMISSIBLE_ATTEMPTS:
                        if not bwlist.is_whitelisted(address) and not bwlist.is_blacklisted(address):
                            bwlist.add_to_blacklist(address.encode(Core.FORMAT))
                            log.sintetic_write(log.WARNING, "ARTILLERY [SSH BF monitor]",
                                               "noticed {} SSH brute force attempts from {}".format(count, address))
                            log.sintetic_write(log.INFO, "ARTILLERY [SSH BF monitor]",
                                               "IP {} has been blacklisted".format(address))

            except Exception as e:
                log.sintetic_write(log.ERROR, "ARTILLERY [SSH BF monitor]", "error {}".format(str(e)))
        else:
            log.sintetic_write(log.ERROR, "ARTILLERY [SSH BF monitor]",
                               "Can't open configuration file {}".format(FILELOG))
