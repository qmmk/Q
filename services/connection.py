import select
import socket
import threading
import asyncio

from tools.Endlessh import Endlessh
from tools.Honeyports import Honeyports
from tools.Invisiport import Invisiport
from tools.Portspoof import Portspoof
from tools.Tcprooter import Tcprooter

SERVER = socket.gethostbyname(socket.gethostname())


class Connection:
    def __init__(self):
        self.Conns = {}
        self.Sockets = {}
        self.Servers = []
        return

    def extend(self, name, ports, method):
        self.Conns[name] = (ports, method)
        for port in ports:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
            s.bind((SERVER, port))
            print("Serving port: {} on socket {}".format(port, s.fileno()))
            s.listen()
            self.Servers.append(s)
        return

    def run(self, loop, shared):
        loop.run_until_complete(self.init())

    async def init(self):
        while True:
            conn, addr = select.select(self.Servers, [], [])[0][0].accept()
            self.Sockets[addr[1]] = conn.dup()
            threading.Thread(target=self.handle_input, args=(conn, addr)).start()

    def handle_input(self, conn, addr):
        print("New Connection from", addr)
        connected = True
        my_ip = conn.getsockname()[0]
        in_port = conn.getsockname()[1]
        malicious_ip = addr[0]
        out_port = addr[1]
        wsock = self.Sockets[out_port]

        while connected:
            msg = conn.recv(1024).decode('utf-8')
            if msg:
                print("Receive something..{} from {}:{} and we reply with {}:{}"
                      .format(msg, malicious_ip, out_port, my_ip, in_port))

                for name, param in self.Conns.items():
                    if name == "Endlessh" and in_port in param[0]:
                        threading.Thread(target=Endlessh().run(wsock, in_port, malicious_ip, msg, param[1])).start()
                        break
                    if name == "Invisiport" and in_port in param[0]:
                        print("Enable Invisiport..\n")
                        threading.Thread(target=Invisiport().run(wsock, in_port, malicious_ip, msg, param[1])).start()
                        break
                    if name == "Honeyports" and in_port in param[0]:
                        print("Enable Honeyports..\n")
                        threading.Thread(Honeyports().run(wsock, malicious_ip, msg)).start()
                        break
                    if name == "Portspoof" and in_port in param[0]:
                        print("Enable Portspoof..\n")
                        threading.Thread(Portspoof(in_port).run(wsock, malicious_ip, msg)).start()
                        break
                    if name == "Tcprooter":
                        print("Enable Tcprooter..\n")
                        threading.Thread(Tcprooter().run(wsock, malicious_ip, msg)).start()
                        break
            else:
                print('Closing connection to', addr)
                conn.close()
                del self.Sockets[out_port]
                connected = False
        return
