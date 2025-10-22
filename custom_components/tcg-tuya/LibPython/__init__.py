from abc import ABC,abstractmethod
from typing import Self
from datetime import datetime
from .Logger import Logger
from .Dynamic import Dynamic
from .AsyncTask import AsyncTask
from .IniFile import IniFile
from . import Utility
if Utility.CanImport('fastapi'):
  from .WebServer import WebServer
from . import Utility
if Utility.CanImport('lxml'):
  from .Xml import Xml

class Singleton(ABC):
  _Instances = {}
  @classmethod
  def GetInstance(cls,*pArg)->Self:
    _Name = cls.__name__+'.'+str(pArg)
    if _Name not in Singleton._Instances:
      Singleton._Instances[_Name] = cls(*pArg)
    return Singleton._Instances[_Name]

# def Singleton(pType:type):
#   _Instances = {}
#   def GetInstance(*pArg):
#     _Name = pType.__name__+'.'+str(pArg)
#     if _Name not in _Instances:
#       _Instances[_Name] = pType(*pArg)
#     return _Instances[_Name]
#   return GetInstance


class Dummy():
  pass

class Status(AsyncTask):
  def __init__(self,pName:str,pMethod,pInterval:int):
    self.Name = pName
    self.Method = pMethod
    super().__init__(pName,pInterval)

  async def Run(self):
    self.Logger.Info(f'{self.Method()}')
    return False
  
  def Stop(self):
    self.Logger.Info(f'{self.Method()}') #Last time
    super().Stop()


class Timer():
  def __init__(self,pName:str):
    self.Name = pName
    self.Start = datetime.now()
    
  def Log(self,pWhat=None):
    Logger(f'{self.Name}.Timer').Info(f'{(pWhat if pWhat is not None else "")} in {(datetime.now()-self.Start).total_seconds()} seconds')
