from homeassistant import config_entries
from homeassistant.config_entries import ConfigEntry
import homeassistant.helpers.config_validation as cv
import voluptuous as vol
import LibPython
import LibHass
import Tuya

class TcgTuyaConfigFlow(config_entries.ConfigFlow,domain='tcg-tuya'):
  VERSION = 1

  async def async_step_user(self, pData):
    await Tuya.Init(__package__,self.hass)
    # if self.hass.config_entries.async_entry_for_domain_unique_id(self.handler,Tuya.Name):
    #   return self.async_abort(reason="already_configured")
    return await self.async_step_Cloud(None)

  async def async_step_Cloud(self, pData):
    if pData is None:
      return self.async_show_form(step_id="Cloud", data_schema=vol.Schema({vol.Required("Type"):vol.In({'ApiKey':'API Key & Secret','Auth':'Authorize with SmartLife app'})}))
    if pData['Type']=='ApiKey':
      return await self.async_step_CloudApi(None)
    return await self.async_step_CloudUser(None)

  async def async_step_CloudApi(self, pData):
    if pData is None:
      r = {'us':'United States','eu':'Europe'}
      return self.async_show_form(step_id='CloudApi', data_schema=vol.Schema({vol.Required('ApiKey'):str, vol.Required('Secret'):str, vol.Required('Region'):vol.In(r)}))
    await self.async_set_unique_id(Tuya.Name)
    #self._abort_if_unique_id_configured()
    Tuya.Config.Cloud = LibPython.Dynamic({'ApiKey':pData['ApiKey'],'Secret':pData['Secret'],'Region':pData['Region']})
    await Tuya.Reload()
    return self.async_create_entry(title='Tuya Devices', data={'Cloud':Tuya.Config.Cloud})

  async def async_step_CloudUser(self, pData):
    if pData is None:
      return self.async_show_form(step_id='CloudUser', data_schema=vol.Schema({vol.Required('ID'):str}))
    self.UserID = pData['ID']
    return await self.async_step_CloudQrCode(None)

  async def async_step_CloudQrCode(self, pData):
    if pData is None:
      self.QrCode,_Image = await LibHass.Hass.async_add_executor_job(Tuya.Cloud.GetQrCode,self.UserID)
      return self.async_show_form(step_id='CloudQrCode',data_schema=vol.Schema({}),description_placeholders={'image':_Image})
    _Auth = await LibHass.Hass.async_add_executor_job(Tuya.Cloud.CheckQrCode,self.UserID,self.QrCode)
    if not _Auth:
      return await self.async_step_Cloud(None)
    await self.async_set_unique_id(Tuya.Name)
    #self._abort_if_unique_id_configured()
    Tuya.Config.Cloud = _Auth
    await Tuya.Reload()
    return self.async_create_entry(title='Tuya Devices', data={'Cloud':Tuya.Config.Cloud})

  def async_get_options_flow(config_entry):
    return TcgTuyaOptionsFlow(config_entry)


class TcgTuyaOptionsFlow(config_entries.OptionsFlow):
  def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
    self.Entry = config_entry

  async def async_step_init(self, pData):
    if pData is None:
      _Devices = {x.ID:f'{x.Name} ({x.Category})' for x in Tuya.Devices}
      _Devices = dict(sorted(_Devices.items(), key=lambda i: i[1]))
      _Enabled = [x.ID for x in Tuya.Devices if x.IsRegistered]
      return self.async_show_form(step_id="init", data_schema=vol.Schema({vol.Optional("ID",default=_Enabled):cv.multi_select(_Devices)}))
    for d in Tuya.Devices:
      d.IsRegistered = d.ID in pData['ID']
    Tuya.Config.Devices = [{'ID':x.ID,'Name':x.Name} for x in Tuya.Devices if x.IsRegistered]
    return self.async_create_entry(data={'Devices':Tuya.Config.Devices})
