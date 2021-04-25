import asyncio
import json
from multiprocessing import Manager, Process

from tools.ArtilleryIntegrity import ArtilleryIntegrity
from tools.Cryptolocked import Cryptolocked
from tools.Endlessh import Endlessh
from tools.Honeyfile import Honeyfile, time
from services.core import Core
from enum import Enum
from services.connection import Server

from tools.StealthCryptolocked import StealthCryptolocked


class ToolsType(Enum):
    ArtilleryIntegrity = "ArtilleryIntegrity"
    ArtillerySSHBFM = "ArtillerySSHBFM"
    Cryptolocked = "Cryptolocked"
    Dummyservice = "Dummyservice"
    Endlessh = "Endlessh"
    Honeyfile = "Honeyfile"
    Honeyports = "Honeyports"
    Invisiport = "Invisiport"
    Portspoof = "Portspoof"
    StealthCryptolocked = "StealthCryptolocked"
    Tcprooter = "Tcprooter"


class Tool:
    def __init__(self, id, params):
        self.id = id
        self.type = params["type"]
        self.file = params["file"]
        self.name = params["class"]
        self.method = params["method"]
        self.attr = params["params"]
        self.status = "NOT INIT"
        self.proc = ""


class Environment:
    def __init__(self):
        # Read initial configuration
        self.Tools = []
        self.Tasks = []
        # self.Core = Core
        self.manager = Manager()
        self.server = Server()
        self.shared = self.manager.dict()
        self.loop = asyncio.get_event_loop()

        with open('persistent/config.json') as c:
            config = json.load(c)
        for i in config:
            if config[i]["type"] == "net":
                self.init_net(Tool(i, config[i]))
            if config[i]["type"] == "fs":
                self.init_fs(Tool(i, config[i]))

        # Server process
        p = Process(target=self.server.run, args=(self.loop, self.shared))
        p.start()
        # output = self.loop.run_until_complete(asyncio.gather(self.server.start(self.loop, 65432)))
        # self.Tasks.append(self.server.add(self.loop, 65432))
        # self.loop.run_until_complete(asyncio.gather(*self.Tasks))
        # print("server output -> {}\n".format(output))

        self.start("ArtilleryIntegrity")

        """
        self.print_status()
        print("starting..")
        self.start("Honeyfile")
        self.start("Cryptolocked")
        self.start("StealthCryptolocked")
        time.sleep(15)
        self.print_status()
        time.sleep(15)
        print("stopping..")
        self.stop("Honeyfile")
        # time.sleep(5)
        self.print_status()
        """

        return

    def __del__(self):
        self.loop.close()
        self.manager.shutdown()
        return

    def print_status(self):
        for tool in self.Tools:
            print("Tool {} is {}".format(tool.name, tool.status))

    def init_net(self, t):
        self.Tools.append(t)
        self.server.extend(t.name, t.attr, t.method)
        return

    def init_fs(self, t):
        self.loop = asyncio.get_event_loop()
        self.Tools.append(t)

        """
        
        if t.name == "Honeyfile":
            h = Honeyfile(t)
            t.proc = Process(target=h.run, args=(self.loop, self.shared,))
            t.status = "STARTED"
        if t.name == "Cryptolocked":
            h = Cryptolocked(t)
            t.proc = Process(target=h.run, args=(self.loop, self.shared,))
            t.status = "STARTED"
        if t.name == "StealthCryptolocked":
            h = StealthCryptolocked(t)
            t.proc = Process(target=h.run, args=(self.loop, self.shared,))
            t.status = "STARTED"       
        """
        if t.name == "ArtilleryIntegrity":
            h = ArtilleryIntegrity(t)
            t.proc = Process(target=h.run, args=(self.loop, self.shared,))
            t.status = "STARTED"

        return

    def start(self, name):
        t = self.get_current_tool(name)
        try:
            t.proc.start()
            t.status = "RUNNING"
        except ValueError as e:
            print(e)
        return

    def stop(self, name):
        t = self.get_current_tool(name)
        try:
            t.proc.terminate()
            t.proc.join(timeout=1.0)
            t.proc.close()
            t.status = "STOPPED"
        except ValueError as e:
            print(e)
        return

    def get_current_tool(self, name):
        return [tool for tool in self.Tools if tool.name == name][0]
