import asyncio
from homeassistant import config_entries
from homeassistant.config_entries import ConfigEntry
import homeassistant.helpers.config_validation as cv
import voluptuous as vol
from urllib.parse import urlparse
import LibPython
import LibHass
import Tuya

class TcgTuyaConfigFlow(config_entries.ConfigFlow,domain=Tuya.Name):
  VERSION = 1

  async def async_step_user(self, pData):
    if self.hass.config_entries.async_entry_for_domain_unique_id(self.handler,Tuya.Name):
      return self.async_abort(reason="already_configured")
    return await self.async_step_Cloud(None)

  async def async_step_Cloud(self, pData):
    if pData is None:
      r = {'us':'United States','eu':'Europe'}
      return self.async_show_form(step_id='Cloud', data_schema=vol.Schema({vol.Required('ApiKey'):str, vol.Required('Secret'):str, vol.Required('Region'):vol.In(r)}))
    await self.async_set_unique_id(Tuya.Name)
    self._abort_if_unique_id_configured()
    pData['Devices'] = []
    await LibHass.Component.Init(self.hass)
    await Tuya.Init()
    await Tuya.Configure(pData)
    return self.async_create_entry(title='Devices', data=pData)

  def async_get_options_flow(config_entry):
    return TcgTuyaOptionsFlow(config_entry)


class TcgTuyaOptionsFlow(config_entries.OptionsFlow):
  def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
    self.Entry = config_entry

  async def async_step_init(self, pData):
    if pData is None:
      _Devices = {x.ID:f'{x.Name} ({x.SubType})' for x in Tuya.Devices}
      _Devices = dict(sorted(_Devices.items(), key=lambda i: i[1]))
      _Enabled = [x.ID for x in Tuya.Devices if x.IsRegistered]
      return self.async_show_form(step_id="init", data_schema=vol.Schema({vol.Optional("ID",default=_Enabled):cv.multi_select(_Devices)}))
    for d in Tuya.Devices:
      d.IsRegistered = d.ID in pData['ID']
    return self.async_create_entry(data={'Devices':Tuya.Configuration()['Devices']})
