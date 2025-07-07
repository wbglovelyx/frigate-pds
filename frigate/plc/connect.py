import time
from types import SimpleNamespace

import snap7
from snap7.util import *


class Snap7Client():
    def __init__(self, config):
        self.config = config
        self.client = snap7.client.Client()
        self.connected = False
        print(self.config)

    def connect(self):
        try:
            self.client.connect(self.config.ip, self.config.rack, self.config.slot)
            self.connected = True
            print(f"✅ Connected to PLC at {self.config.ip}")
        except Exception as e:
            print(f"❌ Connection failed: {e}")
            self.connected = False

    def disconnect(self):
        if self.connected:
            self.client.disconnect()
            self.connected = False
            print("🔌 Disconnected from PLC")

    def read_bytes(self, area, dbnumber, start, size):
        try:
            return self.client.read_area(area, dbnumber, start, size)
        except Exception as e:
            print(f"❌ Read error: {e}")
            return None

    def write_bytes(self, area, dbnumber, start, data):
        try:
            self.client.write_area(area, dbnumber, start, data)
            print("✅ Write successful")
        except Exception as e:
            print(f"❌ Write error: {e}")

    def read_bit(self, area, dbnumber, byte, bit):
        data = self.read_bytes(area, dbnumber, byte, 1)
        return get_bool(data, 0, bit)

    def write_bit(self, area, dbnumber, byte, bit, value):
        data = self.read_bytes(area, dbnumber, byte, 1)
        set_bool(data, 0, bit, value)
        self.write_bytes(area, dbnumber, byte, data)

    def read_int(self, area, dbnumber, byte):
        data = self.read_bytes(area, dbnumber, byte, 2)
        return get_int(data, 0)

    def write_int(self, area, dbnumber, byte, value):
        data = bytearray(2)
        set_int(data, 0, value)
        self.write_bytes(area, dbnumber, byte, data)


if __name__ == "__main__":
    config = SimpleNamespace(ip="192.168.1.2", rack=0, slot=1)
    plc = Snap7Client(config)

    plc.connect()

    if plc.connected:
        try:

            plc.write_int(snap7.type.Area.MK, 0, 16, 1)
            value = plc.read_int(snap7.type.Area.MK, 0, 16)
            print(f"📖 Read from byte {16}: {value}")

            plc.write_int(snap7.type.Area.MK, 0, 17, 1)
            value = plc.read_int(snap7.type.Area.MK, 0, 17)
            print(f"📖 Read from byte {17}: {value}")

            plc.write_int(snap7.type.Area.MK, 0, 18, 1)
            value = plc.read_int(snap7.type.Area.MK, 0, 18)
            print(f"📖 Read from byte {18}: {value}")

            #测试灯亮2s
            plc.write_int(snap7.type.Area.MK, 0, 20, 1)
            value = plc.read_int(snap7.type.Area.MK, 0, 20)
            print(f"📖 Read from byte {20}: {value}")
            time.sleep(2)
            plc.write_int(snap7.type.Area.MK, 0, 20, 0)
            value = plc.read_int(snap7.type.Area.MK, 0, 20)
            print(f"📖 Read from byte {20}: {value}")

            #测试烽鸣器响1s
            plc.write_int(snap7.type.Area.MK, 0, 21, 1)
            value = plc.read_int(snap7.type.Area.MK, 0, 21)
            print(f"📖 Read from byte {21}: {value}")
            time.sleep(0.5)
            plc.write_int(snap7.type.Area.MK, 0, 21, 0)
            value = plc.read_int(snap7.type.Area.MK, 0, 21)
            print(f"📖 Read from byte {21}: {value}")

        except Exception as e:
            print(f"❌ Error during PLC operations: {e}")

    plc.disconnect()
