import json
from .Utility import ToJson

class Dynamic(dict):
  @staticmethod
  def FromString(pString:str,pCaseSensitive=True):
    _Json = json.loads(pString)
    if isinstance(_Json, list):
      return [Dynamic(x,pCaseSensitive) for x in _Json]    
    return Dynamic(_Json,CaseSensitive=pCaseSensitive)
  
  def __init__(self,From:str|dict[str,any]=None,CaseSensitive=True,**kwargs):
    self.__CaseSensitive=CaseSensitive
    if isinstance(From,Dynamic):
      for n,v in From.items():
        self[n] = v
    elif isinstance(From,str):
      if From=='': return
      _Dict = json.loads(From)
      if not isinstance(_Dict,dict): raise 'Dynamic:JSON string must be an object'
      self.__init__(_Dict,CaseSensitive=CaseSensitive,**kwargs)
    elif isinstance(From,dict):
      for n,v in From.items():
        if isinstance(v, (list, tuple)):
          self[str(n)] = [Dynamic(x) if isinstance(x, dict) else x for x in v]
        else:
          self[str(n)] = Dynamic(v) if isinstance(v, dict) else v
    elif kwargs:
      for n,v in kwargs.items():
        self[n] = v
    elif From is None: return
    else: raise 'Invalid initialization parameter'
 
  @property
  def CaseSensitive(self)->bool:
    return self.__CaseSensitive

  #region object methods
  @property
  def Fields(self)->list[str]:
    return list(self.keys())  
  def Contains(self,Field:str)->bool:
    if self.__CaseSensitive: return any(x for x in self.keys() if x==Field)
    return any(x for x in self.keys() if x.upper()==Field.upper())    
  def __getattr__(self,pName:str):
    if pName.startswith('_'): return self.__dict__[pName] if pName in self.__dict__.keys() else None
    if self.__CaseSensitive: return self[pName] if pName in self.keys() else None
    return next((self[x] for x in self.keys() if x.upper()==pName.upper()),None)
  def __setattr__(self,pName:str,pValue):
    if pName.startswith('_'): 
      self.__dict__[pName] = pValue
      return
    self[pName if self.__CaseSensitive else pName.upper()] = pValue    
  def Get(self,pName:str):
    return self.__getattr__(pName if self.__CaseSensitive else pName.upper())  
  def Set(self,pName:str, pValue):
    self[pName if self.__CaseSensitive else pName.upper()] = pValue
  #endregion

  def __repr__(self):
    return ToJson(self)
  
  def __eq__(self,pOther)->bool:
    if not type(self)==type(pOther): return False
    for a in self.keys():
      if not a in pOther.keys(): return False
      if not self[a]==pOther[a]: return False
    return True
  
  def __ge__(self,pOther)->bool:
    for a in self.keys():
      if hasattr(pOther,a) and not self[a]==pOther[a]: return False
    return True  

  def Merge(self,pWhat):
    if not type(self)==type(pWhat): raise ('Dynamic:Can only merge dynamic')
    for _NewKey,_NewValue in pWhat.items():
      if _NewKey in self.keys():
        _Value = self[_NewKey]
        if isinstance(_Value,list):
          if isinstance(_NewValue,list): 
            _Value.extend([x for x in _NewValue if not x in _Value])
          elif isinstance(_NewValue,Dynamic):
            self[_NewKey] = _NewValue #Destructive merge
          else:
            if not _NewValue in _Value: _Value.append(_NewValue) 
        elif _NewValue is None:
          pass
        elif isinstance(_Value,Dynamic) and isinstance(_NewValue,Dynamic):
          _Value.Merge(_NewValue)
        elif isinstance(_Value,dict) and isinstance(_NewValue,dict):
          for k,v in _NewValue.items():
            _Value[k] = v
        else:
          self[_NewKey] = [_Value,_NewValue]
      else:
        self[_NewKey] = _NewValue
