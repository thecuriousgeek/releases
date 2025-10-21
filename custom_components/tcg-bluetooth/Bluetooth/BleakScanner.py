from datetime import datetime
import asyncio
from bleak import BleakScanner,BleakClient
import LibPython
import LibHass
import Bluetooth

SCAN_INTERVAL=10
class Scanner(LibPython.AsyncTask):
  _Events=None
  _Scanner=None
  _Detected=[]

  def __init__(self):
    super().__init__('BleakScanner')

  async def Begin(self):
    self._Scanner = BleakScanner(detection_callback=self.OnDetect,scanning_mode='active')
    self._Events = [asyncio.create_task(self.CommandStop.wait())]
    await self._Scanner.start()
    return True

  async def End(self):
    await self._Scanner.stop()
    return True

  def OnDetect(self,pDevice,pData)->None:
    if not LibHass.RunInLoop(self.OnDetectAsync(pDevice,pData)):
      self.CommandStop.set()
    
  async def OnDetectAsync(self,pDevice,pData)->None:
    _Device = Bluetooth.Devices.Get(pDevice.address)
    if not _Device:
      _Device = Bluetooth.Device(
              ID=pDevice.address,
              Name=pData.local_name or pDevice.address,
              Services=(pData.service_uuids if len(pData.service_uuids)>0 else pData.service_data.keys()))
      Bluetooth.Devices.Add(_Device)
    if pData.local_name and _Device.Name==_Device.ID: #Just got the name
      _Device.Name = pData.local_name
    if not _Device.Template: #No templates, cant be processed
      Bluetooth.Devices.Remove(_Device.ID)
      return
    _Device.BLEDevice = pDevice
    if not any (x for x in self._Detected if x.Device.ID==_Device.ID):
      self._Detected.append(LibPython.Dynamic(Device=_Device,Signal=pData.rssi,ServiceData=pData.service_data))
      self.Logger.Debug(f'Detected:{_Device.ID}({_Device.Name})')
      if _Device.IsRegistered:
        await _Device.OnDetect(pData.rssi,pData.service_data)
      else:
        _Device.Detected = datetime.now()
    return

  async def Run(self)->bool:
    self._Detected = []
    await asyncio.wait(self._Events,timeout=SCAN_INTERVAL,return_when=asyncio.FIRST_COMPLETED)
    for _Device in Bluetooth.Devices:
      if (datetime.now()-_Device.Detected).total_seconds()<Bluetooth.Device.ExpiryInterval: continue
      if not _Device.IsRegistered:
        Bluetooth.Devices.Remove(_Device.ID) #Detected but too old
      elif _Device.IsRegistered and not _Device.Template.Connect and _Device.Refreshed>datetime.min:
        await _Device.Disconnect()
        _Device.Refreshed = datetime.min
    return not self.CommandStop.is_set()

def GetClient(pID:str,pOnDisconnect):
  return BleakClient(pID,disconnected_callback=pOnDisconnect,timeout=60)

_Instance = None
def Start():
  global _Instance
  if _Instance: _Instance.Stop()
  _Instance = Scanner()
  _Instance.Start()

def Stop():
  global _Instance
  if _Instance: _Instance.Stop()
  _Instance = None
