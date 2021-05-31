import asyncio
import json
import time
import uvloop
from multiprocessing import Process
from Environment.services import core
from Environment.services.bwlist import reset_all, access_host, load_blacklist, bwlist_init
from Environment.services.filesystem import Filesystem
from Environment.services.connection import Server

# LOOP
uvloop.install()
asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())


class Environment:
    def __init__(self):
        self.loop = asyncio.get_event_loop()
        self.conn = Server(self.loop)
        self.fs = Filesystem(self.loop)
        self.state = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

        self.p1 = None  # SERVER (P1)
        self.p2 = None  # FILESYSTEM (P2)

        # RESET & INIT & LOAD
        # reset_all()
        # bwlist_init()
        # load_blacklist()

        # CONFIGURATION
        self.init_config()

        # MOUNT
        # access_host(self.fs.Paths)

        # time.sleep(10)

        # DUE MAIN PROCESS: SERVER (P1) & FILESYSTEM (P2)
        self.start_net()
        self.start_fs()

        return

    def __del__(self):
        self.stop_fs()
        self.stop_net()
        self.loop.close()
        return

    def init_config(self):
        with open(core.CONFIG) as c:
            config = json.load(c)
        for i in config:
            if config[i]["type"] == "net":
                self.conn.update(config[i]["id"], config[i]["class"], config[i]["params"], config[i]["method"])
            if config[i]["type"] == "fs":
                self.fs.update(config[i]["id"], config[i]["class"], config[i]["params"], config[i]["method"])
        return

    def update_state(self, action):
        self.stop_net()
        self.stop_fs()
        for idx, x in enumerate(action):
            if x != 2 and self.state[idx] != x:
                self.state[idx] = x
                if idx < 5:
                    self.conn.update(tool_id=idx, state=x)
                else:
                    self.fs.update(tool_id=idx, state=x)
        self.start_net()
        self.start_fs()
        return

    @staticmethod
    def process_status(p):
        status = ""
        try:
            if not p._closed:
                status = "started"
        except ValueError as e:
            status = "stopped"
        return status

    # <editor-fold desc="FILESYSTEM">

    def start_fs(self):
        if self.p2 is None or self.process_status(self.p2) != "started":
            try:
                self.p2 = Process(target=self.fs.run, args=())
                self.p2.start()
            except ValueError as e:
                print(e)
        else:
            print("Filesystem already running.")
        return

    def stop_fs(self):
        if self.p2 is not None and self.process_status(self.p2) != "stopped":
            try:
                self.p2.terminate()
                self.p2.join(timeout=1.0)
                self.p2.close()
            except ValueError as e:
                print(e)
        else:
            print("Filesystem already stopped.")
        return

    # </editor-fold>

    # <editor-fold desc="SERVER">

    def start_net(self):
        if self.p1 is None or self.process_status(self.p1) != "started":
            try:
                self.p1 = Process(target=self.conn.run, args=())
                self.p1.start()
            except ValueError as e:
                print(e)
        else:
            print("Server already running.")
        return

    def stop_net(self):
        if self.p1 is not None and self.process_status(self.p1) != "stopped":
            try:
                self.p1.terminate()
                self.p1.join(timeout=1.0)
                self.p1.close()
            except ValueError as e:
                print("Server already stopped.")
        else:
            print("Server already stopped.")
        return

    # </editor-fold>
