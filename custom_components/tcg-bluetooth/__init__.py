#This is called directly by Home Assistant loader
import sys
import os
import asyncio
DOMAIN='tcg-bluetooth'
os.chdir(os.path.dirname(__file__))
sys.path.insert(1, os.path.dirname(__file__))
import LibPython
LibPython.Logger.SetPrefix(DOMAIN)
import LibHass
import Bluetooth 

async def async_setup(hass, config):
  await LibHass.Component.Init(hass)
  await Bluetooth.Init()
  await LibHass.Component.async_setup(hass,config)
  Bluetooth.Scanner.Start()
  LibHass.WebApi(Bluetooth).Start()
  if not Bluetooth.__name__ in config: return True
  return True

async def async_migrate_entry(hass, entry):
  return await LibHass.Component.async_migrate_entry(hass,Bluetooth,entry)

async def async_setup_entry(hass,entry):
  return await LibHass.Component.async_setup_entry(hass,Bluetooth,entry)

async def async_unload_entry(hass, entry)->bool:
  return await LibHass.Component.async_unload_entry(hass,Bluetooth,entry)
