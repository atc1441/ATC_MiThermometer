const os = require("os");
const noble = require("@abandonware/noble");
const { program } = require("commander");

let debug = false;
let timeout = 60;
let uuid = '181a';
let allowDuplicates = false;

function doScanning(uuid, allowDuplicates, debug) {

  noble.on("stateChange", function (state) {
    if (debug) console.log(`StateChanged to ${state}`);
    if (state === "poweredOn") {
      if (debug) console.log('Start scanning');
      noble.startScanning(uuid=='all'?[]:[uuid], allowDuplicates);
    } else {
      if (debug) console.log('Stopped scanning');
      noble.stopScanning();
    }
  });

  noble.on("discover", function (peripheral) {
    if (debug) {
      console.log(`Peripheral discovered: Local name is: ${peripheral.advertisement.localName}`);
    }
    for (let sData of peripheral.advertisement.serviceData) {
      if (sData.uuid === '181a') {
        let temperature = sData.data.readIntBE(6, 2) / 10.0;
        let humidity = sData.data.readUInt8(8);
        let battery = sData.data.readUInt8(9);
        let now = new Date().toString();
        console.log(
          `${now} ${peripheral.advertisement.localName} T=${temperature}, H=${humidity}% Batt=${battery}%`
        );
      } else {
        console.log(`uuid=${sData.uuid} found with data: ${JSON.stringify(sData.data)}`);
      }
    }
  });
}


program
  .option("-d, --debug", "Show debug messages")
  .option("-t, --timeout <value>", "Stop after TIME seconds (default: 60)")
  .option("-a, --allow-duplicates", "Show all duplicate messages (default: only show once)")
  .option("-u, --uuids", "Show all UUIDs (default: only 181a)")
program.parse(process.argv);

if (program.debug) debug = true;
if (program.uuids) uuid="all";
if (program.timeout) timeout=parseInt(program.timeout);
if (program.allowDuplicates) allowDuplicates=true;

if (debug) {
  console.log("Debug on");
  console.log(`Timeout: ${timeout}s`);
  if (allowDuplicates)
    console.log("Show all discovered devices multiple times");
  else 
    console.log("Show discovered devices only once");
  if (uuid==="all")
    console.log("Showing all UUIDs");
  else
    console.log(`Only showing UUID ${uuid}`)
  console.log("");
}

doScanning(uuid, allowDuplicates, debug);

setTimeout(()=>{
  noble.stopScanning();
  process.exit(0);
}, timeout*10000);
