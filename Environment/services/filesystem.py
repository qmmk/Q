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
    def __init__(self, paths, method):
        self.init = ""
        self.paths = paths
        self.method = method


class Filesystem:
    def __init__(self, loop):
        self.loop = loop
        self.Tools = {}
        self.Paths = []
        return

    def extend(self, name, paths, method=None):
        if name in self.Tools:
            self.Tools[name].paths.extend(paths)
            if method is not None:
                self.Tools[name].method = method
        else:
            self.Tools[name] = Tool(paths, method)
        self.Paths.extend(paths)
        return

    def reduce(self, name, paths=None):
        if paths is not None:
            self.Tools[name].paths = [x for x in self.Tools[name].paths if x not in paths]
            self.Paths = [x for x in self.Paths if x not in paths]
        else:
            del self.Tools[name]
        return

    def initialization(self):
        for name, tool in self.Tools.items():
            if name == "Honeyfile":
                init_honeyfile(tool.paths)
            if name == "Cryptolocked":
                p = init_cryptolocked(tool.paths)
                self.Paths.extend(p)
                self.Tools[name].paths.extend(p)
            if name == "StealthCryptolocked":
                p = init_stealth_cryptolocked(tool.paths)
                self.Paths.extend(p)
                self.Tools[name].paths.extend(p)
            if name == "ArtilleryIntegrity":
                p = init_artillery_integrity(tool.paths)
                self.Paths.extend(p)
                self.Tools[name].paths.extend(p)

    def run(self):
        self.loop.run_until_complete(self.init())

    async def init(self):
        self.initialization()

        with concurrent.futures.ThreadPoolExecutor(max_workers=core.MAX_WORKERS) as executor:
            i = inotify.adapters.Inotify()
            for path in self.Paths:
                try:
                    i.add_watch(path)
                except InotifyError as e:
                    print(e)

            for event in i.event_gen():
                if event is not None:
                    (header, types, target, name) = event

                    for name, tool in self.Tools.items():
                        if name == "Honeyfile" and target in tool.paths:
                            self.loop.run_in_executor(executor, run_honeyfile(event, tool.method))
                        if name == "Cryptolocked" and target in tool.paths:
                            self.loop.run_in_executor(executor, run_cryptolocked(event, tool.method))
                        if name == "StealthCryptolocked" and target in tool.paths:
                            self.loop.run_in_executor(executor, run_stealth_cryptolocked(event, tool.method))
                        if name == "ArtilleryIntegrity" and target in tool.paths:
                            self.loop.run_in_executor(executor, run_artillery_integrity(event, tool.method))
                        if name == "ArtillerySSHBFM" and target in tool.paths:
                            self.loop.run_in_executor(executor, run_artillery_sshbfm(event))
        return
