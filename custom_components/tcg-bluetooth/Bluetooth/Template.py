import json
from types import SimpleNamespace
from pathlib import Path
from datetime import datetime
import asyncio
import LibPython
import Bluetooth
from . import BtHome

Logger = LibPython.Logger('Bluetooth.Template')
class Template():
  __All=None
  def Templates():
    if Template.__All is None:
      Template.__All=[LibPython.Dynamic(x) for x in json.loads(open('template.json','r').read())]
    return Template.__All

  def Get(pCategory,pName,pServices):
    for _Template in Template.Templates():
      if _Template.ID==pCategory:
        return _Template
      if _Template.Match.Name==pName: 
        return _Template
      if _Template.Match.Service:
        ts = _Template.Match.Service if isinstance(_Template.Match.Service,list) else [_Template.Match.Service]
        if pServices and any(x for x in pServices if any(y for y in ts if y.upper() in x.upper())):
          return _Template
    return None

  async def Parse(pDevice:Bluetooth.Device,pData:dict[str:bytes])->list[str]:
    if pDevice.Template.ID in ['BTHome','BTHomeV2']: 
      r = await BtHome.Parse(pDevice,pData)
      return r
    _UpdatedEntities=[]
    for _Entity in pDevice.Entities:
      if  _Entity.Characteristic: #This needs connection
        continue
      if not _Entity.Code: continue
      _ServiceData=None
      if hasattr(_Entity,'Service') and _Entity.Service:
        _ServiceData = next((pData[x] for x in pData.keys() if _Entity.Service in x),None)
        if not _ServiceData: continue
      try:
        v = eval(_Entity.Code,None,{'v':_ServiceData})
        _UpdatedEntities.append(_Entity.Name)
        if v: await _Entity.OnValue(v)
      except Exception as x: 
        Logger.Exception(f'Cannot get value for {_Entity.Name}',x)
      return _UpdatedEntities


  def LoadEntities(pDevice:Bluetooth.Device)->bool:
    if not pDevice.Template: return
    if pDevice.Template.Poll: pDevice.Poll = datetime.min
    if pDevice.Template.Refresh: pDevice.RefreshInterval = pDevice.Template.Refresh
    if pDevice.Template.Expiry: pDevice.ExpiryInterval = pDevice.Template.Expiry
    for e in pDevice.Template.Entities:
      _Config = LibPython.Dynamic()
      _Config.Name=e.Name
      _Config.ID=e.Name.upper()
      _Config.Category = e.Category
      _Config.Unit = e.Unit
      _Config.Service = e.Service
      _Config.Characteristic = e.Characteristic
      _Config.Code = e.Code
      _Entity = None
      if e.Type=='Sensor':
        _Entity = Bluetooth.Sensor(_Config)
      elif e.Type=='BinarySensor':
        _Entity = Bluetooth.Button(_Config)
      elif e.Type=='Button':
        _Entity = Bluetooth.Button(_Config)
      elif e.Type=='Switch':
        _Entity = Bluetooth.Switch(_Config)
      elif e.Type=='Number':
        _Entity = Bluetooth.Number(_Config)
      elif e.Type=='text':
        _Entity = Bluetooth.Text(_Config)
      else:
        raise f'Invalid entity configuration {str(e)}'
      _Entity.Enabled = True
      pDevice.Entities.Add(_Entity)
    return True
  
