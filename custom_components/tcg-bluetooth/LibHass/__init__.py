import asyncio
Hass=None
MainLoop=None
IS_ADDON=False
try:
  from homeassistant import core
  IS_ADDON=True
except:
  pass

async def Init(pHass,pPlatform):
  global MainLoop,Hass
  Hass = pHass
  MainLoop = asyncio.get_running_loop()
  if not WebServer.IsRunning(): WebServer.Start()
  WebServer.AddPlatform(pPlatform)

def RunInLoop(pWhat,pLoop=None)->bool:
  if not pLoop: pLoop = MainLoop
  if pLoop.is_running():
    asyncio.run_coroutine_threadsafe(pWhat,pLoop)
    return True
  return False

from datetime import datetime
import atexit
from threading import Thread,Event
from .Device import Device,DeviceCollection
from .Entity import *
from .Config import Config
from . import Component
from . import WebServer

def StartDebug():
  import debugpy
  debugpy.listen(('0.0.0.0',5678))
  print('Waiting for debugger')
  debugpy.wait_for_client()

Thread(target=StartDebug).start()