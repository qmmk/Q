import asyncio
import json
from tools.Honeyfile import Honeyfile, time
from tools.Core import Core
from enum import Enum
from core import pool
from asyncio import run_coroutine_threadsafe, AbstractEventLoop



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


class Environment:
    def __init__(self):
        # Read initial configuration
        self.Tools = []
        self.Core = Core

        with open('persistent/config.json') as c:
            config = json.load(c)
        for i in config:
            self.Tools.append(Tool(i, config[i]))
            asyncio.get_event_loop().run_until_complete(self.start(config[i]["class"], config[i]["params"]))
        return

    async def start(self, c, p):
        if c == "Honeyfile":
            print("Initialization of HoneyFile")
            h = Honeyfile(p)

            print("START threading -->\n")

            # run_coroutine_threadsafe(h.get_events(), loop=AbstractEventLoop.run_forever())

            f = h.get_events()
            #time.sleep(30)
            print("STOP threading -->\n")

            """
            f.cancel()
            try:
                await f
            except asyncio.CancelledError:
                pass
            print("STOPPED. -->\n")
            """
        return
