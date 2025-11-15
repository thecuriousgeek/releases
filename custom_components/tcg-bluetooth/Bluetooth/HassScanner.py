import asyncio
from datetime import datetime
from bleak import BleakClient
from homeassistant.components import bluetooth
from homeassistant.components.bluetooth import BluetoothScanningMode,BluetoothServiceInfoBleak,async_ble_device_from_address
import LibPython
import LibHass
import Bluetooth

SCAN_INTERVAL=10
class Scanner(LibPython.AsyncTask):
  _Events=None
  _Scanner=None
  _Done=[]

  def __init__(self):
    super().__init__('Bluetooth.HassScanner')

  async def Begin(self):
    self._Scanner = bluetooth.async_register_callback(LibHass.Hass,self.OnDetect,{},bluetooth.BluetoothScanningMode.ACTIVE)
    self._Events = [asyncio.create_task(self.CommandStop.wait())]
    return True

  async def End(self):
    self._Scanner #To remove the callback
    return True

  def OnDetect(self,pDevice,pType):
    if not LibHass.RunInLoop(self.OnDetectAsync(pDevice,pType)):
      self.CommandStop.set()

  async def OnDetectAsync(self,pDevice,pType):
    _Device = Bluetooth.Devices.Get(pDevice.address)
    if not _Device:
      _Device = Bluetooth.Device(ID=pDevice.address,Name=pDevice.name,Services=pDevice.service_uuids if len(pDevice.service_uuids)>0 else pDevice.service_data.keys())
    if not _Device.Template: return
    if not Bluetooth.Devices.Contains(_Device.ID): Bluetooth.Devices.Add(_Device)
    if not any (x for x in self._Done if x.Device.ID==_Device.ID):
      self._Done.append(LibPython.Dynamic(Device=_Device,Signal=pDevice.rssi,ServiceData=pDevice.service_data))
      self.Logger.Debug(f'Detected:{_Device.ID}({_Device.Name})')
      if _Device.IsRegistered:
        _Device.BLEDevice = async_ble_device_from_address(LibHass.Hass,_Device.ID,connectable=_Device.Template.Connect)
        await _Device.OnDetect(pDevice.rssi,pDevice.service_data)
      else:
        _Device.Detected = datetime.now()
    return

  async def Run(self)->bool:
    self._Done=[]
    await asyncio.wait(self._Events,timeout=SCAN_INTERVAL,return_when=asyncio.FIRST_COMPLETED)
    for _Device in Bluetooth.Devices:
      if not _Device.IsRegistered and (datetime.now()-_Device.Detected).total_seconds()>Bluetooth.Device.ExpiryInterval:
        Bluetooth.Devices.Remove(_Device.ID) #Detected but too old
      elif _Device.IsRegistered and not _Device.Template.Connect and _Device.Refreshed>datetime.min and (datetime.now()-_Device.Refreshed).total_seconds()>_Device.ExpiryInterval:
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
  
