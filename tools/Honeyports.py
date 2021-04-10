from Core import Core
from Utilities import *


class Honeyports(Core):

	MSG = ""
	malicious_ip = ""


	def __init__(self, sock, port, active_sock, ip, malicious_ip):
		super().__init__(sock, port, active_sock, ip, malicious_ip)
		self.malicious_ip = malicious_ip
		self.__blacklist(ip, malicious_ip)

	def __blacklist(self, ip, malicious_ip):
		if Honeyports.MSG != "":
			super().send(Honeyports.MSG)
		super().shutdown()

		if not super().is_whitelisted(malicious_ip):
			super().add_to_blacklist(malicious_ip) #TODO: the original version REJECTS instead of DROPPING
			super().log(Core.INFO, "HONEYPORTS" , "IP {} has been blacklisted".format(malicious_ip))

	def start(self, b):
		super().log(Core.WARNING, "HONEYPORTS" , "detected activity from IP {} - content: {}".format(self.malicious_ip, b))
		super().shutdown()