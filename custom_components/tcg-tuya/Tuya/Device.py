import asyncio
import json
from tinytuya import Device as TinyTuyaDevice
import LibPython
import LibHass
import Tuya

class Device(LibHass.Device):
  def __init__(self,*args,**kwargs):
    _Param = args[0] if args else LibPython.Dynamic(**kwargs)
    LibHass.Device.__init__(self,_Param)
    from . import Logger
    self.Logger = LibPython.Logger(self.Name,Logger)
    self.Monitor = None
    self.Product = _Param.Product
    self.Model = _Param.Model
    self.Icon = _Param.Icon
    self._Gateway = _Param.Gateway
    self.NodeID = _Param.NodeID
    self.LocalKey = _Param.LocalKey
    self.Function = _Param.Function
    self.Status = _Param.Status
    self.IP = None #Set by Scanner on detection
    self.Version = None #Set by Scanner on detection
    self.CreateEntities(_Param.Entities)
    self.Template = Tuya.Template.Get(self.Category)
    if self.Template: Tuya.Template.LoadEntities(self)

  @property
  def IsGateway(self)->bool:
    return any(x for x in Tuya.Devices if x._Gateway and x._Gateway.upper()==self.ID.upper()) or self.Category in Tuya.GatewayCategories

  @property
  def SubDevices(self)->list:
    return [x for x in Tuya.Devices if x._Gateway and x._Gateway.upper()==self.ID.upper()] 

  @property
  def IsSubDevice(self)->bool:
    return True if self._Gateway else False

  @property
  def Gateway(self):
    if not self._Gateway: return None
    return Tuya.Devices.Get(self._Gateway)

  @property
  def IsConnected(self)->bool:
    return self.Monitor is not None

  def CreateEntities(self,pEntities:list):
    if not self.IsSubDevice:
      self.Entities.Add(Tuya.Sensor(ID='IP',Name='IP',Device=self,Enabled=True,Virtual=True))
      self.Entities.Add(Tuya.Sensor(ID='MACID',Name='MacID',Device=self,Virtual=True))
      self.Entities.Add(Tuya.Sensor(ID='VERSION',Name='Version',Device=self,Virtual=True))
    for e in pEntities:
      _Entity = None
      _Config = LibPython.Dynamic(e)
      _Config.Device = self
      _Config.Category = None
      if e.Type==Tuya.Sensor.__name__:
        _Entity = Tuya.Sensor(_Config)
      elif e.Type==Tuya.RawSensor.__name__:
        _Entity = Tuya.RawSensor(_Config)
      elif e.Type==Tuya.BinarySensor.__name__:
        _Entity = Tuya.BinarySensor(_Config)
      elif e.Type==Tuya.Switch.__name__:
        _Entity = Tuya.Switch(_Config)
      elif e.Type==Tuya.Number.__name__:
        _Entity = Tuya.Number(_Config)
      elif e.Type==Tuya.Text.__name__:
        _Entity = Tuya.Text(_Config)
      else: 
        continue
      self.Entities.Add(_Entity)

  async def OnDetect(self)->None:
    # if self.IsConnected: return
    # if not self.Entities.Get('MACID').Value==self.MacID: await self.Entities.Get('MACID').OnValue(self.MacID)
    # if not self.Entities.Get('VERSION').Value==self.Version: await self.Entities.Get('VERSION').OnValue(self.Version)
    await LibHass.Device.OnDetect(self)

  async def Connect(self)->bool:
    if self.Monitor: return True
    self.Monitor = Tuya.Monitor(self)
    self.Monitor.Start()
    return True

  async def Disconnect(self)->None:
    if self.Monitor:
      LibHass.RunInLoop(self.Monitor.Disconnect(),self.Monitor.Loop)
    else:
      LibHass.RunInLoop(self.OnDisconnect())

  async def OnDisconnect(self)->None:
    if self.Monitor: 
      self.Monitor.Stop()
    self.Monitor = None
    await LibHass.Device.OnDisconnect(self)

  async def Refresh(self):
    if self.Monitor: 
      LibHass.RunInLoop(self.Monitor.Refresh(),self.Monitor.Loop)
