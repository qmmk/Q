from services.utils import *


class Dummyservice(Core):

	MSG = ""
	#malicious_ip = ""

	def __init__(self, sock, port, active_sock, ip, malicious_ip):
		super().__init__(sock, port, active_sock, ip, malicious_ip)
		#self.malicious_ip = malicious_ip

	def start(self, b):
		super().log(Core.INFO, "DUMMYSERVICE" , "detected activity from IP {} - content: {}".format(super().malicious_ip, b))
		super().send("Protocol error\n")
		super().shutdown()