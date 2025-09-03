import asyncio
from homeassistant import config_entries
from homeassistant.config_entries import ConfigEntry
import homeassistant.helpers.config_validation as cv
import voluptuous as vol
from urllib.parse import urlparse
import LibHass
import Bluetooth

class TcgBluetoothConfigFlow(config_entries.ConfigFlow,domain=Bluetooth.Name):
  VERSION = 1

  async def async_step_user(self, pData):
    if self.hass.config_entries.async_entry_for_domain_unique_id(self.handler,Bluetooth.Name):
      return self.async_abort(reason="already_configured")
    await self.async_set_unique_id(Bluetooth.Name)
    self._abort_if_unique_id_configured()
    pData = {'Devices':[]}
    await LibHass.Component.Init(self.hass)
    await Bluetooth.Init()
    await Bluetooth.Configure({'Devices':[]})
    return self.async_create_entry(title='Devices', data=pData)

  def async_get_options_flow(config_entry):
    return TcgBluetoothOptionsFlow(config_entry)


class TcgBluetoothOptionsFlow(config_entries.OptionsFlow):
  def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
    self.Entry = config_entry

  async def async_step_init(self, pData):
    if pData is None:
      _Devices = {x.ID:f'{x.Name} ({x.SubType})' for x in Bluetooth.Devices}
      _Devices = dict(sorted(_Devices.items(), key=lambda i: i[1]))
      _Enabled = [x.ID for x in Bluetooth.Devices if x.IsRegistered]
      return self.async_show_form(step_id="init", data_schema=vol.Schema({vol.Optional("ID",default=_Enabled):cv.multi_select(_Devices)}))
    for d in Bluetooth.Devices:
      d.IsRegistered = d.ID in pData['ID']
    return self.async_create_entry(data={'Devices':Bluetooth.Configuration()['Devices']})
