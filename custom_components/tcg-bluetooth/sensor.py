import LibPython
import LibHass
Logger = LibPython.Logger('HASS.sensor')

async def async_setup_entry(hass,entry,async_add_entities):
  Logger.Debug(f'async_setup_entry:{[d.Name for d in entry.Devices]}')
  _Entities=[]
  for d in entry.Devices:
    _Entities.extend([e for e in d.Entities if isinstance(e,LibHass.Sensor)])
  async_add_entities(_Entities)
  return True

async def async_remove_entry(hass, entry) -> None:
  Logger.Debug(f'async_remove_entry:{[d.Name for d in entry.Devices]}')
