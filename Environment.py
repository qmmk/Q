import asyncio
import json
import time
import uvloop
from multiprocessing import Manager, Process
from services.filesystem import Filesystem
from services.connection import Server

# LOOP
uvloop.install()
asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())


class Environment:
    def __init__(self):
        self.loop = asyncio.get_event_loop()
        self.manager = Manager()
        self.conn = Server(self.loop)
        self.fs = Filesystem(self.loop)
        self.shared = self.manager.dict()

        self.p1 = None  # SERVER (P1)
        self.p2 = None  # FILESYSTEM (P2)

        with open('persistent/config.json') as c:
            config = json.load(c)
        for i in config:
            if config[i]["type"] == "net":

                self.conn.extend(config[i]["class"], config[i]["params"], config[i]["method"])
            if config[i]["type"] == "fs":
                self.fs.extend(config[i]["class"], config[i]["params"], config[i]["method"])

        # DUE MAIN PROCESS: SERVER (P1) & FILESYSTEM (P2)
        self.start_net()
        self.start_fs()


        # testing
        # self.testing()

        return

    def __del__(self):
        self.stop_fs()
        self.stop_net()
        self.loop.close()
        self.manager.shutdown()
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

    def testing(self):

        print("Uno")
        self.start_net()
        self.stop_net()
        print("Due")
        self.start_net()
        self.stop_net()

        print("Tre_1")
        self.stop_net()
        print("Tre_2")
        self.start_net()
        print("Quattro_1")
        self.start_net()

        self.stop_net()

        self.start_net()

        print("First pause..")
        time.sleep(10)
        # self.conn.reduce([1999, 2001])
        self.del_server([1999, 2001])

        print("Second pause..")
        time.sleep(10)

        self.print_status()
        print("starting..")
        self.start("Honeyfile")
        self.start("Cryptolocked")
        self.start("StealthCryptolocked")
        self.start("ArtilleryIntegrity")
        time.sleep(15)
        self.print_status()
        time.sleep(15)
        print("stopping..")
        self.stop("Honeyfile")
        # time.sleep(5)
        self.print_status()
        return

    # <editor-fold desc="FILESYSTEM">

    def start_fs(self):
        if self.p2 is None or self.process_status(self.p2) != "started":
            try:
                self.p2 = Process(target=self.fs.run, args=(self.shared,))
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

    def extend_fs(self, name, paths, method):
        self.stop_fs()
        self.conn.extend(name, paths, method)
        self.start_fs()
        return

    def reduce_fs(self, paths):
        self.stop_fs()
        self.conn.reduce(paths)
        self.start_fs()
        return

    def remove_fs(self, name):
        self.stop_fs()
        self.conn.remove(name)
        self.start_fs()

    # </editor-fold>

    # <editor-fold desc="SERVER">

    def start_net(self):
        if self.p1 is None or self.process_status(self.p1) != "started":
            try:
                self.p1 = Process(target=self.conn.run, args=(self.shared,))
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

    def extend_net(self, name, ports, method):
        self.stop_net()
        self.conn.extend(name, ports, method)
        self.start_net()
        return

    def reduce_net(self, ports):
        self.stop_net()
        self.conn.reduce(ports)
        self.start_net()
        return

    def remove_net(self, name):
        self.stop_net()
        self.conn.remove(name)
        self.start_net()
        return

    # </editor-fold>


