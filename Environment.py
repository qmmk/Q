import asyncio
import json
from multiprocessing import Manager, Process

from tools.Cryptolocked import Cryptolocked
from tools.Honeyfile import Honeyfile, time
from tools.Core import Core
from enum import Enum

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
        self.Core = Core
        self.manager = Manager()
        self.shared = self.manager.dict()
        self.loop = asyncio.get_event_loop()

        with open('persistent/config.json') as c:
            config = json.load(c)
        for i in config:
            t = Tool(i, config[i])
            self.Tools.append(t)
            self.init(t)

        self.print_status()
        print("starting..")
        self.start("Honeyfile")
        self.start("Cryptolocked")
        self.start("StealthCryptolocked")
        time.sleep(5)
        self.print_status()
        time.sleep(5)
        print("stopping..")
        # self.stop("Honeyfile")
        time.sleep(5)
        self.print_status()

        return

    def __del__(self):
        self.loop.close()
        self.manager.shutdown()
        return

    def print_status(self):
        for tool in self.Tools:
            print("Tool {} is {}".format(tool.name, tool.status))

    def init(self, t):
        self.loop = asyncio.get_event_loop()

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
