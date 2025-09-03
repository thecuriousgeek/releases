#This is called directly by Home Assistant loader
import sys
import os
import asyncio
DOMAIN='tcg-tuya'
os.chdir(os.path.dirname(__file__))
sys.path.insert(1, os.path.dirname(__file__))
import LibPython
LibPython.Logger.SetPrefix(DOMAIN)
import LibHass
import Tuya

async def async_setup(hass, config):
  await LibHass.Component.Init(hass)
  await Tuya.Init()
  await LibHass.Component.async_setup(hass,config)
  Tuya.Scanner.Start()
  LibHass.WebApi(Tuya).Start()
  if not Tuya.__name__ in config: return True
  return True

async def async_migrate_entry(hass, entry):
  return await LibHass.Component.async_migrate_entry(hass,Tuya,entry)

async def async_setup_entry(hass,entry):
  return await LibHass.Component.async_setup_entry(hass,Tuya,entry)
 
async def async_unload_entry(hass, entry)->bool:
  return await LibHass.Component.async_unload_entry(hass,Tuya,entry)
