import os
import LibPython
import LibHass 
Name=None
Logger=None
from .Device import Device
from .Entity import *
from .Template import Template
from . import Scanner
from .Monitor import Monitor
from . import Cloud as LibCloud

Config=None
Cloud=None
Devices=None
GatewayCategories=[
  "wgsxj",  # Gateway camera
  "lyqwg",  # Router
  "bywg",  # IoT edge gateway
  "zigbee",  # Gateway
  "wg2",  # Gateway
  "dgnzk",  # Multi-function controller
  "videohub",  # Videohub
  "xnwg",  # Virtual gateway
  "qtyycp",  # Voice gateway composite solution
  "alexa_yywg",  # Gateway with Alexa
  "gywg",  # Industrial gateway
  "cnwg",  # Energy gateway
  "wnykq",  # 
]

async def Init(pName:str,pHass)->None:
  global Name,Logger,Config,Cloud,Devices
  if Name: return
  Name = pName
  if not Logger: Logger = LibPython.Logger(Name)
  Config = LibHass.Config()
  Cloud = LibCloud.Cloud()
  Devices = LibHass.DeviceCollection()
  from importlib import import_module
  await LibHass.Init(pHass,import_module('Tuya'))
  Scanner.Start()
  
async def Reload()->None:
  os.remove('cloud.json')
  if LibHass.IS_ADDON: await LibHass.Hass.async_add_executor_job(Cloud.Load)
  else: Cloud.Load()
  
async def Restart()->None:
  Scanner.Stop()
  for d in Devices:
    if d.IsConnected: LibHass.RunInLoop(d.Disconnect())
  Scanner.Start()
  
async def Configure(pEntry):
  if LibHass.IS_ADDON: 
    await LibHass.Hass.async_add_executor_job(Cloud.Load)
  else: 
    if not Config.Cloud:
      Logger.Warning('Configure:No configuration found, starting authorization')
      Config.Cloud = Cloud.GetToken()
      Config.Devices = Config.Devices or []
    Cloud.Load()
  Devices.Clear()
  for d in Cloud.Devices or []:
    _Name = next((x.Name for x in Config.Devices if x.ID.upper()==d.ID.upper()),None)
    _Config = LibPython.Dynamic(d)    
    if _Name: Config.Name = _Name
    _Device = Device(_Config)
    _Device.IsRegistered = _Name is not None 
    Devices.Add(_Device)    
  for d in Config.Devices or []:
    if not (x.ID.upper()==d.ID.upper() for x in Cloud.Devices):
      Logger.Warning(f'Configure:Device {d.ID} not found in cloud')
  await LibHass.Component.Configure(pEntry,[x for x in Devices if x.IsRegistered])

async def UnConfigure(pEntry):
  await LibHass.Component.UnConfigure(pEntry,[x for x in Devices if x.IsRegistered])

async def Add(pDevice)->bool:
  pDevice.IsRegistered = True
  Config.Add(pDevice)

async def Remove(pDevice)->bool:
  pDevice.IsRegistered = False
  Config.Remove(pDevice)
