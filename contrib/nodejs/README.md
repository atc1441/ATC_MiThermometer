# Scan for reflashed LYWSD03MMC

This short Node.js program scans for BLE announcements from the reflashed LYWSD03MMC 
Mijia Thermometer+Hygrometer from https://github.com/atc1441/ATC_MiThermometer

## Usage

```
❯ npm install
[...]
❯ node scan-thermometer.js
Sat Jan 09 2021 12:27:49 GMT+0900 (Japan Standard Time) ATC_C1CADA T=24.4, H=35% Batt=100%
```
The program terminates after 60s

### Options

```
❯ node scan-thermometer.js -h
Usage: scan-thermometer [options]

Options:
  -d, --debug             extra debugging
  -t, --timeout <value>   timeout in seconds
  -a, --allow-duplicates  show duplicate device discoveries
  -u, --uuids             Show all UUIDs (default: only 181a)
  -h, --help              display help for command
```

### Notes

Sometimes the device name is not defined (shows as "undefined" instead of "ATC_C1CADA" in above example), but if duplicates are not allowed, it'll not show up again with its correct name. Using "--allow-duplicates" will usually show the correct device name at the 2nd message and any subsequent received message.

node needs to have permission to to raw connecta to the network, so either use sudo:
```
❯ sudo node scan-thermometer.js
```
or set capabilities for the node binary to allow raw connects to the network:
```
❯ sudo setcap cap_net_raw+eip $(eval readlink -f `which node`)
```
and then you don't need sudo anymore.
