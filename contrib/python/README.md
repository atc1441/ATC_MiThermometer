# Quick Thermometer scan in Python

This is intended as a demo of how to read BLE announcements in Python.  It is based on [bluepy](https://github.com/IanHarvey/bluepy).

## Usage

```
❯ pip3 install bluepy
[...]
❯ python3 scan-thermometer.py
{"timestamp": "2021-06-10T20:36:50+02:00", "mac": "A4:C1:38:XX:XX:XX", "temperature": 23.4, "humidity": 52, "battery_percent": 85, "battery_volt": 0.328, "count": 22}
```

The program terminates after reading one value, or after 10s.

The scan is performed in passive mode.
