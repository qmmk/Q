from Core import *
from Utilities import *
import os
import re
from collections import defaultdict

ADMISSIBLE_ATTEMPTS = 10

class ArtillerySSHBFM(Core):


	def __init__(self, paths):
		super().__init__(paths)

	def initialization(self, paths):
		pass

	def check_log(self, target):
		failed_attempts = {}
		failed_attempts = defaultdict(lambda:0,failed_attempts)

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
						failed_attempts[ipaddress] = failed_attempts[ipaddress]+1

			for address, count in failed_attempts.items():
				#print("{} attempted {} times in total".format(address, count))
				if count >= ADMISSIBLE_ATTEMPTS:
					if not super().is_whitelisted(address) and not super().is_blacklisted(address):
						super().add_to_blacklist(address)
						super().log(Core.WARNING, "ARTILLERY [SSH BF monitor]" , "noticed {} SSH brute force attempts from {}".format(count, address))
						super().log(Core.INFO, "ARTILLERY [SSH BF monitor]" , "IP {} has been blacklisted".format(address))

		except Exception as e:
			super().log(super().ERROR, "ARTILLERY [SSH BF monitor]" , "error {}".format(str(e)))


	def start(self, mask, name, target):
		#print("Method has been called because of mask: 0x{:8X}".format(mask), name)
		if mask & Core.IN_MODIFY:
			self.check_log(target)