import tinytuya.scanner
from tinytuya import Device as TinyTuyaDevice
from datetime import datetime
import LibPython
import Tuya

SCAN_INTERVAL=10
class Scanner(LibPython.AsyncTask):     
  def __init__(self):
    super().__init__('Scanner',30)
    from . import Logger
    self.Logger = LibPython.Logger(self.Name,Logger)

  async def Begin(self)->bool:
    return True
  
  async def End(self):
    for d in Tuya.Devices:
      if d.IsConnected: await d.Disconnect()

  async def Run(self)->None:
    _ScanResult = await LibPython.Utility.RunSync(tinytuya.scanner.devices,verbose=False,poll=False)
    for _ScanData in _ScanResult.values():
      _Device = Tuya.Devices.Get(_ScanData['id'])
      if not _Device:
        #self.Logger.Warning(f'Unknown device detected {str(_ScanData)}')
        continue
      _Device.Detected = datetime.now()
      _Device.IP = _ScanData['ip']
      _Device.Version = _ScanData['version']
      self.Logger.Debug(f'Detected {_Device.Name}')
      if not _Device.IsRegistered: continue
      await _Device.OnDetect()
      if _Device.IsGateway:
        #Check if there are any subdevices that dont have a gateway defined and try if this is the gateway
        for _SubDevice in [x for x in Tuya.Devices if x.NodeID is not None and x._Gateway is None]:
          if not hasattr(_SubDevice,'_InvalidGateways'): _SubDevice._InvalidGateways = []
          if _Device.ID in _SubDevice._InvalidGateways: continue
          _SubDevice._InvalidGateways.append(_Device.ID)
          self.Logger.Info(f'Testing if {_Device.Name} is gateway for {_SubDevice.Name}')
          _Client = TinyTuyaDevice(_Device.ID,address=_Device.IP,local_key=_Device.LocalKey or _SubDevice.LocalKey,version=float(_Device.Version),cid=_SubDevice.NodeID)
          if not _Client: continue
          _Response = await LibPython.Utility.RunSync(_Client.status)
          _Client.close()
          if _Response and 'Err' not in _Response:
            _SubDevice._Gateway = _Device.ID
            self.Logger.Info(f'Set {_Device.Name} as gateway for {_SubDevice.Name}') 
        for _SubDevice in _Device.SubDevices:
          self.Logger.Debug(f'Detected SubDevice {_SubDevice.Name}')
          _Device.Detected = datetime.now()
          _Device.IP = _ScanData['ip']
          _Device.Version = _ScanData['version']
          if _SubDevice.IsRegistered: await _SubDevice.OnDetect()
    return True

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
  
