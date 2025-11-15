import asyncio
import threading
from datetime import datetime,timedelta
import time
from types import SimpleNamespace
import LibPython
import LibHass
import Bluetooth

class Device(LibHass.Device):  
  Poll=None

  def __init__(self,*args,**kwargs):
    _Param = args[0] if args else LibPython.Dynamic(**kwargs)
    LibHass.Device.__init__(self,_Param)
    from . import Logger
    self.Logger = LibPython.Logger(self.Name,Logger)
    self.Services = _Param.Services
    self.CreateEntities()
    self.Template = Bluetooth.Template.Get(self.Category,self.Name,self.Services)
    if self.Template: 
      self.Category = self.Template.ID
      Bluetooth.Template.LoadEntities(self)
    self.Monitor = None

  @property
  def IsConnected(self)->bool:
    if not self.Template.Connect: return (datetime.now()-self.Refreshed).total_seconds() < self.ExpiryInterval
    return self.Monitor is not None    

  def CreateEntities(self):
    _Entity = Bluetooth.Sensor(Name='Signal',ID='SIGNAL',SubType='signal_strength',Enabled=True,Virtual=True)         
    self.Entities.Add(_Entity)
                          
  async def OnDetect(self,pSignal:int,pData:dict[str:bytes])->None:
    _UpdatedEntities = await Bluetooth.Template.Parse(self,pData)
    await self.Entities.Get("SIGNAL").OnValue(pSignal)
    if not self.Template.Connect: 
      self.Logger.Debug(f'Updated:{len(_UpdatedEntities)} entities ({','.join(_UpdatedEntities)})')
      await LibHass.Device.OnRefresh(self)
    await LibHass.Device.OnDetect(self)

  async def Connect(self)->bool:
    if self.Monitor: return True #Already connected, or connectin in progress
    if not self.Template.Connect: return True #BLE device
    self.Monitor = Bluetooth.Monitor(self)
    self.Monitor.Start()
    return True

  async def Disconnect(self)->None:
    if self.Monitor:
      LibHass.RunInLoop(self.Monitor.Disconnect(),self.Monitor.Loop)
    else:
      LibHass.RunInLoop(self.OnDisconnect())

  async def OnDisconnect(self)->None:
    # if self.Monitor: 
    #   self.Monitor.join()
    self.Monitor = None
    await LibHass.Device.OnDisconnect(self)

  async def Refresh(self):
    if self.Monitor: 
      LibHass.RunInLoop(self.Monitor.Refresh(),self.Monitor.Loop)
