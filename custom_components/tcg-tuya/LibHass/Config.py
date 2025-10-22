import os
import json
import LibPython
import LibHass

class Config:
  def __init__(self):
    self._Data = LibPython.Dynamic(Devices=[])
    if LibHass.IS_ADDON: return
    if not os.path.exists('config.json'): return
    self._Data = LibPython.Dynamic(json.load(open('config.json','r')))

  def Load(self,pData:dict):
    self._Data = LibPython.Dynamic(pData)

  def Save(self)->str|None:
    _Result = json.dumps(self._Data,indent=2,sort_keys=True)
    if LibHass.IS_ADDON: return _Result
    with open('config.json','w') as f: f.write(_Result)
    return
    
  def Add(self,pDevice):
    if any(x for x in self.Devices if x.ID==pDevice.ID): raise 'Device already configured'
    self.Devices.append(LibPython.Dynamic(ID=pDevice.ID,Name=pDevice.Name,Category=pDevice.Category))
    self.Save()

  def Remove(self,pDevice):
    if not any(x for x in self.Devices if x.ID==pDevice.ID): raise 'Device not configured'
    self.Devices.remove(next(x for x in self.Devices if x.ID==pDevice.ID))
    self.Save()

  def __getattr__(self,pName:str):
    if not pName.startswith('_'): return self._Data[pName] if pName in self._Data else None
    return self.__dict__.__getattr__(pName)
  def __setattr__(self,pName:str,pValue):
    if not pName.startswith('_'): self._Data[pName] = pValue
    else: self.__dict__[pName] = pValue
