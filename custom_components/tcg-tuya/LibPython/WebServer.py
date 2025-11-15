import os
import time
import ast
import io
import asyncio
import socket
import starlette
from fastapi import FastAPI, Request, Response
from fastapi.responses import FileResponse
import uvicorn
from . import AsyncTask,Dynamic,Logger,Utility

class WebServer(AsyncTask):
  class ObjectResponse(Response):
    media_type = "application/json"
    def __init__(self,content,**kwargs) -> None:
        super().__init__(content,**kwargs)
    def render(self, content) -> bytes:
      if isinstance(content,bytes): return content
      elif isinstance(content,str): return content.encode("utf-8")
      elif isinstance(content,Response): return content
      elif isinstance(content,Dynamic): return content.__repr__().encode("utf-8")
      return Utility.ToJson(content).encode("utf-8")
     
  def GenerateCerts(pNames:list[str])->tuple:
    if not Utility.CanImport('cryptography'): raise 'Cryptography not installed'
    from datetime import datetime,timezone,timedelta
    import socket
    import ipaddress
    import re
    from cryptography import x509
    from cryptography.x509.oid import NameOID
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.backends import default_backend
    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.primitives.asymmetric import rsa
    
    _HostName=socket.gethostname()
    pNames.append(_HostName)
    pNames.append(socket.getfqdn())
    pNames.append(socket.gethostbyname(_HostName))
    _CertFile = f'{_HostName}.crt'
    _KeyFile = f'{_HostName}.key'
    if os.path.isfile(_CertFile) and os.path.isfile(_KeyFile): return _CertFile,_KeyFile
    _Key = rsa.generate_private_key(public_exponent=65537,key_size=2048,backend=default_backend(),)    
    _Name = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, _HostName)])
    _AltNames = [x509.DNSName(x) for x in pNames]
    for n in pNames:
      if re.match("^[0-9]{1,3}\\.[0-9]{1,3}\\.[0-9]{1,3}\\.[0-9]{1,3}$",n):
        _AltNames.append(x509.IPAddress(ipaddress.ip_address(n)))
    _SubAltNames = x509.SubjectAlternativeName(_AltNames)
    _Constraints = x509.BasicConstraints(ca=False,path_length=None)
    _Now = datetime.now(tz=timezone.utc)
    _Cert = (
      x509.CertificateBuilder()
        .subject_name(_Name)
        .issuer_name(_Name)
        .public_key(_Key.public_key())
        .serial_number(1000)
        .not_valid_before(_Now)
        .not_valid_after(_Now+timedelta(days=10*365))
        .add_extension(_Constraints, False)
        .add_extension(_SubAltNames, False)
        .sign(_Key, hashes.SHA256(), default_backend())
    )
    _CertData = _Cert.public_bytes(encoding=serialization.Encoding.PEM)
    _KeyData = _Key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption(),
    )
    with open(_CertFile, "wt") as f:
      f.write(_CertData.decode('utf-8'))
    with open(_KeyFile, "wt") as f:
      f.write(_KeyData.decode('utf-8'))
    return _CertFile,_KeyFile

  def __init__(self,Port=None,Name='WebServer',Root='/',Tls=[]):
    super().__init__(Name,30)
    self.Port = Port
    if not self.Port:
      _Socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
      _PortRange = [443,8443] if Tls else range(80,90)
      for _Port in _PortRange:
        try:
          _Socket.bind(('0.0.0.0',_Port))
          _Socket.close()
          self.Port = _Port
          break
        except Exception: self.Logger.Error(f'Port {_Port} not available')
    if not self.Port: raise 'No port to listen'
    self.App = FastAPI()
    self.App.middleware('https' if Tls else 'http')(self.OnRequest)
    if Tls: #Generate certificate if required
      _CertFile,_KeyFile = WebServer.GenerateCerts(Tls)
      _Config = uvicorn.Config(self.App,host='0.0.0.0',port=self.Port,log_config=None,ssl_certfile=_CertFile,ssl_keyfile=_KeyFile,log_level='warning')
    else:
      _Config = uvicorn.Config(self.App,host='0.0.0.0',port=self.Port,log_config=None,log_level='warning')
    self.Server = uvicorn.Server(_Config)    
    self.Root=Root

  #region helpers
  @property
  def Method(self): return self._Request.method
  @property
  def URL(self): return str(self._Request.url)
  @property
  async def Data(self):
    if self._Request.headers.get('content-type','').startswith('application/json'):
      _Data = await self._Request.json()
      return Dynamic.FromString(_Data)
    elif self._Request.headers.get('content-type','').startswith('application/x-www-form-urlencoded'):
      _Data = await self._Request.form()
      return Dynamic({x:_Data.get(x) for x in _Data.keys()},CaseSensitive=False)
    elif int(self._Request.headers.get('content-length','')) > 0:
      _Data = await self._Request.body()
      return _Data
    return None
  #endregion

  #May be overridden by the implementation, but be sure to call super().OnRequest
  async def OnRequest(self,pRequest:Request,pNext):
    _Start = time.perf_counter()
    self._Request = pRequest
    self.QueryString = Dynamic(CaseSensitive=False)
    _Param = self._Request.query_params
    for k,v in _Param.items():
      if v.startswith(('{','[','(')):
        self.QueryString.Set(k,ast.literal_eval(v))
      else:
        self.QueryString.Set(k,v)
    try:
      _Response = await pNext(pRequest)
    except (asyncio.CancelledError, ConnectionResetError):
        self.Logger.Debug("Client disconnected early")
        return None
    _Time = time.perf_counter() - _Start
    self.Logger.Debug(f'{pRequest.method} {pRequest.url} - {_Response.status_code} in {round(_Time*1000)}ms')
    return _Response

  async def Begin(self):
    import asyncio
    asyncio.create_task(self.Server.serve())
    self.Logger.Info(f'Listening on {self.Port}')
    return True

  async def Run(self):
    return True

  async def End(self):
    self.Server.should_exit = True
    return True

  def AddRoute(self,pRoute,pName,pHandler,pMethods):
    self.App.add_api_route(pRoute,pHandler,methods=pMethods,name=pName)
    
  def SendFile(self,pFile:str=None):
    if not pFile or pFile=='/': pFile = 'index.html'
    if not os.path.isfile(self.Root+'/'+pFile):
      return Response('No such file',404)
    return FileResponse(self.Root+'/'+pFile)
