import asyncio
import LibHass.Web
import LibPython
import LibHass

Logger = LibPython.Logger('Component')
if LibHass.IS_ADDON:
  from homeassistant.helpers import discovery
  from homeassistant.helpers import device_registry,entity_registry
  from homeassistant.config_entries import ConfigEntry,ConfigEntryState,ConfigEntryDisabler
  import homeassistant.config_entries

#For entries in configuration.yaml
async def async_setup(hass, config):
  Logger.Debug(f'async_setup:{config}')
  return True

async def async_migrate_entry(hass, entry):
  Logger.Debug(f'async_migrate_entry:{entry.unique_id}')
  return True

async def Configure(pEntry,pDevices):
  Logger.Debug(f'async_setup_entry:{str([x.Name for x in pDevices])}')
  if not LibHass.IS_ADDON: return
  dr = device_registry.async_get(LibHass.Hass)
  er = entity_registry.async_get(LibHass.Hass)
  for _Device in pDevices:
    _Device.Logger.Info(f'Adding to HASS')
    d = dr.async_get_or_create(
        config_entry_id=pEntry.entry_id,
        connections={},
        identifiers={('TheCuriousGeek',f'{_Device.Name.replace(" ","_")}')},
        name=_Device.Name,
        manufacturer="SV Anand",
        model=_Device.Template.Name if _Device.Template else 'Unknown'
        )
    _Device.DeviceID = d.id
  pEntry.async_on_unload(pEntry.add_update_listener(Listener))
  pEntry.Devices = pDevices
  await LibHass.Hass.config_entries.async_forward_entry_setups(pEntry,['sensor','binary_sensor','switch','button','number','text'])
  for _Device in pDevices:
    for e in _Device.Entities:
      e.InHass = True
      er.async_update_entity(entity_id=e.entity_id,device_id=e.Device.DeviceID)
      if not e.Enabled: er.async_update_entity(entity_id=e.entity_id,disabled_by=entity_registry.RegistryEntryDisabler.USER)
      await e.RestoreState()
  return

async def Listener(hass,entry):
  if LibHass.IS_ADDON: await hass.config_entries.async_reload(entry.entry_id)

async def UnConfigure(pEntry,pDevices):
  Logger.Debug(f'async_unload_entry:{str([x.Name for x in pDevices])}')
  for p in ['sensor','binary_sensor','switch','button','number','text']:
    try: 
      await LibHass.Hass.config_entries.async_forward_entry_unload(pEntry,p)
    except:
      pass
  dr = device_registry.async_get(LibHass.Hass)
  er = entity_registry.async_get(LibHass.Hass)
  for _Device in pDevices:
    if _Device.IsConnected: await _Device.Disconnect()
    if _Device.IsRegistered:
      try:
        if dr.async_get(_Device.DeviceID):
          d = dr.async_remove_device(_Device.DeviceID)
          _Device.Logger.Info(f'Removed from HASS')
          for e in _Device.Entities:
            e.InHass = False
      except:
        _Device.Logger.Error(f'Error removing from HASS')
        pass
      _Device.IsRegistered = False
  return
