#!/usr/bin/env python3

import bluepy
import sys
import time
import struct
import argparse

class Flash(object):
    def __init__(self, doTest=False):
        super().__init__()
        self._doTest = doTest
        self._firmware = None
        self._device = None
        self._miEnabled = False
        self._customEnabled = False

    def loadFirmware(self, firmware_name):
        with open(firmware_name, "rb") as firmware_file:
            firmware = firmware_file.read()
        signature = struct.unpack(">L",firmware[8:12])[0]
        if signature != 0x4b4e4c54:
            print("The file is not a valid firmware file. Aborting.")
            sys.exit(-1)
        print(f"The firmware is {len(firmware)} bytes in length.")
        while 0 != (len(firmware) % 16):
            firmware += bytes([0xff])
        self._firmware = firmware
        self._blockCount = int(len(firmware) / 16)
        print(f"Count: {int(self._blockCount)}")

    def disconnect(self):
        if not self._doTest:
            self._device.disconnect()

    def connect(self, mac):
        if self._doTest:
            return
        else:
            conTry = 0
            maxTry = 5
            self._device = bluepy.btle.Peripheral()
            print(f"Trying to connect to {mac}")
            while True:
                conTry += 1
                try:
                    self._device.connect(mac)
                    break
                except bluepy.btle.BTLEException as ex:
                    if conTry <= maxTry:
                        print(f"{ex}, retrying: {conTry}/{maxTry}")
                    else:
                        print(f"{ex}")
                        self.disconnect()
                        sys.exit(-1)
            print(f"Connected to {mac}")

            services = self._device.getServices()
            self._services = {}
            for service in services:
                self._services[str(service.uuid)] = service
            if '00010203-0405-0607-0809-0a0b0c0d1912' in self._services:
                service = self._services['00010203-0405-0607-0809-0a0b0c0d1912']
                self._writeCharacteristic = service.getCharacteristics(forUUID='00010203-0405-0607-0809-0a0b0c0d2b12')[0]
                self._detectMi()
            else:
                print("No Telink device detected.")
                self.disconnect()
                sys.exit(-1)

    def _detectMi(self):
        self._miEnabled = "ebe0ccb0-7a0a-4b0c-8a1a-6ff2997da3a6" in self._services
        self._customEnabled = "00001f10-0000-1000-8000-00805f9b34fb" in self._services

        if self._miEnabled:
            print("Detected Mi Thermometer. Can't flash it.")
            self.disconnect()
            sys.exit(-1)
        elif self._customEnabled:
            print("Detected device with valid custom Firmware")
            service = self._services['00001f10-0000-1000-8000-00805f9b34fb']
            self._settingsCharacteristics = service.getCharacteristics(forUUID='00001f1f-0000-1000-8000-00805f9b34fb')[0]
        else:
            print("Detected device with not valid Firmware. Can't flash it.")
            self.disconnect()
            sys.exit(-1)

    def startFlashing(self):
        self._otaCharSend(bytes([0x00, 0xff]))
        self._otaCharSend(bytes([0x01, 0xff]))
        if self._doTest:
            endline = "\n"
        else:
            endline = "\r"
        for c in range(self._blockCount):
            print(f"Sending block {c} of {self._blockCount} ({int(100 * c / self._blockCount)}%)", end=endline)
            offset = c * 16
            blockCount = struct.pack("<H", c)
            block = self._firmware[offset:offset + 16]
            crc = self._crc16_modbus(blockCount + block)
            self._otaCharSend(blockCount + block + crc)
            if ((c + 1) % 8) == 0:
                if self._doTest:
                    print("Doing read")
                else:
                    self._writeCharacteristic.read()
        blockCount = self._blockCount - 1
        blockCountInverted = 65535 - blockCount
        data = struct.pack("<HHH",0xff02, blockCount, blockCountInverted)
        self._otaCharSend(data)
        print()
        print("Done")

    def _crc16_modbus(self, data):
        crc = 0x0ffff
        for d in data:
            crc ^= struct.unpack("B", bytes([d]))[0]
            for l in range(8):
                odd = crc & 0x0001
                crc = (crc >> 1) & 0x7fff
                if odd != 0:
                    crc ^= 0xa001
        return struct.pack("<H",crc)

    def _otaCharSend(self, data):
        if self._doTest:
            for d in data:
                d = hex(d)[2:]
                if len(d) == 1:
                    d = '0' + d
                print(d, end = "")
            print()
        else:
            try:
                self._writeCharacteristic.write(data)
            except:
                print("Failed to send data to the device. Aborting.")
                self.disconnect()
                sys.exit(-1)

    def sendCustomSetting(self, data):
        if self._doTest:
            for d in data:
                d = hex(d)[2:]
                if len(d) == 1:
                    d = '0' + d
                print(d, end = "")
            print()
        else:
            try:
                self._settingsCharacteristics.write(data)
            except:
                print(f"Error on sending setting 0x{data.hex()}")
                self.disconnect()
                sys.exit(-1)
            print(f"Settings 0x{data.hex()} was send successful")

    def waitForNotifications(self, timeout):
        self._device.waitForNotifications(timeout)


def main(argv):
    parser = argparse.ArgumentParser(description="Telink Flasher for Mi Thermostat")
    group = parser.add_mutually_exclusive_group(required=True)
    parser.add_argument("-t", "--test", dest="doTest", help="enable test mode", action="store_true")
    group.add_argument("-f", "--firmware_file", help="firmware file to flash")
    group.add_argument("-s", "--setting", help="custom settings strings to send")
    parser.add_argument("mac", help="Mi Thermostat MAC address")
    args = parser.parse_args()

    manager = Flash(args.doTest)
    manager.connect(args.mac)

    if args.firmware_file:
        manager.loadFirmware(args.firmware_file)
        manager.startFlashing()
    if args.setting:
        try:
            # convert "hex" string into an integer
            setting = int(args.setting, 16)
            # convert the integer into a bytearray
            setting = setting.to_bytes(setting.bit_length() // 8, "big")
        except:
            print(f"Input '{args.setting}' is not a valid hex string")
            manager.disconnect()
            sys.exit(-1)
        manager.sendCustomSetting(setting)

    manager.disconnect()


if __name__ == "__main__":
    try:
        main(sys.argv[1:])
    except Exception as exc:
        sys.stderr.write("%s\n" % exc)
        sys.exit(1)
