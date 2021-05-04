import select
import socket
import threading
import concurrent.futures

from services import log
from tools.Endlessh import Endlessh
from tools.Honeyports import Honeyports
from tools.Invisiport import Invisiport
from tools.Portspoof import Portspoof
from tools.Tcprooter import Tcprooter

SERVER = socket.gethostbyname(socket.gethostname())
MAX_WORKERS = 5


class Connection:
    def __init__(self, ports, method):
        self.ports = ports
        self.method = method


class Server:
    def __init__(self, loop):
        self.loop = loop
        self.Conns = {}
        self.Sockets = {}
        self.Servers = []
        self.Ports = []
        return

    def extend(self, name, ports, method):
        self.Conns[name] = Connection(ports, method)
        self.Ports.extend(ports)
        return

    def reduce(self, ports):
        for port in ports:
            self.Ports = [x for x in self.Ports if x != port]
        return

    def remove(self, name):
        del self.Conns[name]
        return

    def initialization(self):
        for port in self.Ports:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
            s.bind((SERVER, port))
            # print("Serving port: {} on socket {}".format(port, s.fileno()))
            log.sintetic_write(log.INFO, "SERVER", "Serving port {} on socket {}".format(port, s.fileno()))

            s.listen()
            self.Servers.append(s)
        return

    def run(self, shared):
        self.loop.run_until_complete(self.init())

    async def init(self):
        self.initialization()

        # with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        while True:
            conn, addr = select.select(self.Servers, [], [])[0][0].accept()
            self.Sockets[addr[1]] = conn.dup()

            threading.Thread(target=self.handle_input, args=(conn, addr)).start()
            # self.loop.run_in_executor(executor, self.handle_input(conn, addr))

    def handle_input(self, conn, addr):
        # print("New Connection from", addr)
        log.sintetic_write(log.INFO, "SERVER", "New Connection from {}".format(addr))

        connected = True
        my_ip = conn.getsockname()[0]
        in_port = conn.getsockname()[1]
        mal_ip = addr[0]
        out_port = addr[1]
        ws = self.Sockets[out_port]

        with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            while connected:
                msg = conn.recv(1024).decode('utf-8').strip("\n")
                if msg:
                    log.sintetic_write(log.WARNING, "SERVER", "Receive something..{} from {}:{} and we reply with {}:{}"
                                       .format(msg, mal_ip, out_port, my_ip, in_port))

                    # print("Receive something..{} from {}:{} and we reply with {}:{}"
                    #       .format(msg, mal_ip, out_port, my_ip, in_port))

                    for name, tool in self.Conns.items():
                        if name == "Endlessh" and in_port in tool.ports:
                            # print("Enable Endlessh..")
                            self.loop.run_in_executor(executor, Endlessh().run(ws, in_port, mal_ip, msg, tool.method))
                            # threading.Thread(target=Endlessh().run(wsock, in_port, malicious_ip, msg, param[1])).start()
                            break
                        if name == "Invisiport" and in_port in tool.ports:
                            # print("Enable Invisiport..")
                            self.loop.run_in_executor(executor, Invisiport().run(ws, in_port, mal_ip, msg, tool.method))
                            # threading.Thread(target=Invisiport().run(wsock, in_port, malicious_ip, msg, param[1])).start()
                            break
                        if name == "Honeyports" and in_port in tool.ports:
                            # print("Enable Honeyports..")
                            self.loop.run_in_executor(executor, Honeyports().run(ws, mal_ip, msg))
                            # threading.Thread(Honeyports().run(wsock, malicious_ip, msg)).start()
                            break
                        if name == "Portspoof" and in_port in tool.ports:
                            # print("Enable Portspoof..")
                            self.loop.run_in_executor(executor, Portspoof(in_port).run(ws, mal_ip, msg))
                            # threading.Thread(Portspoof(in_port).run(wsock, malicious_ip, msg)).start()
                            break
                        if name == "Tcprooter":
                            # print("Enable Tcprooter..")
                            self.loop.run_in_executor(executor, Tcprooter().run(ws, mal_ip, msg))
                            # threading.Thread(Tcprooter().run(wsock, malicious_ip, msg)).start()
                            break
                else:
                    # print('Closing connection to', addr)
                    log.sintetic_write(log.INFO, "SERVER", "Closing connection to {}".format(addr))
                    conn.close()
                    del self.Sockets[out_port]
                    connected = False
        return
