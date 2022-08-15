import numpy as np
import time
from gpib import Fake

imported_time = time.time()


class LakeShore(Fake):
    @staticmethod
    def query(msg: str) -> str:
        """Write to the device and then read its response"""
        time.sleep(0.1)
        if msg == 'KRDG? A':
            return str(300 - 0.1 * (time.time() - imported_time) + np.random.random())
        if 'PID?' in msg:
            return '1,1,1'
        else:
            return f"You queried the fake GPIB interface with {msg}"


class VoltageSupply(Fake):
    @staticmethod
    def query(msg: str) -> str:
        if msg == 'V?':
            time.sleep(0.1)
            return str((3+np.random.random()) * np.sin(time.time() - imported_time + 0.1 * np.random.random()))
        else:
            return f"You queried the fake GPIB interface with {msg}"


class PhotonCounter(Fake):
    @staticmethod
    def query(msg: str) -> str:
        time.sleep(0.1)
        if msg == 'C?':
            return str(3000 + 1000 * np.random.random() * np.sin(time.time()))
        else:
            return f"You queried the fake GPIB interface with {msg}"
