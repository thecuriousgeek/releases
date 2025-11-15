import tempfile
import webbrowser
import time
import sys
import io
import os
import json
import asyncio
import pyqrcode
import tinytuya
import tuya_sharing
import LibPython
import LibHass
import Tuya

CONF_ENDPOINT = "endpoint"
CONF_USER_CODE = "user_code"
CONF_CLIENT_ID = "HA_3y9q4ak7g4ephrvke"
CONF_SCHEMA = "haauthorize"
APP_QR_CODE_HEADER = "tuyaSmart--qrLogin?token="

class Cloud:
  def __init__(self):
    self.Devices = []
    from . import Logger
    self.Logger = LibPython.Logger('Cloud',Logger)

  def Load(self):
    self.Devices.clear()
    _Data = []
    if os.path.exists(Tuya.CLOUDCACHE_FILE):# and os.stat(Tuya.CLOUDCACHE_FILE).st_mtime>time.time()-43200:
      self.Logger.Debug(f'Load:Loading cached data')
      _Data = [LibPython.Dynamic(x) for x in json.loads(open(Tuya.CLOUDCACHE_FILE,'r').read())]
    else:
      self.Logger.Debug(f'Load:Retrieving from cloud')
      from . import Config
      if Config.Cloud.ApiKey: 
        _Data = self.LoadWithApiKey(Config.Cloud.ApiKey,Config.Cloud.Secret,Config.Cloud.Region)
      elif Config.Cloud.Token: 
        _Data = self.LoadWithToken(Config.Cloud.UserName,Config.Cloud.Terminal,Config.Cloud.URL,Config.Cloud.Token)
      else: 
        self.Logger.Warning('Load:No settings defined')
        return
      json.dump(_Data,open(Tuya.CLOUDCACHE_FILE,'w'),default=lambda o: o.__dict__,indent=2,sort_keys=True)
    self.Logger.Info(f'Load:Loaded {len(_Data)} devices')
    self.Devices.clear()
    for d in _Data:
      self.Devices.append(d)
      # Devices[d['id'].upper()] = d

  def GetQrCode(self,pUser)->tuple:
    _Login = tuya_sharing.LoginControl()
    self.Logger.Debug(f'GetQrCode:Getting QR Code from Tuya for {pUser}')
    _Response = _Login.qr_code(CONF_CLIENT_ID,CONF_SCHEMA,pUser)
    if not _Response.get('success',False): return None
    _QrCode = _Response['result']['qrcode']
    _Image = pyqrcode.create(APP_QR_CODE_HEADER+_QrCode)
    with io.BytesIO() as buffer:
      _Image.svg(file=buffer, scale=4)
      _Image = str(
              buffer.getvalue()
              .decode("ascii")
              .replace("\n", "")
              .replace(
                  (
                      '<?xml version="1.0" encoding="UTF-8"?>'
                      '<svg xmlns="http://www.w3.org/2000/svg"'
                  ),
                  "<svg",
              )
        )
      return (_QrCode,_Image)

  def CheckQrCode(self,pUser,pQrCode):
    _Login = tuya_sharing.LoginControl()
    _Response = _Login.login_result(pQrCode,CONF_CLIENT_ID,pUser)
    if not _Response[0]: return None
    _Result = LibPython.Dynamic()
    _Result.UserID = pUser
    _Result.Token = {
      "t": _Response[1].get("t"),
      "uid": _Response[1].get("uid"),
      "expire_time": _Response[1].get("expire_time"),
      "access_token": _Response[1].get("access_token"),
      "refresh_token": _Response[1].get("refresh_token"),
    }
    _Result.UserName = _Response[1]['username']
    _Result.Terminal = _Response[1]['terminal_id']
    _Result.URL = _Response[1]['endpoint']
    return _Result

  def GetToken(self):
    _UserID = 'BaJWsm6'
    _UserID = input(f'Enter the user ID[{_UserID}]') or _UserID
    if not _UserID: sys.exit(1)
    _QrCode,_Image = Cloud.GetQrCode(_UserID)
    import tempfile
    import webbrowser
    import os
    _File = tempfile.NamedTemporaryFile('w',delete=False,suffix='.html')
    _File.write(f'<html><body>Scan this with QR Code the "Smart Things" app on the phone<br>{_Image}</body></html>')
    _File.close()
    self.Logger.Info('GetToken:Showing QR Code to user for authorization')
    _Result = None
    webbrowser.open(_File.name)
    for i in range(0,30):
      time.sleep(2.0)
      self.Logger.Debug('GetToken:Checking for authorization')
      _Result = Cloud.CheckQrCode(_UserID,_QrCode)
      if _Result: break
    os.remove(_File.name)
    if not _Result:
      self.Logger.Error('GetToken:Failed to get authorization')
    return _Result
    
  def LoadWithToken(self,pUserName,pTerminal,pURL,pToken):
    from .Entity import Sensor,BinarySensor,RawSensor,Switch,Number,Text #Just to get correct spelling
    self.Logger.Debug('LoadWithToken:Getting devices with token')
    _Manager = tuya_sharing.Manager(CONF_CLIENT_ID,pUserName,pTerminal,pURL,pToken)
    _Listener = DeviceListener(_Manager)
    _Manager.add_device_listener(_Listener)
    _Homes = _Manager.home_repository
    _Repo = _Manager.device_repository
    _Result = []
    for h in _Homes.query_homes():
      self.Logger.Debug(f'LoadWithToken:Getting devices for home {h.name}')
      for d in _Repo.query_devices_by_home(h.id):
        _Device = LibPython.Dynamic()
        _Device.ID = d.id
        _Device.Name = d.name
        _Device.Category = d.category
        _Device.Product = d.product_name
        _Device.Model = d.model
        _Device.Icon = d.icon
        _Device.Gateway = d.gateway_id if hasattr(d,'gateway_id') else None
        _Device.NodeID = d.node_id if hasattr(d,'node_id') else None
        _Device.LocalKey = d.local_key if hasattr(d,'local_key') else None
        _Device.Entities = []
        for f in d.function.values():
          _Type = None
          if f.type in ['Integer']: _Type = Number.__name__
          elif f.type in ['String']: _Type = Text.__name__
          elif f.type in ['Raw']: _Type = RawSensor.__name__
          elif f.type in ['Boolean']: _Type = Switch.__name__
          elif f.type in ['Enum','Bitmap']: continue
          else: continue
          _Entity = LibPython.Dynamic(Name=f.code,Type=_Type)
          _Entity.ID = next((str(k) for k,v in d.local_strategy.items() if v['status_code']==_Entity.Name),None)
          if not _Entity.ID: continue
          _Device.Entities.append(_Entity)
        for s in d.status_range.values():
          _Type = None
          if s.type in ['Integer','Enum','String']: _Type = Sensor.__name__
          elif s.type in ['Raw']: _Type = RawSensor.__name__
          elif s.type in ['Boolean']: _Type = BinarySensor.__name__
          elif s.type in ['Bitmap']: _Type = Text.__name__
          else: continue
          _Entity = LibPython.Dynamic(Name=s.code,Type=_Type)
          _Entity.ID = next((str(k) for k,v in d.local_strategy.items() if v['status_code']==_Entity.Name),None)
          if not _Entity.ID: continue
          try: _Values = json.loads(d.local_strategy[int(_Entity.ID)]['config_item']['valueDesc'])
          except: _Values = None
          if _Values:
            if 'unit' in _Values:_Entity.Unit = _Values['unit']
            if 'scale' in _Values:_Entity.Scale = 10**_Values['scale']
            if 'label' in _Values: _Entity.Labels = _Values['label']
          if not any(x for x in _Device.Entities if x.ID==_Entity.ID):
            _Device.Entities.append(_Entity)
        #Any DPs that are not defined as functions or statuses, e.g.. switch_1
        for dp,s in d.local_strategy.items():
          if any (x for x in _Device.Entities if x.ID==str(dp)): continue
          _Type = None
          if s['config_item']['valueType'] in ['Integer','Enum','String']: _Type = Sensor.__name__
          elif s['config_item']['valueType'] in ['Raw']: _Type = RawSensor.__name__
          elif s['config_item']['valueType'] in ['Boolean']: _Type = BinarySensor.__name__
          elif s['config_item']['valueType'] in ['Bitmap']: _Type = Text.__name__
          else: continue
          sf = json.loads(s['config_item']['statusFormat'])
          if not sf: continue
          _Entity = LibPython.Dynamic(ID=str(dp),Name=sf.popitem()[0],Type=_Type)
          _Device.Entities.append(_Entity)
        _Result.append(_Device)
    return _Result

  def LoadWithApiKey(self,pApiKey,pSecret,pRegion):
    _Result=[]
    from .Entity import Sensor,BinarySensor,RawSensor,Switch,Number,Text
    self.Logger.Debug('Cloud.LoadWithApiKey:Getting devices with ApiKey')
    t = tinytuya.Cloud(apiRegion=pRegion,apiKey=pApiKey,apiSecret=pSecret)
    l = t.getdevices()
    for d in l:
      _Device = LibPython.Dynamic()
      _Device.ID = d['id']
      _Device.Name = d['name']
      _Device.Category = d['category']
      _Device.Product = d['product_name']
      _Device.Model = d['model']
      _Device.Icon = d['icon']
      _Device.Gateway = d['gateway_id'] if 'gateway_id' in d else None
      _Device.NodeID = d['node_id'] if 'node_id' in d else None
      _Device.LocalKey = d['key'] if 'key' in d else None
      _Device.Entities = []
      self.Logger.Debug(f'LoadWithApiKey:Getting details for {_Device.Name}')
      p = t.getdps(d['id'])
      if 'result' in p: 
        for dp in p['result']['functions']:
          _Type = None
          if dp['type'] in ['Integer']: _Type = Number.__name__
          elif dp['type'] in ['String']: _Type = Text.__name__
          elif dp['type'] in ['Raw']: _Type = RawSensor.__name__
          elif dp['type'] in ['Boolean']: _Type = Switch.__name__
          elif dp['type'] in ['Enum','Bitmap']: continue
          else: continue
          _Entity = LibPython.Dynamic(ID=str(dp['dp_id']),Name=dp['code'],Type=_Type)
          _Device.Entities.append(_Entity)
        for dp in p['result']['status']:
          _Type = None
          if dp['type'] in ['Integer','Enum','String']: _Type = Sensor.__name__
          elif dp['type'] in ['Raw']: _Type = RawSensor.__name__
          elif dp['type'] in ['Boolean']: _Type = BinarySensor.__name__
          elif dp['type'] in ['Bitmap']: _Type = Text.__name__
          else: continue
          _Entity = LibPython.Dynamic(ID=str(dp['dp_id']),Name=dp['code'],Type=_Type)
          try: _Values = json.loads(dp['values'])
          except: _Values = None
          if _Values:
            if 'unit' in _Values:_Entity.Unit = _Values['unit']
            if 'scale' in _Values:_Entity.Scale = 10**_Values['scale']
            if 'label' in _Values: _Entity.Labels = _Values['label']
          if not any(x for x in _Device.Entities if x.ID==_Entity.ID):
            _Device.Entities.append(_Entity)
      _Result.append(_Device)
    return _Result


class DeviceListener(tuya_sharing.SharingDeviceListener):
    """Device update listener."""
    def __init__(self,manager,):
        self._manager = manager

    def update_device(self,device,updated_status_properties: list[str] | None,) -> None:
        """Device status has updated."""
        pass

    def add_device(self, device) -> None:
        """A new device has been added."""
        pass

    def remove_device(self, device_id) -> None:
        """A device has been removed."""
        pass


class TokenListener(tuya_sharing.SharingTokenListener):
    """Listener for upstream token updates.
    This is only needed to get some debug output when tokens are refreshed."""
    def update_token(self, token_info) -> None:
        print("Token updated")
