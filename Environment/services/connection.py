import select
import socket
import threading
import concurrent.futures
from Environment.services import log, core
from Environment.tools.Endlessh import run_endlessh
from Environment.tools.Honeyports import run_honeyports
from Environment.tools.Invisiport import run_invisiport
from Environment.tools.Portspoof import run_portspoof
from Environment.tools.Tcprooter import run_tcprooter

SERVER = socket.gethostbyname(socket.gethostname())


class Connection:
    def __init__(self, tool_id, name, state, ports, method):
        self.id = tool_id
        self.name = name
        self.state = state
        self.ports = ports
        self.method = method
        return


class Server:
    def __init__(self, loop):
        self.loop = loop
        self.Conns = {}
        self.Sockets = {}
        self.Servers = []
        return

    def update(self, tool_id, name=None, ports=None, method=None, state=None):
        if state is None:
            self.Conns[tool_id] = Connection(tool_id, name, 0, ports, method)
        else:
            self.Conns[tool_id].state = state
        return

    def initialization(self):
        self.Servers = []
        for tool in self.Conns.values():
            if tool.state == 0:
                for port in tool.ports:
                    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
                    s.bind((SERVER, port))
                    log.sintetic_write(core.INFO, "SERVER", "Serving port {}:{} on socket {}"
                                       .format(SERVER, port, s.fileno()))
                    s.listen()
                    self.Servers.append(s)
        return

    def run(self):
        self.loop.run_until_complete(self.init())

    async def init(self):
        self.initialization()

        while True:
            conn, addr = select.select(self.Servers, [], [])[0][0].accept()
            self.Sockets[addr[1]] = conn.dup()
            threading.Thread(target=self.handle_input, args=(conn, addr)).start()

    def handle_input(self, conn, addr):
        log.sintetic_write(core.INFO, "SERVER", "New Connection from {}".format(addr))

        connected = True
        my_ip = conn.getsockname()[0]
        in_port = conn.getsockname()[1]
        mal_ip = addr[0]
        out_port = addr[1]
        ws = self.Sockets[out_port]

        with concurrent.futures.ThreadPoolExecutor(max_workers=core.MAX_WORKERS) as executor:
            while connected:
                try:
                    msg = conn.recv(1024).decode(encoding=core.FORMAT, errors="replace")
                    if msg:
                        log.sintetic_write(core.WARNING, "SERVER", "GET [{}] from {}:{} and we reply with {}:{}"
                                           .format(msg.strip("\n"), mal_ip, out_port, my_ip, in_port))
                        for tool in self.Conns.values():
                            if tool.name == "Endlessh" and in_port in tool.ports:
                                self.loop.run_in_executor(executor,
                                                          run_endlessh(ws, in_port, mal_ip, msg, tool))
                                break
                            if tool.name == "Invisiport" and in_port in tool.ports:
                                self.loop.run_in_executor(executor,
                                                          run_invisiport(ws, in_port, mal_ip, msg, tool))
                                break
                            if tool.name == "Honeyports" and in_port in tool.ports:
                                self.loop.run_in_executor(executor, run_honeyports(ws, mal_ip, msg, tool.id))
                                break
                            if tool.name == "Portspoof" and in_port in tool.ports:
                                self.loop.run_in_executor(executor, run_portspoof(ws, in_port, mal_ip, msg, tool.id))
                                break
                            if tool.name == "Tcprooter":
                                self.loop.run_in_executor(executor, run_tcprooter(ws, mal_ip, msg, tool.id))
                                break
                except ConnectionError as e:
                    print(e)
                connected = False
        log.sintetic_write(core.INFO, "SERVER", "Closing connection to {}".format(addr))
        conn.close()
        del self.Sockets[out_port]
        return
