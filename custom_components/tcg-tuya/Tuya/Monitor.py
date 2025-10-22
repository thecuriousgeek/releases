from datetime import datetime
import asyncio
from tinytuya import Device as TinyTuyaDevice
import LibPython
import LibHass
import Tuya

class Monitor(LibPython.AsyncTask):
  def __init__(self,pDevice:Tuya.Device):
    super().__init__(f'Monitor.{pDevice.Name}')
    from . import Logger
    self.Logger = LibPython.Logger(self.Name,Logger)
    self.Device = pDevice
    self.Client = None
    self.HeartBeat = datetime.min
    # self.Device.RefreshInterval = 30

  async def Begin(self)->bool:
    self.Device.Updated = datetime.min #I want to refresh the first time
    if self.Device.IsSubDevice:
      _Parent = self.Device.Gateway
      self.Client = TinyTuyaDevice(_Parent.ID,address=_Parent.IP,local_key=_Parent.LocalKey or self.Device.LocalKey,version=float(_Parent.Version),cid=self.Device.NodeID)
    else:
      self.Client = TinyTuyaDevice(self.Device.ID,address=self.Device.IP,local_key=self.Device.LocalKey,version=float(self.Device.Version))
    if not self.Client: return False
    if not self.Device.IsSubDevice:
      LibHass.RunInLoop(self.Device.Entities.Get('IP').OnValue(self.Device.IP))
    self.Client.set_socketPersistent(True)
    LibHass.RunInLoop(self.Device.OnConnect())
    return True

  async def Run(self)->bool:
    if not self.Client: return False
    _Data = await LibPython.Utility.RunSync(self.Client.receive)
    if _Data: 
      if 'Err' in _Data and not _Data['Err']=='904': 
        self.Logger.Warning(f'Network error in receive:{str(_Data)}')
        return False
      if 'dps' in _Data:
        self.UpdateEntities(_Data)
      return True
    if not self.Client: return False
    if (datetime.now()-self.HeartBeat).total_seconds()>10: 
      await LibPython.Utility.RunSync(self.Client.heartbeat)
      self.HeartBeat = datetime.now()
    if not self.Client: return False
    if (datetime.now()-self.Device.Refreshed).total_seconds()>self.Device.RefreshInterval:
      self.Logger.Info(f'Not updated since {str(self.Device.Refreshed)}, Refreshing')
      return await self.Refresh()
    if (datetime.now()-self.Device.Refreshed).total_seconds()>self.Device.ExpiryInterval:
      self.Logger.Warning(f'Not updated since {str(self.Device.Refreshed)}, Disconnecting')
      return False
    await asyncio.sleep(1.0)    
    return True

  async def End(self)->None:
    if self.Client: self.Client.close()
    self.Client = None
    # if self.Device.IsGateway:
    #   for _SubDevice in self.Device.SubDevices:
    #     LibHass.RunInLoop(_SubDevice.OnDisconnect())
    LibHass.RunInLoop(self.Device.OnDisconnect())

  async def Disconnect(self)->None:
    if self.Client: self.Client.close()
    self.Client = None
    if self.Device.IsGateway:
      for _SubDevice in self.Device.SubDevices:
        LibHass.RunInLoop(_SubDevice.OnDisconnect())
    LibHass.RunInLoop(self.Device.OnDisconnect())

  async def Refresh(self)->bool:
    if self.Device.IsGateway:
      _ChildStatus = await LibPython.Utility.RunSync(self.Client.subdev_query)
      if _ChildStatus and 'data' in _ChildStatus:
        if 'online' in _ChildStatus['data']: 
          for d in _ChildStatus['data']['online']:
            _Child = Tuya.Devices.GetNode(d)
            if _Child: _Child._Gateway = self.Device.ID
            # if _Child.IsConnected:
            #   LibHass.RunInLoop(BaseDevice.OnRefresh(_Child))
        if 'offline' in _ChildStatus['data']: 
          for d in _ChildStatus['data']['offline']:
            _Child = Tuya.Devices.GetNode(d)
            if _Child: _Child._Gateway = self.Device.ID
            # if _Child.IsConnected:
            #   LibHass.RunInLoop(LibHass.Device.Disconnect(_Child))
      LibHass.RunInLoop(LibHass.Device.OnRefresh(self.Device))
      return True
    _Status = await LibPython.Utility.RunSync(self.Client.status)
    if not _Status:
      return True
    if 'Err' in _Status:
      self.Logger.Warning(f'Network error in status:{str(_Status)}')
      return False
    _UpdatedEntities = self.UpdateEntities(_Status)
    LibHass.RunInLoop(LibHass.Device.OnRefresh(self.Device))
    return True
 
  def UpdateEntities(self,pStatus):
    _UpdatedEntities=[]
    if not 'dps' in pStatus:
      return _UpdatedEntities
    if 'Payload' in pStatus and not pStatus['Payload']: #Try again in next cycle with just receive
      self.Logger.Warning(f'No Payload:{str(pStatus)}')
      return _UpdatedEntities
    self.Device.Updated = datetime.now()
    _Device = self.Device
    if 'cid' in pStatus:
      _Device = Tuya.Devices.GetNode(pStatus['cid'])
      if not _Device: return _UpdatedEntities
    for k,v in pStatus['dps'].items():
      e = _Device.Entities.Get(k)
      if not e: continue
      LibHass.RunInLoop(e.OnValue(v))
      _UpdatedEntities.append(e.Name)
    _Device.Logger.Info(f'Updated:{len(_UpdatedEntities)} entities ({','.join(_UpdatedEntities)})')
    return _UpdatedEntities
    
