import sys
import json
import ast
import os
import platform
import importlib.util
import pathlib
import functools
import asyncio
from datetime import datetime,timedelta,timezone

def ToJson(pObject):
  return json.dumps(pObject, default=lambda x: {k:v for k,v in x.__dict__.items() if k[0]!='_'} if hasattr(x,'__dict__') else str(x))

def ToObject(pWhat):
  if pWhat is None or isinstance(pWhat, (bool, int, float, str)): return pWhat
  if pWhat is None or isinstance(pWhat, datetime): return str(pWhat)
  if isinstance(pWhat, (list, tuple, set)): return [ToObject(item) for item in pWhat]
  if isinstance(pWhat, dict):
    _Result = {}
    for k, v in pWhat.items():      
      try: _Result[str(k)] = ToObject(v)
      except Exception: continue
    return _Result
  if hasattr(pWhat, "__dict__"):
    _Result = {}
    for k, v in pWhat.__dict__.items():
      if k.startswith('_'): continue
      try: _Result[k] = ToObject(v)
      except Exception: continue
    return _Result
  try:
    json.dumps(pWhat)
    return pWhat
  except Exception:
    return str(pWhat)

def DictGet(pDict:dict,pKeys:list):
  for a in pKeys:
    if a in pDict: return pDict[a]
  return None

def Scan(pFolder:str, pExtensions:list=None):
  for _Root,_Folders,_Files in os.walk(pFolder):
    for _File in _Files:
      if not pExtensions: 
        yield (_Root+"/"+_File).replace('\\','/')
      elif pathlib.Path(_File).suffix.lower() in pExtensions: 
        yield (_Root+"/"+_File).replace('\\','/')

def StringToObject(pSource:str=None):
  if pSource is None: return None
  if pSource.startswith('{') or pSource.startswith('['):
    from . import Dynamic
    _Result = json.loads(pSource)
    if isinstance(_Result,list): return [Dynamic(x) for x in _Result]
    return Dynamic(_Result)
  return ast.literal_eval(pSource)

def DebugMode()->bool:
  return sys.gettrace() is not None

def IsNative()->bool:
  return platform.python_implementation() == 'CPython'
  
def ToTimestamp(pDate:datetime)->int:
  return (pDate.replace(tzinfo=pDate.tzinfo or timezone.utc)-datetime(1970,1,1,tzinfo=timezone.utc)).total_seconds()
  # _Result = (pDate-datetime(1970,1,1)).total_seconds()
  # return _Result if _Result>0 else _Result+time.timezone

def FromTimestamp(pTimestamp:int|float)->datetime:
  # return datetime.fromtimestamp(pTimestamp) if pTimestamp>0 else datetime(1970,1,1)+timedelta(0,pTimestamp-time.timezone)
  return datetime(1970,1,1,tzinfo=timezone.utc)+timedelta(0,pTimestamp)

#Hack to set modified to pre-epoch
def SetModified(pFileName,pDate):    
  os.utime(pFileName,(datetime.now(tz=timezone.utc).timestamp(),ToTimestamp(pDate)))

#Stupid method so I dont have to try/catch the import errors
def CanImport(pModule):
  return importlib.util.find_spec(pModule) is not None


async def RunSync(pWhat,**kwargs):
  _Loop = asyncio.get_running_loop()
  _Method = functools.partial(pWhat,**kwargs)
  _Result = await _Loop.run_in_executor(None,_Method)
  return _Result
