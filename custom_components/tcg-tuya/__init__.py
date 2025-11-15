#This is called directly by Home Assistant loader
import sys
import os
# os.chdir(os.path.dirname(__file__))
sys.path.insert(1, os.path.dirname(__file__))
import LibPython
import Tuya

async def async_setup_entry(hass,entry):
  await Tuya.Init(__package__,hass)
  Tuya.Config.Cloud = LibPython.Dynamic(dict(entry.data['Cloud']))
  Tuya.Config.Devices = [LibPython.Dynamic(x) for x in entry.options['Devices']] if 'Devices' in entry.options else []
  await Tuya.Configure(entry)
  return True
 
async def async_unload_entry(hass,entry)->bool:
  await Tuya.UnConfigure(entry)
  return True
