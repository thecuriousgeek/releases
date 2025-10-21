import asyncio
import LibPython
import LibHass

class Entity(LibHass.Entity):
  def __init__(self,*args,**kwargs):
    _Param = args[0] if args else LibPython.Dynamic(**kwargs)
    LibHass.Entity.__init__(self,_Param)
    from . import Logger
    self.Logger = LibPython.Logger(self.FullName,Logger)
    self.Service = _Param.Service
    self.Characteristic = _Param.Characteristic
    self.Category = _Param.Category
    self.Unit = _Param.Unit
    self.Code = _Param.Code
    self.Handle = None


class Sensor(Entity,LibHass.Sensor):
  def __init__(self,*args,**kwargs):
    _Param = args[0] if args else LibPython.Dynamic(**kwargs)
    Entity.__init__(self,_Param)
    LibHass.Sensor.__init__(self,_Param)


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
    if self.Device and self.Device.IsConnected:
      LibHass.RunInLoop(self.OnValue(pCommand))
      LibHass.MainLoop.run_in_executor(None,lambda:self.Device.Monitor.Client.write_gatt_char(self.Handle,self.Value.to_bytes(1,'big')))
    await LibHass.Switch.OnCommand(self,pCommand)


class Text(Entity,LibHass.Text):
  def __init__(self,*args,**kwargs):
    _Param = args[0] if args else LibPython.Dynamic(**kwargs)
    Entity.__init__(self,_Param)
    LibHass.Switch.__init__(self,_Param)

  async def OnCommand(self,pCommand:str):
    if self.Device and self.Device.IsConnected:
      LibHass.RunInLoop(self.OnValue(pCommand))
      LibHass.MainLoop.run_in_executor(None,lambda:self.Device.Monitor.Client.write_gatt_char(self.Handle,bytes(self.Value)))
    await LibHass.Text.OnCommand(self,pCommand)


class Number(Entity,LibHass.Number):
  def __init__(self,*args,**kwargs):
    _Param = args[0] if args else LibPython.Dynamic(**kwargs)
    Entity.__init__(self,_Param)
    LibHass.Switch.__init__(self,_Param)

  async def OnCommand(self,pCommand:int):
    if self.Device and self.Device.IsConnected:
      await self.OnValue(int(pCommand))
      LibHass.MainLoop.run_in_executor(None,lambda:self.Device.Monitor.Client.write_gatt_char(self.Handle,self.Value.to_bytes(1,'big')))
    await LibHass.Number.OnCommand(self,pCommand)
