import base64
import asyncio
import LibPython
import LibHass

class Entity(LibHass.Entity):
  def __init__(self,*args,**kwargs):
    _Param = args[0] if args else LibPython.Dynamic(**kwargs)
    LibHass.Entity.__init__(self,_Param)
    from . import Logger
    self.Logger = LibPython.Logger(self.FullName,Logger)
    self.Unit = _Param.Unit
    self.Code = _Param.Code


class Sensor(Entity,LibHass.Sensor):
  def __init__(self,*args,**kwargs):
    _Param = args[0] if args else LibPython.Dynamic(**kwargs)
    Entity.__init__(self,_Param)
    LibHass.Sensor.__init__(self,_Param)
    self.Scale = _Param.Scale

  async def OnValue(self,pValue):
    await LibHass.Sensor.OnValue(self,pValue/self.Scale if pValue and self.Scale else pValue)


class RawSensor(Entity,LibHass.Sensor):
  def __init__(self,*args,**kwargs):
    _Param = args[0] if args else LibPython.Dynamic(**kwargs)
    Entity.__init__(self,_Param)
    LibHass.Sensor.__init__(self,_Param)

  async def OnValue(self,pValue):
    await LibHass.Sensor.OnValue(self,base64.b64decode(pValue) if pValue else pValue)


class BinarySensor(Entity,LibHass.BinarySensor):
  def __init__(self,*args,**kwargs):
    _Param = args[0] if args else LibPython.Dynamic(**kwargs)
    Entity.__init__(self,_Param)
    LibHass.BinarySensor.__init__(self,_Param)


class Button(Entity,LibHass.Button):
  def __init__(self,*args,**kwargs):
    _Param = args[0] if args else LibPython.Dynamic(**kwargs)
    Entity.__init__(self,_Param)
    LibHass.Button.__init__(self,_Param)


class Switch(Entity,LibHass.Switch):
  def __init__(self,*args,**kwargs):
    _Param = args[0] if args else LibPython.Dynamic(**kwargs)
    Entity.__init__(self,_Param)
    LibHass.Switch.__init__(self,_Param)

  async def OnCommand(self,pCommand:bool):
    if not self.Device or not self.Device.IsConnected:
      raise 'Device not connected'
    _Command=pCommand
    if self.Code: #Custom code to send
      try:
        _Command = eval(self.Code,{'v':pCommand})
      except Exception as x:
        self.Logger.Error('Cannot send command')
    LibHass.MainLoop.run_in_executor(None,lambda:self.Device.Monitor.Client.set_value(self.Parent.ID if self.Parent else self.ID,_Command,True))
    await self.OnValue(pCommand)


class Text(Entity,LibHass.Text):
  def __init__(self,pEntity):
    Entity.__init__(self,pEntity)
    LibHass.Text.__init__(self,pEntity)

  async def OnCommand(self,pCommand:str):
    await self.OnValue(pCommand)
    if self.Device and self.Device.IsConnected:
      LibHass.MainLoop.run_in_executor(None,lambda:self.Device.Client.set_value(self.ID,self.Value,True))


class Number(Entity,LibHass.Number):
  def __init__(self,pEntity):
    Entity.__init__(self,pEntity)
    LibHass.Number.__init__(self,pEntity)

  async def OnCommand(self,pCommand:int):
    await self.OnValue(pCommand)
    if self.Device and self.Device.IsConnected:
      LibHass.MainLoop.run_in_executor(None,lambda:self.Device.Client.set_value(self.ID,self.Value,True))


class Energy(Entity,LibHass.Energy):
  def __init__(self,pEntity):
    Entity.__init__(self,pEntity)
    LibHass.Energy.__init__(self,pEntity)
