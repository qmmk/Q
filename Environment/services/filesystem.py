import inotify
import inotify.adapters
import inotify.constants
import concurrent.futures
from inotify.calls import InotifyError
from Environment.tools.ArtilleryIntegrity import init_artillery_integrity, run_artillery_integrity
from Environment.tools.ArtillerySSHBFM import run_artillery_sshbfm
from Environment.tools.Cryptolocked import init_cryptolocked, run_cryptolocked
from Environment.tools.Honeyfile import run_honeyfile, init_honeyfile
from Environment.tools.StealthCryptolocked import init_stealth_cryptolocked, run_stealth_cryptolocked
from Environment.services import core


class Tool:
    def __init__(self, tool_id, name, state, paths, method):
        self.id = tool_id
        self.name = name
        self.state = state
        self.paths = paths
        self.method = method
        return


class Filesystem:
    def __init__(self, loop):
        self.loop = loop
        self.Tools = {}
        return

    def update(self, tool_id, name=None, paths=None, method=None, state=None):
        if state is None:
            self.Tools[tool_id] = Tool(tool_id, name, 0, paths, method)
        else:
            self.Tools[tool_id].state = state
        return

    def initialization(self):
        for tool in self.Tools.values():
            if tool.state == 0:
                if tool.name == "Honeyfile":
                    init_honeyfile(tool.paths)
                if tool.name == "Cryptolocked":
                    self.Tools[tool.id].paths.extend(init_cryptolocked(tool.paths))
                if tool.name == "StealthCryptolocked":
                    self.Tools[tool.id].paths.extend(init_stealth_cryptolocked(tool.paths))
                if tool.name == "ArtilleryIntegrity":
                    self.Tools[tool.id].paths.extend(init_artillery_integrity(tool.paths))

    def run(self):
        self.loop.run_until_complete(self.init())

    async def init(self):
        self.initialization()

        with concurrent.futures.ThreadPoolExecutor(max_workers=core.MAX_WORKERS) as executor:
            i = inotify.adapters.Inotify()
            for tool in self.Tools.values():
                if tool.state == 0:
                    for path in tool.paths:
                        try:
                            i.add_watch(path)
                        except InotifyError as e:
                            print(e)

            for event in i.event_gen():
                if event is not None:
                    (header, types, target, name) = event

                    for tool in self.Tools.values():
                        if tool.name == "Honeyfile" and target in tool.paths:
                            self.loop.run_in_executor(executor, run_honeyfile(event, tool.method, tool.id))
                        if tool.name == "Cryptolocked" and target in tool.paths:
                            self.loop.run_in_executor(executor, run_cryptolocked(event, tool.method, tool.id))
                        if tool.name == "StealthCryptolocked" and target in tool.paths:
                            self.loop.run_in_executor(executor, run_stealth_cryptolocked(event, tool.method, tool.id))
                        if tool.name == "ArtilleryIntegrity" and target in tool.paths:
                            self.loop.run_in_executor(executor, run_artillery_integrity(event, tool.method, tool.id))
                        if tool.name == "ArtillerySSHBFM" and target in tool.paths:
                            self.loop.run_in_executor(executor, run_artillery_sshbfm(event, tool.id))
        return
