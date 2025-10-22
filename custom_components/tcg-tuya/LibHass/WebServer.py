import os
from datetime import datetime
from fastapi import Request,Response
from typing import Optional
import LibPython
import LibHass

class WebServer(LibPython.WebServer):
  def __init__(self,**kwargs):
    self.Platforms = []
    super().__init__(Root=f'{os.path.dirname(__file__)}/Web',**kwargs)
    self.AddRoute('/api/debug','Debug',self.Debug,['GET'])
    self.AddRoute('/api/device/{pID}','GetDevice',self.GetDevice,['GET'])
    self.AddRoute('/api/device/{pID}','SetDevice',self.SetDevice,['PUT'])
    self.AddRoute('/api/refresh/{pID}','Refresh',self.Refresh,['GET'])
    self.AddRoute('/api/register/{pID}','Register',self.Register,['POST','DELETE'])
    self.AddRoute('/api/devices','Devices',self.GetDevices,['GET'])
    self.AddRoute('/{pFile:path}','SendFile',self.SendFile,['GET'])

  def _GetDevice(self,pID:str)->LibHass.Device:
    for _Platform in self.Platforms:
      d = _Platform.Devices.Get(pID)
      if d: return d
    return None
  def _GetPlatform(self,pID:str):
    for _Platform in self.Platforms:
      d = _Platform.Devices.Get(pID)
      if d: return _Platform
    return None

  async def Debug(self)->None:
    import debugpy
    debugpy.listen(('0.0.0.0',5678))
    print('Waiting for debugger')
    debugpy.wait_for_client()
    
  async def Refresh(self,pID:str)->None:
    _Device = self._GetDevice(pID)
    if not _Device: return Response('No such device',404)
    if not _Device.IsConnected: return Response('Device not connected',404)
    if not _Device.Monitor:  return f'{_Device.Name} not monitored'
    LibHass.RunInLoop(_Device.Monitor.Refresh(),_Device.Monitor.Loop)
    return f'Refreshed {_Device.Name}'

  def GetDevice(self,pID:str):
    _Device = self._GetDevice(pID)
    if not _Device: return Response('No such device',404)
    return LibPython.Dynamic(Name=_Device.Name, ID=_Device.ID, Category=_Device.Category, Updated=_Device.Updated, Refreshed=_Device.Refreshed, Entities=[LibPython.Dynamic(Type=x.Type, Name=x.Name, ID=x.ID, Value=str(x.Value), Updated=x.Updated, Command=hasattr(x,'OnCommand')) for x in _Device.Entities])

  async def SetDevice(self,request:Request,pID:str,pData:Optional[dict]=None):
    _Device = self._GetDevice(pID)
    if not _Device: return Response('No such device',404)
    if not _Device.IsConnected: return Response('Device not connected',404)
    e = pData['Entity']
    _Entity = _Device.Entities.Get(e['ID'])
    if not _Entity: return Response('No such entity',404)
    try:
      if isinstance(_Entity,LibHass.Switch):
        LibHass.RunInLoop(_Entity.OnCommand(e['Value'].upper() in ['1','ON','TRUE']))
      elif isinstance(_Entity,LibHass.Button):
        LibHass.RunInLoop(_Entity.OnCommand())
      elif isinstance(_Entity,LibHass.Number):
        LibHass.RunInLoop(_Entity.OnCommand(int(e['Value'])))
      else:
        LibHass.RunInLoop(_Entity.OnCommand(e['Value']))
      return 'OK'
    except Exception as x:
      return Response(str(x),500)

  def GetDevices(self):
    _Result = []
    _Devices = []
    for p in self.Platforms:
      for d in p.Devices:
        _Device = LibPython.Dynamic()
        _Device.Name = d.Name
        _Device.ID = d.ID
        _Device.Category = d.Template.Name if d.Template else d.Category
        _Device.IsRegistered = d.IsRegistered
        _Device.IsDetected = d.Detected>datetime.min
        _Device.IsConnected = d.IsConnected
        _Device.Updated = d.Updated.strftime('%H:%M:%S')
        _Device.Detected = d.Detected.strftime('%H:%M:%S')
        _Device.Connected = d.Connected.strftime('%H:%M:%S')
        _Device.Refreshed = d.Refreshed.strftime('%H:%M:%S')
        _Device.Entities = str(d.Entities)
        _Result.append(_Device)
    _Result.sort(key=lambda d:d.Updated,reverse=True)
    return _Result

  async def Register(self,request:Request,pID:str):
    _Device = self._GetDevice(pID)
    if request.method=='DELETE':
      if not _Device: return Response('No such device',404)
      if not _Device.IsRegistered: return Response('Device not registered',404)
      if _Device.IsConnected: await _Device.Disconnect()
      await self._GetPlatform(pID).Remove(_Device)
      return f'{_Device.Name} deregistered'
    elif request.method=='POST':
      if not _Device: return Response('No such device',404)
      if  _Device.IsRegistered: return Response('Device already registered',404)
      await self._GetPlatform(pID).Add(_Device)
      return f'{_Device.Name} registered'
    return Response('Invalid method',400)


_Instance = None
def Start():
  global _Instance
  if _Instance: _Instance.Stop()
  _Instance = WebServer()
  _Instance.Start()

def IsRunning()->bool: return _Instance is not None

def Stop():
  global _Instance
  if _Instance: _Instance.Stop()
  _Instance = None

def AddPlatform(pPlatform):
  if not _Instance: raise 'Not started yet'
  _Instance.Platforms.append(pPlatform)