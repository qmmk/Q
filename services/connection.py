import asyncio
import socket

from tools.Endlessh import Endlessh
from tools.Honeyports import Honeyports
from tools.Invisiport import Invisiport
from tools.Portspoof import Portspoof
from tools.Tcprooter import Tcprooter

SERVER = socket.gethostbyname(socket.gethostname())

FAMILY = socket.AF_INET
MAX_LEN = 2048
TIMEOUT = 16
MAX_WORKERS = 5


class Server(asyncio.Protocol):
    def __init__(self):
        self.Ports = []
        self.Tasks = []
        self.Conns = {}
        return

    def extend(self, name, ports, method):
        self.Ports.extend(ports)
        self.Conns[name] = (ports, method)
        return

    def run(self, loop, shared):
        for port in self.Ports:
            print("Serving port: {}".format(port))
            self.Tasks.append(loop.create_task(self.start(loop, port)))
        output = loop.run_until_complete(asyncio.gather(*self.Tasks))

    async def start(self, loop, port):
        server = await asyncio.start_server(self.accept_client, host=SERVER, port=port, loop=loop,
                                            family=FAMILY, reuse_address=True, reuse_port=True)
        await server.serve_forever()

    async def accept_client(self, reader, writer):
        # loop = asyncio.get_running_loop()
        # with concurrent.futures.ProcessPoolExecutor(max_workers=MAX_WORKERS) as executor:
        while not writer.is_closing():

            data = await reader.read(MAX_LEN)
            msg = data.decode()

            # get information about socket
            info = writer.get_extra_info('socket')

            in_port = info.getsockname()[1]
            malicious_ip = info.getpeername()[0]

            print(f"Received something on: {in_port}, from {malicious_ip!r}")
            for name, param in self.Conns.items():
                if name == "Endlessh" and in_port in param[0]:
                    print("Enable Endlessh..\n")
                    # loop.run_in_executor(executor, Endlessh().run(writer, in_port, malicious_ip, msg, param[1]))
                    # executor.submit(Endlessh().run, writer, in_port, malicious_ip, msg, param[1])
                    await Endlessh().run(writer, in_port, malicious_ip, msg, param[1])
                    # await t.run(writer, in_port, malicious_ip, msg, param[1])
                    # loop.create_task(t.run(writer, in_port, malicious_ip, msg, param[1]))
                    # await loop.run_in_executor(executor, t.run, writer, in_port, malicious_ip, msg, param[1])

                if name == "Invisiport" and in_port in param[0]:
                    print("Enable Invisiport..\n")
                    # asyncio.run(Invisiport().run(writer, in_port, malicious_ip, msg, param[1]))
                    # executor.submit(Invisiport, writer, in_port, malicious_ip, msg, param[1])
                    await Invisiport().run(writer, in_port, malicious_ip, msg, param[1])
                    # await t.run(writer, in_port, malicious_ip, msg, param[1])
                    # await loop.run_in_executor(executor, t.run, writer, in_port, malicious_ip, msg, param[1])
                    # loop.create_task(t.run(writer, in_port, malicious_ip, msg, param[1]))
                if name == "Honeyports" and in_port in param[0]:
                    print("Enable Honeyports..\n")
                    await Honeyports().run(writer, malicious_ip, msg)
                if name == "Portspoof" and in_port in param[0]:
                    print("Enable Portspoof..\n")
                    await Portspoof(in_port).run(writer, malicious_ip, msg)
                if name == "Tcprooter":
                    print("Enable Tcprooter..\n")
                    await Tcprooter().run(writer, malicious_ip, msg)
                else:
                    writer.close()
        return
