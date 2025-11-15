import os

class IniFile:
  def __init__(self,pFileName:str):
    self.FileName = pFileName
    self.Sections = {}
    if not os.path.exists(pFileName): return
    _Section = {}
    self.Sections["ROOT"] = _Section
    with open(self.FileName,'r') as _File:
      while True:
        _Line = _File.readline()
        if not _Line: break
        _Line = _Line.removesuffix('\n')
        if _Line == "": continue
        if _Line[0]=='[' and _Line[-1]==']':
          _Section = {}
          self.Sections[_Line[1:-1]] = _Section
        else:
          _KeyValue = _Line.split('=',1)
          _Section[_KeyValue[0]] = _KeyValue[1] if len(_KeyValue) > 1 else None
    if len(self.Sections["ROOT"])==0: del self.Sections['ROOT']

  def Get(self,pSection:str,pKey:str)->str:
    if not pSection in self.Sections: return None
    if not pKey in self.Sections[pSection]: return None
    return self.Sections[pSection][pKey]

  def GetSections(self)->list:
    return list(self.Sections.keys())
  
  def GetKeys(self,pSection:str)->list:
    if not pSection in self.Sections: return []
    return list(self.Sections[pSection].keys())

  def Add(self,pSection:str,pKey:str,pValue:str):
    if not pSection in self.Sections:
      self.Sections[pSection] = {}
    self.Sections[pSection][pKey] = pValue

  def Delete(self,pSection:str,pKey:str):
    if pSection in self.Sections:
      if not pKey: del self.Sections[pSection]
      elif pKey in self.Sections[pSection]: del self.Sections[pSection][pKey]

  def Save(self):
    _Buffer = ''
    for _Section,_Items in self.Sections.items():
      _Buffer += f'[{_Section}]\n'
      for _Name,_Value in _Items.items():
        _Buffer += f'{_Name}={_Value}\n'
    with open(self.FileName,'tw') as _File:
      _File.write(_Buffer)
