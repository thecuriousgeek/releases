import logging
import traceback

if logging.getLogger().handlers:
  logging.basicConfig(format='%(message)s')
else:
  logging.basicConfig(format='[%(asctime)s %(name)s(%(levelname)s)]=>%(message)s')

class Logger:
  class LEVEL:
    from logging import DEBUG,INFO,WARNING,ERROR,CRITICAL, NOTSET as TRACE

  COLOR_MAP = {
    LEVEL.TRACE:"\x1b[38m",
    LEVEL.DEBUG:"\x1b[38m",
    LEVEL.INFO:"\x1b[32m", #Green
    LEVEL.WARNING:"\x1b[33m", #Yellow
    LEVEL.ERROR:"\x1b[31m", #Red
    LEVEL.CRITICAL:"\x1b[31;1m", #Red
  }
  RESET = "\x1b[0m"
  _Level=logging.WARNING

  @classmethod
  def SetLevel(cls,pWhat:int):
    Logger._Level=pWhat
    logging.getLogger().setLevel(Logger._Level)

  def __init__(self,pName,pParent=None):
    if pParent is not None and pParent.Name:
      self.Name = f'{pParent.Name}.{pName}'
    else:
      self.Name = pName
    self.__BaseLogger = logging.getLogger(self.Name)

  def Log(self,pLevel,pWhat):
      self.__BaseLogger.log(pLevel,f'{Logger.COLOR_MAP[pLevel]}{pWhat}{Logger.RESET}')

  def Trace(self,pWhat): 
    self.Log(Logger.LEVEL.TRACE,pWhat)
  def Debug(self,pWhat): 
    self.Log(Logger.LEVEL.DEBUG,pWhat)
  def Info(self,pWhat): 
    self.Log(Logger.LEVEL.INFO,pWhat)
  def Warning(self,pWhat): 
    self.Log(Logger.LEVEL.WARNING,pWhat)
  def Error(self,pWhat): 
    self.Log(Logger.LEVEL.ERROR,pWhat)
  def Exception(self,pWhat,pException): 
    self.Log(Logger.LEVEL.CRITICAL,f'{pWhat}({str(pException)})\n{traceback.format_exc()}')
