import os
import json
import LibPython
import LibHass

Devices=[]
async def Load(pData:dict=None):
  global Devices
  if pData: #HASS has provided the data
    _Data = LibPython.Dynamic(pData)
  elif os.path.exists('config.json'):
    _Data = LibPython.Dynamic(json.load(open('config.json','r')))
  else: return
  Devices = [x for x in _Data.Devices]

async def Save():
  s = json.dumps({'Devices':Devices},indent=2,sort_keys=True)
  if LibHass.IS_ADDON: return s
  open('config.json','w').write(s)

async def Add(pID):
  if any(x for x in Devices if x.ID==pID): raise 'Device already configured'
  from . import Devices as BluetoothDevices
  _Device = BluetoothDevices.Get(pID)
  if not _Device: raise 'Device not detected'
  Devices.append(LibPython.Dynamic(ID=_Device.ID,Name=_Device.Name,Category=_Device.Category))
  await Save()

async def Remove(pID):
  if not any(x for x in Devices if x.ID==pID): raise 'Device not configured'
  Devices.remove(next(x for x in Devices if x.ID==pID))
  await Save()
