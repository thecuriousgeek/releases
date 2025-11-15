import json
from types import SimpleNamespace
import os
import LibPython
import Tuya

Logger = LibPython.Logger('Tuya.Template')
class Template():
  __All = None
  def Templates():
    if Template.__All is None:
      Template.__All=[LibPython.Dynamic(x) for x in json.loads(open(Tuya.TEMPLATE_FILE,'r').read())]
    return Template.__All
  
  def Get(pCategory=None):
    return next((x for x in Template.Templates() if x.ID==pCategory),None)
  
  def LoadEntities(pDevice:Tuya.Device):
    if not pDevice.Template: return True
    if not pDevice.Template.Entities: return True
    for e in pDevice.Template.Entities:
      if e.ID: #Enabling an existing entity
        _Entity = pDevice.Entities.Get(e.ID)
        if _Entity:
          _Entity.Enabled = True
          if e.Name: _Entity.Name = e.Name
        continue
      if not e.Parent: continue #Cant have an entity without a parent
      _Entity = None
      _Config = LibPython.Dynamic()
      _Config.Device = pDevice
      _Config.ID = e.Name
      _Config.Name = e.Name
      parent = pDevice.Entities.Get(e.Parent)
      if not parent: continue #raise f'Parent not defined: {str(e)}'
      _Config.Parent = parent
      _Config.Category = e.Category
      _Config.Unit = e.Unit
      _Config.Code = e.Code
      if e.Type=='Sensor':
        _Entity = Tuya.Sensor(_Config)
      elif e.Type=='BinarySensor':
        _Entity = Tuya.BinarySensor(_Config)
      elif e.Type=='Button':
        _Entity = Tuya.Button(_Config)
      elif e.Type=='Switch':
        _Entity = Tuya.Switch(_Config)
      elif e.Type=='Number':
        _Entity = Tuya.Number(_Config)
      elif e.Type=='String':
        _Entity = Tuya.Text(_Config)
      elif e.Type=='Energy':
        _Entity = Tuya.Energy(_Config)
      else:
        continue #raise f'Invalid entity configuration. Invalid Type:{str(e)}'
      _Entity.Enabled = True
      pDevice.Entities.Add(_Entity)
