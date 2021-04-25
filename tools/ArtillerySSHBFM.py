from services.core import *
from services.utils import *
import os
import re
from collections import defaultdict
import concurrent.futures
import inotify.adapters
import inotify.constants
from services.core import *
from services.utils import *

ADMISSIBLE_ATTEMPTS = 10
MAX_WORKERS = 5


class ArtillerySSHBFM(Core):
    def __init__(self, tool):
        super().__init__()
        self.paths = tool.attr

    def run(self, loop, shared):
        with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            try:
                i = inotify.adapters.Inotify()
                for filename in self.paths:
                    wd = i.add_watch(filename)
                    if wd == -1:
                        log.sintetic_write(log.INFO, "ARTILLERY [SSH BF monitor]", "Couldn't add watch to {0}".format(filename))
                    else:
                        log.sintetic_write(log.INFO, "ARTILLERY [SSH BF monitor]",
                                           "Added inotify watch to: {0}, value: {1}".format(filename, wd))

                for event in i.event_gen():
                    if event is not None:
                        loop.run_in_executor(executor, self.process(event))
            finally:
                time.sleep(1)

    def process(self, event):
        (header, types, target, name) = event
        mask = header.mask

        if mask & Core.IN_MODIFY:

            failed_attempts = {}
            failed_attempts = defaultdict(lambda: 0, failed_attempts)

            if os.path.isfile(target):
                fileopen = open(target, "r")

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
