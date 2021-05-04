import inotify
import inotify.adapters
import inotify.constants
import concurrent.futures
from inotify.calls import InotifyError
from tools.ArtilleryIntegrity import ArtilleryIntegrity
from tools.ArtillerySSHBFM import ArtillerySSHBFM
from tools.Cryptolocked import Cryptolocked
from tools.Honeyfile import Honeyfile
from tools.StealthCryptolocked import StealthCryptolocked

MAX_WORKERS = 5


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

    def extend(self, name, paths, method):
        self.Tools[name] = Tool(paths, method)
        self.Paths.extend(paths)
        return

    def reduce(self, paths):
        for path in paths:
            self.Paths = [x for x in self.Paths if x != path]
        return

    def remove(self, name):
        del self.Tools[name]
        return

    def initialization(self):
        for name, tool in self.Tools.items():
            if name == "Honeyfile":
                self.Tools[name].init = Honeyfile(tool)
            if name == "Cryptolocked":
                self.Tools[name].init = Cryptolocked(tool)
                p = self.Tools[name].init.initialization()
                self.Paths.extend(p)
                self.Tools[name].paths.extend(p)
            if name == "StealthCryptolocked":
                self.Tools[name].init = StealthCryptolocked(tool)
                p = self.Tools[name].init.initialization()
                self.Paths.extend(p)
                self.Tools[name].paths.extend(p)
            if name == "ArtilleryIntegrity":
                self.Tools[name].init = ArtilleryIntegrity(tool)
                p = self.Tools[name].init.initialization()
                self.Paths.extend(p)
                self.Tools[name].paths.extend(p)
            if name == "ArtillerySSHBFM":
                self.Tools[name].init = ArtillerySSHBFM(tool)

    def run(self, shared):
        self.loop.run_until_complete(self.init())

    async def init(self):
        self.initialization()

        with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
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
                            print("Enable Honeyfile..")
                            # executor.submit(self.Tools[name].init.process, event)
                            self.loop.run_in_executor(executor, self.Tools[name].init.process(event))
                        if name == "Cryptolocked" and target in tool.paths:
                            print("Enable Cryptolocked..")
                            # executor.submit(self.Tools[name].init.process, event)
                            self.loop.run_in_executor(executor, self.Tools[name].init.process(event))
                        if name == "StealthCryptolocked" and target in tool.paths:
                            print("Enable StealthCryptolocked..")
                            # executor.submit(self.Tools[name].init.process, event)
                            self.loop.run_in_executor(executor, self.Tools[name].init.process(event))
                        if name == "ArtilleryIntegrity" and target in tool.paths:
                            print("Enable ArtilleryIntegrity..")
                            # executor.submit(self.Tools[name].init.process, event)
                            self.loop.run_in_executor(executor, self.Tools[name].init.process(event))
                        if name == "ArtillerySSHBFM" and target in tool.paths:
                            print("Enable ArtillerySSHBFM..")
                            # executor.submit(self.Tools[name].init.process, event)
                            self.loop.run_in_executor(executor, self.Tools[name].init.process(event))
        return
