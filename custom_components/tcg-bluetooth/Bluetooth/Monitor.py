from datetime import datetime
import asyncio
import LibPython
import LibHass
import Bluetooth

MONITOR_INTERVAL=30
class Monitor(LibPython.AsyncTask):
  def __init__(self,pDevice:Bluetooth.Device):
    super().__init__(f'Monitor.{pDevice.Name}',MONITOR_INTERVAL)
    self.Device = pDevice
    self.Client = None

  async def Begin(self)->bool:
    try:
      if hasattr(self.Device,'BLEDevice'):
        self.Logger.Debug('Connecting BLEDevice')
        self.Client = Bluetooth.Scanner.GetClient(self.Device.BLEDevice,self.OnDisconnectSync)
      else:
        self.Logger.Debug('Connecting Address')
        self.Client = Bluetooth.Scanner.GetClient(self.Device.ID,self.OnDisconnectSync)
      if not self.Client:
        self.Logger.Warning('Cannot create client')
        return False
      await self.Client.connect()
      if not self.Client.is_connected:
        self.Logger.Warning('Cannot connect')
        del self.Client
        self.Client = None
        return False
      #self.__Client.pair()
    except Exception as x:
      if self.Client: #Some times disconnect happens automatically
        self.Logger.Exception('Connect exception',x)
        if self.Client.is_connected: self.Client.disconnect()
      self.Client = None
      return False
    for _Service in self.Client.services:
      for _Characteristic in _Service.characteristics:
        if not any (e for e in self.Device.Entities if e.Service and e.Service.upper() in _Service.uuid.upper() and e.Characteristic and e.Characteristic.upper() in _Characteristic.uuid.upper()):
          continue
        _Value=None
        if "read" in _Characteristic.properties:
          try:
            _Value = bytes(await self.Client.read_gatt_char(_Characteristic.handle))
          except Exception as x:
            self.Logger.Exception('GetValue',x)
        if "notify" in _Characteristic.properties:
          await self.Client.start_notify(_Characteristic.handle, self.OnNotify)
        for _Entity in [e for e in self.Device.Entities if e.Service and e.Service.upper() in _Service.uuid.upper() and e.Characteristic and e.Characteristic.upper() in _Characteristic.uuid.upper()]:
          _Entity.Handle = _Characteristic.handle
          if _Value and _Entity.Code:
            LibHass.RunInLoop(_Entity.OnValue(eval(_Entity.Code,None,{'v':_Value})))
    LibHass.RunInLoop(self.Device.OnConnect())
    return True

  async def Run(self)->bool:
    if not self.Client: return False
    if not self.Device.RefreshInterval>0: return True
    if self.Device.IsConnected and (datetime.now()-self.Device.Refreshed).total_seconds()>self.Device.RefreshInterval:
      self.Logger.Info(f'Not updated since {str(self.Device.Refreshed)}, Refreshing')
      return await self.Refresh()
    if self.Device.IsConnected and (datetime.now()-self.Device.Refreshed).total_seconds()>self.Device.ExpiryInterval:
      self.Logger.Warning(f'Not updated since {str(self.Device.Refreshed)}, Disconnecting')
      return False
    return True

  async def End(self)->None:
    await self.Disconnect()

  async def Disconnect(self)->None:
    if self.Client:
      for e in [x for x in self.Device.Entities if x.Handle]:
        try: await self.Client.stop_notify(e.Handle)
        except: pass
      try: await self.Client.disconnect()
      except: pass
    await self.OnDisconnect(self.Client)

  def OnDisconnectSync(self,pClient)->None: #Called from bleak callback, so cannot be async
    LibHass.RunInLoop(self.OnDisconnect(pClient),self.Loop)
  async def OnDisconnect(self,pClient)->None:
    self.Client = None
    LibHass.RunInLoop(self.Device.OnDisconnect())

  async def Refresh(self)->bool:
    for e in self.Device.Entities:
      if not e.Handle: continue
      try: _Value = bytes(await self.Client.read_gatt_char(e.Handle))
      except: continue
      if not _Value: continue
      if e.Code:
        LibHass.RunInLoop(e.OnValue(eval(e.Code,None,{'v':_Value})))
      else:
        LibHass.RunInLoop(e.OnValue(_Value))
    LibHass.RunInLoop(LibHass.Device.OnRefresh(self.Device))
    return True

  async def OnNotify(self,pSender,pData)->None:
    asyncio.ensure_future(self._OnNotify(pSender,pData),loop=LibHass.MainLoop)

  async def _OnNotify(self,pSender,pData)->None:
    _UpdatedEntities = []
    for _Entity in [e for e in self.Device.Entities if e.Handle==pSender.handle]:
      self.Updated = datetime.now()
      if isinstance(_Entity,Bluetooth.Button):
        _UpdatedEntities.append(_Entity.Name)
        await _Entity.OnValue(True)
        await asyncio.sleep(0.1)
        await _Entity.OnValue(False)
      elif _Entity.Code and pData:
        _UpdatedEntities.append(_Entity.Name)
        await _Entity.OnValue(eval(_Entity.Code,None,{'v':pData}))
#    if self.Poll is None:
#      return
#    #If all entities have been updated, disconnect so as to save battery
#    if all(x.Updated>self.Poll for x in self.Entities):
#      self.Logger.Info('All entities updated..Disconnecting')
#      await self.Disconnect()
#      self.Poll = datetime.now() + timedelta(0,self.RefreshInterval)
    self.Device.Logger.Debug(f'Updated:{len(_UpdatedEntities)} entities ({','.join(_UpdatedEntities)})')
