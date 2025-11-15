import Bluetooth

class DATA_OBJECT():
  def __init__(self,**kwargs):
    self.Name = kwargs['Name'] if 'Name' in kwargs else None
    self.Units = kwargs['Unit'] if 'Unit' in kwargs else None
    self.Type = kwargs['Type'] if 'Type' in kwargs else 'I'
    self.Length = kwargs['Length'] if 'Length' in kwargs else 1
    self.Scale = kwargs['Scale'] if 'Scale' in kwargs else 1

DataTypes: dict[int, DATA_OBJECT] = {
    0x00: DATA_OBJECT(Name='PACKETID'),
    0x01: DATA_OBJECT(Name='BATTERY',Units='%'),
    0x02: DATA_OBJECT(Name='TEMPERATURE',Units='C',Length=2,Type="SI",Scale=0.01),
    0x03: DATA_OBJECT(Name='HUMIDITY',Units='%',Length=2,Scale=0.01),
    # 0x04: DATA_OBJECT(Name='PRESSURE',Units='MBAR',Length=3,Scale=0.01),
    # 0x05: DATA_OBJECT(Name='LIGHT',Units='Lux',Length=3,Scale=0.01),
    # 0x06: DATA_OBJECT(Name='MASS',Units='KG',Length=2,Scale=0.01),
    # 0x07: DATA_OBJECT(Name='MASS',Units='lbs'.Length=2,Scale=0.01),
    # 0x08: DATA_OBJECT(Name='DEW_POINT',Unit='C',Length=2,Type="SI",Scale=0.01),
    # 0x09: DATA_OBJECT(
    #     Name='SensorLibrary.COUNT__NONE,
    #     Length=1,
    # ),
    # 0x0A: DATA_OBJECT(
    #     Name='SensorLibrary.ENERGY__ENERGY_KILO_WATT_HOUR,
    #     Length=3,
    #     Scale=0.001,
    # ),
    # 0x0B: DATA_OBJECT(
    #     Name='SensorLibrary.POWER__POWER_WATT,
    #     Length=3,
    #     Scale=0.01,
    # ),
    0x0C: DATA_OBJECT(Name='VOLTAGE',Units='V',Length=2,Scale=0.001),
    # 0x0D: DATA_OBJECT(
    #     Name='SensorLibrary.PM25__CONCENTRATION_MICROGRAMS_PER_CUBIC_METER,
    #     Length=2,
    # ),
    # 0x0E: DATA_OBJECT(
    #     Name='SensorLibrary.PM10__CONCENTRATION_MICROGRAMS_PER_CUBIC_METER,
    #     Length=2,
    # ),
    # 0x0F: DATA_OBJECT(
    #     Name='description.BaseBinarySensorDescription(
    #         device_class=BinarySensorDeviceClass.GENERIC,
    #     ),
    # ),
    0x10: DATA_OBJECT(Name='POWER',Units='On/Off'),
    0x11: DATA_OBJECT(Name='OPEN',Units='Yes/No'),
    # 0x12: DATA_OBJECT(
    #     Name='SensorLibrary.CO2__CONCENTRATION_PARTS_PER_MILLION,
    #     Length=2,
    # ),
    # 0x13: DATA_OBJECT(
    #     Name='(
    #         SensorLibrary.VOLATILE_ORGANIC_COMPOUNDS__CONCENTRATION_MICROGRAMS_PER_CUBIC_METER
    #     ),
    #     Length=2,
    # ),
    # 0x14: DATA_OBJECT(
    #     Name='SensorLibrary.MOISTURE__PERCENTAGE,
    #     Length=2,
    #     Scale=0.01,
    # ),
    # 0x15: DATA_OBJECT(
    #     Name='description.BaseBinarySensorDescription(
    #         device_class=BinarySensorDeviceClass.BATTERY,
    #     )
    # ),
    # 0x16: DATA_OBJECT(
    #     Name='description.BaseBinarySensorDescription(
    #         device_class=BinarySensorDeviceClass.BATTERY_CHARGING,
    #     )
    # ),
    # 0x17: DATA_OBJECT(
    #     Name='description.BaseBinarySensorDescription(
    #         device_class=BinarySensorDeviceClass.CO,
    #     )
    # ),
    # 0x18: DATA_OBJECT(
    #     Name='description.BaseBinarySensorDescription(
    #         device_class=BinarySensorDeviceClass.COLD,
    #     )
    # ),
    # 0x19: DATA_OBJECT(
    #     Name='description.BaseBinarySensorDescription(
    #         device_class=BinarySensorDeviceClass.CONNECTIVITY,
    #     )
    # ),
    # 0x1A: DATA_OBJECT(
    #     Name='description.BaseBinarySensorDescription(
    #         device_class=BinarySensorDeviceClass.DOOR,
    #     )
    # ),
    # 0x1B: DATA_OBJECT(
    #     Name='description.BaseBinarySensorDescription(
    #         device_class=BinarySensorDeviceClass.GARAGE_DOOR,
    #     )
    # ),
    # 0x1C: DATA_OBJECT(
    #     Name='description.BaseBinarySensorDescription(
    #         device_class=BinarySensorDeviceClass.GAS,
    #     )
    # ),
    # 0x1D: DATA_OBJECT(
    #     Name='description.BaseBinarySensorDescription(
    #         device_class=BinarySensorDeviceClass.HEAT,
    #     )
    # ),
    # 0x1E: DATA_OBJECT(
    #     Name='description.BaseBinarySensorDescription(
    #         device_class=BinarySensorDeviceClass.LIGHT,
    #     )
    # ),
    # 0x1F: DATA_OBJECT(
    #     Name='description.BaseBinarySensorDescription(
    #         device_class=BinarySensorDeviceClass.LOCK,
    #     )
    # ),
    # 0x20: DATA_OBJECT(
    #     Name='description.BaseBinarySensorDescription(
    #         device_class=BinarySensorDeviceClass.MOISTURE,
    #     )
    # ),
    # 0x21: DATA_OBJECT(
    #     Name='description.BaseBinarySensorDescription(
    #         device_class=BinarySensorDeviceClass.MOTION,
    #     )
    # ),
    # 0x22: DATA_OBJECT(
    #     Name='description.BaseBinarySensorDescription(
    #         device_class=BinarySensorDeviceClass.MOVING,
    #     )
    # ),
    # 0x23: DATA_OBJECT(
    #     Name='description.BaseBinarySensorDescription(
    #         device_class=BinarySensorDeviceClass.OCCUPANCY,
    #     )
    # ),
    # 0x24: DATA_OBJECT(
    #     Name='description.BaseBinarySensorDescription(
    #         device_class=BinarySensorDeviceClass.PLUG,
    #     )
    # ),
    # 0x25: DATA_OBJECT(
    #     Name='description.BaseBinarySensorDescription(
    #         device_class=BinarySensorDeviceClass.PRESENCE,
    #     )
    # ),
    # 0x26: DATA_OBJECT(
    #     Name='description.BaseBinarySensorDescription(
    #         device_class=BinarySensorDeviceClass.PROBLEM,
    #     )
    # ),
    # 0x27: DATA_OBJECT(
    #     Name='description.BaseBinarySensorDescription(
    #         device_class=BinarySensorDeviceClass.RUNNING,
    #     )
    # ),
    # 0x28: DATA_OBJECT(
    #     Name='description.BaseBinarySensorDescription(
    #         device_class=BinarySensorDeviceClass.SAFETY,
    #     )
    # ),
    # 0x29: DATA_OBJECT(
    #     Name='description.BaseBinarySensorDescription(
    #         device_class=BinarySensorDeviceClass.SMOKE,
    #     )
    # ),
    # 0x2A: DATA_OBJECT(
    #     Name='description.BaseBinarySensorDescription(
    #         device_class=BinarySensorDeviceClass.SOUND,
    #     )
    # ),
    # 0x2B: DATA_OBJECT(
    #     Name='description.BaseBinarySensorDescription(
    #         device_class=BinarySensorDeviceClass.TAMPER,
    #     )
    # ),
    # 0x2C: DATA_OBJECT(
    #     Name='description.BaseBinarySensorDescription(
    #         device_class=BinarySensorDeviceClass.VIBRATION,
    #     )
    # ),
    # 0x2D: DATA_OBJECT(
    #     Name='description.BaseBinarySensorDescription(
    #         device_class=BinarySensorDeviceClass.WINDOW,
    #     )
    # ),
    # 0x2E: DATA_OBJECT(Name='SensorLibrary.HUMIDITY__PERCENTAGE),
    # 0x2F: DATA_OBJECT(Name='SensorLibrary.MOISTURE__PERCENTAGE),
    # 0x3A: DATA_OBJECT(Name='EventDeviceKeys.BUTTON),
    # 0x3C: DATA_OBJECT(
    #     Name='EventDeviceKeys.DIMMER,
    #     Length=2,
    # ),
    # 0x3D: DATA_OBJECT(
    #     Name='SensorLibrary.COUNT__NONE,
    #     Length=2,
    # ),
    0x3E: DATA_OBJECT(Name='COUNT',Length=4),
    # 0x3F: DATA_OBJECT(
    #     Name='SensorLibrary.ROTATION__DEGREE,
    #     Length=2,
    #     Type="signed_integer",
    #     Scale=0.1,
    # ),
    # 0x40: DATA_OBJECT(
    #     Name='SensorLibrary.DISTANCE__LENGTH_MILLIMETERS,
    #     Length=2,
    #     Scale=1,
    # ),
    # 0x41: DATA_OBJECT(
    #     Name='SensorLibrary.DISTANCE__LENGTH_METERS,
    #     Length=2,
    #     Scale=0.1,
    # ),
    # 0x42: DATA_OBJECT(
    #     Name='SensorLibrary.DURATION__TIME_SECONDS,
    #     Length=3,
    #     Scale=0.001,
    # ),
    # 0x43: DATA_OBJECT(
    #     Name='SensorLibrary.CURRENT__ELECTRIC_CURRENT_AMPERE,
    #     Length=2,
    #     Scale=0.001,
    # ),
    # 0x44: DATA_OBJECT(
    #     Name='SensorLibrary.SPEED__SPEED_METERS_PER_SECOND,
    #     Length=2,
    #     Scale=0.01,
    # ),
    # 0x45: DATA_OBJECT(
    #     Name='SensorLibrary.TEMPERATURE__CELSIUS,
    #     Length=2,
    #     Type="signed_integer",
    #     Scale=0.1,
    # ),
    # 0x46: DATA_OBJECT(
    #     Name='SensorLibrary.UV_INDEX__NONE,
    #     Length=1,
    #     Scale=0.1,
    # ),
    # 0x47: DATA_OBJECT(
    #     Name='SensorLibrary.VOLUME__VOLUME_LITERS,
    #     Length=2,
    #     Scale=0.1,
    # ),
    # 0x48: DATA_OBJECT(
    #     Name='SensorLibrary.VOLUME__VOLUME_MILLILITERS,
    #     Length=2,
    # ),
    # 0x49: DATA_OBJECT(
    #     Name='SensorLibrary.VOLUME_FLOW_RATE__VOLUME_FLOW_RATE_CUBIC_METERS_PER_HOUR,
    #     Length=2,
    #     Scale=0.001,
    # ),
    # 0x4A: DATA_OBJECT(
    #     Name='SensorLibrary.VOLTAGE__ELECTRIC_POTENTIAL_VOLT,
    #     Length=2,
    #     Scale=0.1,
    # ),
    # 0x4B: DATA_OBJECT(
    #     Name='SensorLibrary.GAS__VOLUME_CUBIC_METERS,
    #     Length=3,
    #     Scale=0.001,
    # ),
    # 0x4C: DATA_OBJECT(
    #     Name='SensorLibrary.GAS__VOLUME_CUBIC_METERS,
    #     Length=4,
    #     Scale=0.001,
    # ),
    # 0x4D: DATA_OBJECT(
    #     Name='SensorLibrary.ENERGY__ENERGY_KILO_WATT_HOUR,
    #     Length=4,
    #     Scale=0.001,
    # ),
    # 0x4E: DATA_OBJECT(
    #     Name='SensorLibrary.VOLUME__VOLUME_LITERS,
    #     Length=4,
    #     Scale=0.001,
    # ),
    # 0x4F: DATA_OBJECT(
    #     Name='SensorLibrary.WATER__VOLUME_LITERS,
    #     Length=4,
    #     Scale=0.001,
    # ),
    # 0x50: DATA_OBJECT(
    #     Name='SensorLibrary.TIMESTAMP__NONE,
    #     Length=4,
    #     Type="timestamp",
    # ),
    # 0x51: DATA_OBJECT(
    #     Name='SensorLibrary.ACCELERATION__ACCELERATION_METERS_PER_SQUARE_SECOND,
    #     Length=2,
    #     Scale=0.001,
    # ),
    # 0x52: DATA_OBJECT(
    #     Name='SensorLibrary.GYROSCOPE__GYROSCOPE_DEGREES_PER_SECOND,
    #     Length=2,
    #     Scale=0.001,
    # ),
    # 0x53: DATA_OBJECT(
    #     Name='ExtendedSensorLibrary.TEXT__NONE,
    #     Type="string",
    # ),
    # 0x54: DATA_OBJECT(
    #     Name='ExtendedSensorLibrary.RAW__NONE,
    #     Type="raw",
    # ),
    # 0x55: DATA_OBJECT(
    #     Name='ExtendedSensorLibrary.VOLUME_STORAGE__VOLUME_LITERS,
    #     Length=4,
    #     Scale=0.001,
    # ),
    # 0x56: DATA_OBJECT(
    #     Name='SensorLibrary.CONDUCTIVITY__CONDUCTIVITY,
    #     Length=2,
    # ),
    # 0x57: DATA_OBJECT(
    #     Name='SensorLibrary.TEMPERATURE__CELSIUS,
    #     Length=1,
    #     Type="signed_integer",
    # ),
    # 0x58: DATA_OBJECT(
    #     Name='SensorLibrary.TEMPERATURE__CELSIUS,
    #     Length=1,
    #     Type="signed_integer",
    #     Scale=0.35,
    # ),
    # 0x59: DATA_OBJECT(
    #     Name='SensorLibrary.COUNT__NONE,
    #     Length=1,
    #     Type="signed_integer",
    # ),
    # 0x5A: DATA_OBJECT(
    #     Name='SensorLibrary.COUNT__NONE,
    #     Length=2,
    #     Type="signed_integer",
    # ),
    # 0x5B: DATA_OBJECT(
    #     Name='SensorLibrary.COUNT__NONE,
    #     Length=4,
    #     Type="signed_integer",
    # ),
    # 0x5C: DATA_OBJECT(
    #     Name='SensorLibrary.POWER__POWER_WATT,
    #     Length=4,
    #     Scale=0.01,
    #     Type="signed_integer",
    # ),
    # 0x5D: DATA_OBJECT(
    #     Name='SensorLibrary.CURRENT__ELECTRIC_CURRENT_AMPERE,
    #     Length=2,
    #     Scale=0.001,
    #     Type="signed_integer",
    # ),
}

  #https://bthome.io/v1/

#https://bthome.io/v1/
async def Parse(pDevice:Bluetooth.Device,pData:dict[str:bytes])->list[str]:
  _Result = {}
  if _Data:= next((pData[x] for x in pData.keys() if '181c' in x),None):
    _Result = ParseV1(_Data)
  if _Data:= next((pData[x] for x in pData.keys() if 'fcd2' in x),None):
    _Result = ParseV2(_Data)
  _UpdatedEntities = []
  for n,v in _Result.items():
      e = pDevice.Entities.Get(n)
      if e: 
        await e.OnValue(v)
        _UpdatedEntities.append(e.Name)
      # else:
        # pDevice.Logger.Warning(f'Extra data:{n}={v}')
  return _UpdatedEntities

def GetData(pData:bytes,pType:DATA_OBJECT)->any:
  _Value = None
  if pType.Type=='I':
    _Value = int.from_bytes(pData,'little',signed=False)
  elif pType.Type=='SI':
    _Value = int.from_bytes(pData,'little',signed=True)
  elif pType.Type=='F':
    _Value = float.from_bytes(pData,'little')
  elif pType.Type==4:
    _Value = pData.decode('utf-8')
  else: 
    return None,None
  if isinstance(_Value,int) or isinstance(_Value,float): _Value = _Value*pType.Scale
  if isinstance(_Value,float): _Value = round(_Value,2)
  return pType.Name,_Value

def ParseV1(pData:bytes)->dict[str:any]:
  #_Data = b'\x02\x00\xec\x02\x10\x00\x03\x0c\x14\x10'
  #_Data = b'\x02\x00\x01\x23\x02\xfa\x09\x03\x03\xeb\x0f\x02\x01\x3d'
  _Result = {}
  _Ptr = 0
  _Max = len(pData)
  while _Ptr < _Max:
    _PacketHeader = pData[_Ptr]
    _PacketLength = _PacketHeader & 0x1F
    _PacketType = _PacketHeader >> 5
    _ObjectType = pData[_Ptr+1]
    _ObjectData = pData[_Ptr+2:_Ptr+2+_PacketLength-1]
    _Ptr = _Ptr + _PacketLength + 1
    _Type = DataTypes[_ObjectType] if _ObjectType in DataTypes else None
    if _Type is None:
      raise 'Invalid data object'
    n,v = GetData(_ObjectData,_Type)
    if not n: continue
    if n=='TEMPERATURE': 
      v = round(32+v*9/5,2)
    _Result[n] = v
  return _Result

def ParseV2(pData:bytes)->dict[str,any]:
  _Result = {}
  if not pData[0]==0x40: return _Result
  _Ptr = 1
  _Max = len(pData)
  while _Ptr < _Max:
    _ObjectType = pData[_Ptr]
    _Type = DataTypes[_ObjectType] if _ObjectType in DataTypes else None
    if _Type is None: 
      raise 'Invalid data object'
    _ObjectData = pData[_Ptr+1:_Ptr+1+_Type.Length]
    _Ptr = _Ptr + _Type.Length + 1
    n,v = GetData(_ObjectData,_Type)
    if not n: continue
    if n=='TEMPERATURE': 
      v = round(32+v*9/5,2)
    _Result[n] = v
  return _Result
