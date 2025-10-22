import sys
import signal
import asyncio
import json
import LibPython
LibPython.Logger.SetLevel(LibPython.Logger.LEVEL.INFO)
import LibHass
import Tuya

def Interrupt(sig, frame):
  print('Terminating due to interrupt')
  sys.exit(0)

async def main():
  await Tuya.Init('SmartHub.Tuya',None)
  await Tuya.Configure(None)
  signal.signal(signal.SIGINT, Interrupt)
  while True:
    await asyncio.sleep(1.0)

#There are 4 + #Tuya threads
# Main thread - Main thread or HASS thread
# WebApi.Thread - Thread for the web API server
# Scanner.Thread - Thread for scanning Tuya devices
# Device().Thread - Thread for monitoring each Tuya device
#Each thread also has an asyncio loop that can be called using asyncio.run_coroutine_threadsafe
# LibHass.MainLoop - Main loop started by this or by HASS
# Scanner.Loop - Loop for scanning Tuya devices
# Device().Loop - Monitor loop for each Tuya device

if __name__ == "__main__":
  asyncio.run(main())
