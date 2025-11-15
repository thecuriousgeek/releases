from abc import ABC, abstractmethod
from datetime import datetime
import LibPython
from . import IS_ADDON
if IS_ADDON:
  import homeassistant.const
  from homeassistant.components.binary_sensor import BinarySensorEntity as HassBinarySensor
  from homeassistant.components.sensor import SensorEntity as HassSensor
  from homeassistant.components.switch import SwitchEntity as HassSwitch
  from homeassistant.components.button import ButtonEntity as HassButton
  from homeassistant.components.number import NumberEntity as HassNumber
  from homeassistant.components.text import TextEntity as HassText
  from homeassistant.const import UnitOfTemperature
  from homeassistant.config_entries import ConfigEntry
  from homeassistant.helpers import entity_registry,entity_component
  from homeassistant.helpers.restore_state import RestoreEntity,ExtraStoredData
  from homeassistant.components import ffmpeg
else:
  from LibPython import Dummy as HassSensor
  from LibPython import Dummy as HassBinarySensor
  from LibPython import Dummy as HassSwitch
  from LibPython import Dummy as HassButton
  from LibPython import Dummy as HassNumber
  from LibPython import Dummy as HassText
  class RestoreEntity:
    pass
  class ExtraStoredData:
    pass


class Entity(ABC):
  def __init__(self,*args,**kwargs):
    _Param = args[0] if args else LibPython.Dynamic(**kwargs)
    self.ID = _Param.ID.upper()
    self.Name = _Param.Name
    self.Device = _Param.Device
    self.Category = _Param.Category
    self.Parent = _Param.Parent
    self.Unit = _Param.Unit
    self.__Value = _Param.Value
    self.Enabled = _Param.Enabled
    self.Virtual = _Param.Virtual #Virtual entities dont update Updated
    self.Updated = datetime.min
    self.EntityID=None
    self.Delta = 1.0 #Percent change below which is not reported
    self.Interval = 60 #Update interval to update even if delta is not met
    self.InHass = False
    if IS_ADDON:
      self._no_platform_reported=True
    self.Logger = LibPython.Logger(f'{self.FullName}')

  def __repr__(self):
    return f'{self.FullName} {self.ID}={self.Value}'

  @property
  def Type(self):
    return self.__class__.__name__

  @property
  def FullName(self):
    return '.'.join([self.Device.Name if self.Device else 'UnknownDevice',self.Name])

  @property
  def HasCommand(self):
    return hasattr(self,'OnCommand')

  @property
  def Value(self):
    return self.__Value
  
  @property
  def name(self):
    return self.Name

  @property
  def device_class(self):
    return self.Category

  @property
  def available(self):
    return self.Device and self.Device.IsConnected

  @property
  def should_poll(self):
    return False

  @property
  def unique_id(self):
    #return f'{Global.Domain}_{self.entity_id}'.replace('.','_')
    return f'{self.FullName}'.replace('.','_')

  @property
  def entity_id(self):
    if not self.EntityID: self.EntityID = f"{self.Platform}.{self.Device.Name.lower().replace(' ','_')}_{self.Name.lower().replace(' ','_')}"
    #self.Logger.Warning(f'entity_id:{self.EntityID}')
    return self.EntityID
  @entity_id.setter
  def entity_id(self,v):
    self.EntityID = v
    #self.Logger.Warning(f'entity_id=>{self.EntityID}')
  
  async def async_will_remove_from_hass(self):
    self.Logger.Debug('remove_from_hass')

  @property
  def extra_state_attributes(self):
    return {"last_update": self.Updated}

  async def RestoreState(self):
    self.Logger.Debug('Nothing to restore')

  async def Update(self):
    if not IS_ADDON: return
    if self.Device.IsRegistered: await self._Update()
  async def _Update(self):
    if self.InHass: self.async_write_ha_state()
    #if self.hass: self.async_schedule_update_ha_state()
    
  async def OnConnect(self)->None:    
    await self.Update()

  async def OnDisconnect(self)->None:
    self.__Value = None
    await self.Update()

  #When the entity changes its value
  async def OnValue(self,pValue)->bool:
    if not self.Virtual: self.Device.Updated = datetime.now()
    _Ignore = False
    if self.__Value is not None:
      if self.__Value==pValue and \
         (datetime.now()-self.Updated).total_seconds()<=self.Interval:
        self.Logger.Debug(f'Insignificant change - ignoring')
        _Ignore = True
      elif (isinstance(pValue,int) or isinstance(pValue,float)) and \
         abs((self.__Value-pValue))<=(self.__Value*self.Delta/100.0) and  \
         (datetime.now()-self.Updated).total_seconds()<=self.Interval:
        self.Logger.Debug(f'Insignificant change - ignoring')
        _Ignore = True
    if not _Ignore:
      self.Updated = datetime.now()
      self.__Value = pValue
      if self.Enabled:
        self.Logger.Debug(f'Value:{str(self.Value)}')
        await self.Update()
    for e in [x for x in self.Device.Entities if x.Parent and x.Parent.ID==self.ID]:
      if e.Code:
        try: 
          if pValue is not None: await e.OnValue(eval(e.Code,{'v':pValue}))
        except Exception as x:
          e.Logger.Exception('Cannot decode value',x)
      else:
        await e.OnValue(pValue)
    return True

  #When the entity needs to be sent a command
  async def OnCommand(self,pCommand=None)->bool:
    self.Logger.Debug(f'Command:{str(pCommand)}')


class Sensor(Entity,HassSensor):
  Platform='sensor'
  def __init__(self,*args,**kwargs):
    _Param = args[0] if args else LibPython.Dynamic(**kwargs)
    Entity.__init__(self,_Param)
    HassSensor.__init__(self)

  @property
  def native_value(self):
    return self.Value

  CLASS_MAP={'temperature':'measurement',
             'humidity':'measurement',
             'battery':'measurement',
             'voltage':'measurement',
             'power':'measurement',
             'energy':'total',
             'current':'measurement',
             'signal_strength':'measurement',
            }
  @property
  def state_class(self):
    if self.Category in Sensor.CLASS_MAP: return Sensor.CLASS_MAP[self.Category]
    if isinstance(self.Value,int): return "Int"
    if isinstance(self.Value,float): return "Float"
    return None

  UNIT_MAP={'temperature':'°C',
            'humidity':'%',
            'battery':'%',
            'voltage':'V',
            'power':'W',
            'energy':'kWh',
            'current':'A',
            'signal_strength':'dB'}
  @property
  def native_unit_of_measurement(self):
    if self.Unit: return self.Unit
    if self.Category in Sensor.UNIT_MAP: return Sensor.UNIT_MAP[self.Category]
    return None
  
  async def OnValue(self, pValue) -> bool:
    return await Entity.OnValue(self,pValue)
  
  async def OnCommand(self, pCommand=None) -> bool:
    raise f'{self.FullName} cannot receive commands'


class BinarySensor(Entity,HassBinarySensor):
  Platform='binary_sensor'
  def __init__(self,*args,**kwargs):
    _Param = args[0] if args else LibPython.Dynamic(**kwargs)
    Entity.__init__(self,_Param)
    HassBinarySensor.__init__(self)

  @property
  def is_on(self):
    return self.Value

  async def OnValue(self, pValue) -> bool:
    return await Entity.OnValue(self,pValue)
  
  async def OnCommand(self, pCommand=None) -> bool:
    raise f'{self.FullName} cannot receive commands'


class Button(Entity,HassButton):
  Platform='button'
  def __init__(self,*args,**kwargs):
    _Param = args[0] if args else LibPython.Dynamic(**kwargs)
    Entity.__init__(self,_Param)
    HassButton.__init__(self)

  @property
  def is_on(self):
    return self.Value

  async def OnValue(self, pValue) -> bool:
    return await Entity.OnValue(self,pValue)
  
  async def OnCommand(self, pCommand=None) -> bool:
    raise f'{self.FullName} cannot receive commands'


class Switch(Entity,HassSwitch):
  Platform='switch'
  def __init__(self,*args,**kwargs):
    _Param = args[0] if args else LibPython.Dynamic(**kwargs)
    Entity.__init__(self,_Param)
    HassSwitch.__init__(self)

  @property
  def is_on(self):
    return self.Value==True

  async def async_turn_on(self, **kwargs) -> None:
    await self.OnCommand(True)

  async def async_turn_off(self, **kwargs) -> None:
    await self.OnCommand(False)

  @abstractmethod
  async def OnCommand(self, pCommand=None) -> bool:
    await Entity.OnCommand(self,pCommand)

class Text(Entity,HassText):
  Platform='text'
  def __init__(self,*args,**kwargs):
    _Param = args[0] if args else LibPython.Dynamic(**kwargs)
    Entity.__init__(self,_Param)
    HassSensor.__init__(self)

  @property
  def native_value(self):
    return self.Value

  def set_value(self,pValue):
    self.OnCommand(pValue)

  @abstractmethod
  async def OnCommand(self, pCommand=None) -> bool:
    await Entity.OnCommand(self,pCommand)


class Number(Entity,HassNumber):
  Platform='number'
  def __init__(self,*args,**kwargs):
    _Param = args[0] if args else LibPython.Dynamic(**kwargs)
    Entity.__init__(self,_Param)
    HassSensor.__init__(self)

  @property
  def native_value(self):
    return self.Value

  def set_value(self,pValue):
    self.OnCommand(pValue)

  @abstractmethod
  async def OnCommand(self, pCommand=None) -> bool:
    await Entity.OnCommand(self,pCommand)


class Energy(Sensor,RestoreEntity,ExtraStoredData):
  def __init__(self,*args,**kwargs):
    _Param = args[0] if args else LibPython.Dynamic(**kwargs)
    Sensor.__init__(self,_Param)
    self.Power=0.0
    self.Today=0.0
    self.Total=0.0

  def as_dict(self):
    return {'Power':self.Power,'Today':self.Today,'Total':self.Total,'Updated':self.Updated.strftime('%Y-%m-%d %H:%M:%S')}

  @property
  def extra_state_attributes(self):
    _Result = {
      "Total" : self.Total,
      "Today" : self.Today,
    }
    return _Result

  @property
  def extra_restore_state_data(self):
    return self

  async def RestoreState(self):
    try:
      d = await self.async_get_last_extra_data()
      if d:
        d = d.as_dict()
        self.Updated = datetime.strptime(d['Updated'],'%Y-%m-%d %H:%M:%S') if 'Updated' in d else datetime.min
        self.Today = d['Today'] if 'Today' in d else 0.0
        self.Total = d['Total'] if 'Total' in d else 0.0
        self.Power = d['Power'] if 'Power' in d else 0.0
        await Sensor.OnValue(self,self.Today)
        self.Logger.Debug(f'Restoring state to Total:{self.Total}kWh, Today:{self.Today}kWh, Power:{self.Power}W as of {str(self.Updated)}')
      else:
        self.Logger.Debug(f'No state to restore')
    except Exception as e: self.Logger.Exception('RestoreState',e)

  async def OnValue(self,pValue:int):
    v = 0.0
    if not self.Updated==datetime.min:
      v = self.Power*(datetime.now().astimezone()-self.Updated.astimezone()).total_seconds()/3600000
    self.Power = pValue
    if not self.Updated.day==datetime.now().day: 
      self.Today=0.0
      await Sensor.OnValue(self,self.Today)
    else:
      self.Today = round(self.Today+v,2)
    self.Total = round(self.Total+v,2)
    await Sensor.OnValue(self,self.Today)


class EntityCollection(list[Entity]):
  def __init__(self,pDevice):
    self.Logger = LibPython.Logger(f'EntityCollection({pDevice.Name})')
    self.Device = pDevice
    super().__init__()

  def Add(self,pEntity:Entity|list[Entity]):
    if not isinstance(pEntity,list): pEntity=[pEntity]
    for e in pEntity:
      if not any(x for x in self if x.ID.upper()==e.ID.upper()):
        self.append(e)
        e.Device = self.Device
        e.Logger = LibPython.Logger(f'{e.FullName}')

  def Remove(self,pID:str):
    d = next((x for x in self if x.ID.upper()==pID.upper()),None) or next((x for x in self if x.Name.upper()==pID.upper()),None)
    if d: self.remove(d)

  def Get(self,pID:str)->Entity:
    return next((x for x in self if x.ID.upper()==pID.upper()),None) or next((x for x in self if x.Name.upper()==pID.upper()),None)

  def Clear(self,):
    self.clear()

  def __repr__(self)->str:
    return str.join(',',(f'{x.Name}:{x.Value}' for x in self if x.Enabled))
