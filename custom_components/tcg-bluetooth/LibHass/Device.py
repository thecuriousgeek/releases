from abc import ABC, abstractmethod
from datetime import datetime
import LibPython
from . import IS_ADDON
if IS_ADDON:
  from homeassistant.helpers import device_registry,entity_registry
  from homeassistant.config_entries import ConfigEntry,ConfigEntryState,ConfigEntryDisabler
  import homeassistant.config_entries

class Device(ABC):
  RefreshInterval:int=180
  ExpiryInterval:int=600

  def __init__(self,*args,**kwargs):
    _Param = args[0] if args else LibPython.Dynamic(**kwargs)
    self.ID = _Param.ID.upper()
    self.Name = _Param.Name.upper()
    self.Category = _Param.Category
    self.Updated = datetime.min
    self.Detected = datetime.min
    self.Refreshed = datetime.min
    self.Connected = datetime.min
    self.IsRegistered = False
    self.DeviceID = None
    self.Template = None
    from .Entity import EntityCollection
    self.Entities = EntityCollection(self)
    self.Logger = LibPython.Logger(f'{self.Name}')

  def __repr__(self):
    return f'{self.Name} ID:{self.ID}, Registered:{self.IsRegistered}, Entities:{self.Entities}'

  @property
  def unique_id(self)->str:
    return f'{self.Name}'.replace(' ','_').replace('.','_')

  #Events
  async def OnDetect(self)->None:
    self.Logger.Debug('Detected')
    self.Detected = datetime.now()
    if not self.IsConnected:
      await self.Connect()

  async def OnConnect(self)->None:
    self.Logger.Info(f'Connected')
    self.Connected = datetime.now()
    for e in self.Entities:
      await e.OnConnect()

  async def OnDisconnect(self)->None:
    self.Logger.Warning(f'Disconnected')
    for e in self.Entities:
      await e.OnDisconnect()
  
  #Must implement
  @abstractmethod
  async def Connect(self)->bool: pass
  @abstractmethod
  async def Disconnect(self)->None: pass
  @abstractmethod
  async def Refresh(self)->None: pass
  @property
  @abstractmethod
  def IsConnected(self)->bool: pass
  #Optional methds can be overridden
  async def OnRefresh(self)->bool: self.Refreshed = datetime.now()    

class DeviceCollection(list[Device]):
  def __init__(self):
    self.Logger = LibPython.Logger('DeviceCollection')
    super().__init__()

  def Add(self,pDevice:Device|list[Device]):
    if isinstance(pDevice,Device):
      if any(x for x in self if x.ID==pDevice.ID): 
        self.Remove(pDevice.ID)
      self.append(pDevice)
    elif isinstance(pDevice,DeviceCollection):
      for d in pDevice:
        self.Add(d)

  def Remove(self,pID:str):
    d = next((x for x in self if x.ID.upper()==pID.upper()),None)
    if d: self.remove(d)

  def Get(self,pID:str)->Device:
    return next((x for x in self.__iter__() if x.ID.upper()==pID.upper()),None)

  def GetNode(self,pID:str)->Device:
    return next((x for x in self.__iter__() if x.NodeID and x.NodeID.upper()==pID.upper()),None)
  
  def Contains(self,pID:str)->bool:
    return any(x for x in self.__iter__() if x.ID.upper()==pID.upper())

  def Clear(self,):
    self.clear()
