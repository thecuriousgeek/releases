from datetime import datetime
import atexit
import asyncio
import threading
import contextlib
import gc
from . import Logger
from abc import ABC, abstractmethod

class AsyncTask(ABC):
  def __init__(self,pName:str,pInterval:int=0):
    self.Name = pName or 'AsyncTask'
    self.Logger = Logger(self.Name)
    self.Interval = pInterval
    self.CommandStop = asyncio.Event()
    self.Thread = None
    self.Loop = None

  def Start(self,pBackground=False):
    self.Logger.Debug(f'Starting')
    atexit.register(self.Stop)
    try:
      if pBackground:
        raise RuntimeError(None)
      else: asyncio.get_running_loop().create_task(self.StartAsync())
    except RuntimeError:
      self.Thread = threading.Thread(target=asyncio.run,args=[self.StartAsync()],daemon=True,name=self.Name)
      self.Thread.start()

  async def StartAsync(self):
    if not self.Loop: self.Loop = asyncio.get_running_loop()
    if not await self.Begin():
      self.Logger.Error('Could not begin task')
      await self.End()
      return
    while not self.CommandStop.is_set():
      self.Logger.Trace('RunBegin')
      _Start = datetime.now()
      _RunResult = False
      try:
        _RunResult = await self.Run()
      except Exception as x:
        self.Logger.Exception('Exception in run',x)
        with contextlib.suppress(asyncio.TimeoutError):
          await asyncio.wait_for(self.CommandStop.wait(),30)
        continue
      self.Logger.Trace('RunEnd')
      if self.CommandStop.is_set(): break
      if not _RunResult: break
      if (datetime.now()-_Start).total_seconds() < self.Interval:
        with contextlib.suppress(asyncio.TimeoutError):
          await asyncio.wait_for(self.CommandStop.wait(),self.Interval)
    await self.End()

  def Stop(self):
    self.Logger.Debug('Stopping')
    self.CommandStop.set()
    atexit.unregister(self.Stop)
    if self.Thread: self.Thread.join()
    gc.collect()

  @abstractmethod
  async def Run(self)->bool: return True #Returns true if complete so I dont have to force a wait
  async def Begin(self)->bool: return True #May be overridden, returns False if could not begin
  async def End(self): pass #May be overridden

