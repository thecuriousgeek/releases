#This is called directly by Home Assistant loader
import sys
import os
# os.chdir(os.path.dirname(__file__))
sys.path.insert(1, os.path.dirname(__file__))
import LibPython
import Bluetooth 

async def async_setup_entry(hass,entry):
  await Bluetooth.Init(__package__,hass)
  Bluetooth.Config.Devices = [LibPython.Dynamic(x) for x in entry.options['Devices']] if 'Devices' in entry.options else []
  await Bluetooth.Configure(entry)
  return True
 
async def async_unload_entry(hass,entry)->bool:
  await Bluetooth.UnConfigure(entry)
  return True
