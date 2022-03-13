from bluepy.btle import Scanner, DefaultDelegate, BTLEInternalError
import json
from datetime import datetime

class ScanDelegate(DefaultDelegate):
    def __init__(self):
        DefaultDelegate.__init__(self)

    def handleDiscovery(self, dev, isNewDev, isNewData):
        for (sdid, desc, val) in dev.getScanData():
            if self.isTemperature(dev.addr, sdid, val):
                print(json.dumps(self.parseData(val)))
                exit()

    def isTemperature(self, addr, sdid, val):
        if sdid != 22:
            return False
        if len(val) != 30:
            return False
        return True
    
    def parseData(self, val):
        bytes = [int(val[i:i+2], 16) for i in range(0, len(val), 2)]
        if bytes[8] > 127:
            bytes[8] -= 256
        return {
            'timestamp': datetime.now().astimezone().replace(microsecond=0).isoformat(),
            'mac': ":".join(["{:02X}".format(bytes[i]) for i in range(2,8)]),
            'temperature': (bytes[8] * 256 + bytes[9]) / 10,
            'humidity': bytes[10],
            'battery_percent': bytes[11],
            'battery_volt': (bytes[12] * 256 + bytes[13]) / 1000,
            'count': bytes[14],
        }

scanner = Scanner().withDelegate(ScanDelegate())
scanner.scan(10.0, passive=True)
