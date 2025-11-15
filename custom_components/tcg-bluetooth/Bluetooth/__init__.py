import LibHass 
Name=None
Logger=None
from .Device import Device
from .Entity import *
from .Template import Template
if LibHass.IS_ADDON:
  from . import HassScanner as Scanner
else:
  from . import BleakScanner as Scanner
from .Monitor import Monitor

Config=None
Devices=None

async def Init(pName:str,pHass)->None:
  global Name,Logger,Config,Devices
  if Name: return
  Name = pName
  if not Logger: Logger = LibPython.Logger(Name)
  Config = LibHass.Config()
  Devices = LibHass.DeviceCollection()
  from importlib import import_module
  await LibHass.Init(pHass,import_module('Bluetooth'))
  Scanner.Start()
  
async def Reload()->None:
  return

async def Restart()->None:
  Scanner.Stop()
  for d in Devices:
    if d.IsConnected: LibHass.RunInLoop(d.Disconnect())
  Scanner.Start()

async def Configure(pEntry):
  Devices.clear()
  for d in Config.Devices or []:
    _Device = Device(d)
    Devices.Add(_Device)
    _Device.IsRegistered = True
  await LibHass.Component.Configure(pEntry,[x for x in Devices if x.IsRegistered])
  
async def UnConfigure(pEntry):
  await LibHass.Component.UnConfigure(pEntry,[x for x in Devices if x.IsRegistered])

async def Add(pDevice)->bool:
  pDevice.IsRegistered = True
  Config.Add(pDevice)

async def Remove(pDevice)->bool:
  pDevice.IsRegistered = False
  Config.Remove(pDevice)
