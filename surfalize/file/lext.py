import chardet
import tifffile
import xmltodict
from surfalize.file.common import RawSurface, FileHandler, UNIT_EXPONENT

MAGIC = b'II*'

PAGE_CORRESPONDENCE = {
    "height": 3,
    "color": 0,
    "laser": 2
}
UNIT_CORRESPONDENCE = {
    "2": "um"
}

def convert_bytes2str(text:str|bytes):
    if is_bytes:= isinstance(text, bytes):
        encoding = chardet.detect(text)["encoding"]
        text = text.decode(encoding)
    else:
        pass
    return text

@FileHandler.register_reader(suffix='.lext',magic=MAGIC)
def read_lext(filehandle, read_image_layers=False, encoding='auto'):
  with tifffile.TiffFile(filehandle) as tif:
      metadata = {}
      height_data    = tif.pages[PAGE_CORRESPONDENCE["height"]].asarray().astype(float)
      info = {}
      if 'ImageDescription' in tif.pages[0].tags:
          info = xmltodict.parse(tif.pages[0].tags['ImageDescription'].value)["TiffTagDescData"]
      if 'ExifTag' in tif.pages[0].tags:
          exifinfo = convert_bytes2str(tif.pages[0].tags["ExifTag"].value["DeviceSettingDescription"])
          exifinfo = xmltodict.parse(exifinfo)["ExifTagDescData"]
          info = info|exifinfo
      height_data *= float(info["HeightInfo"]["HeightDataPerPixelZ"])*float(info["ImageCommonSettingsInfo"]["MakerCalibrationValueZ"])
      step_x = float(info["HeightInfo"]["HeightDataPerPixelX"])*float(info["ImageCommonSettingsInfo"]["MakerCalibrationValueX"])
      step_y = float(info["HeightInfo"]["HeightDataPerPixelY"])*float(info["ImageCommonSettingsInfo"]["MakerCalibrationValueY"])
      step_x *= pow(10**UNIT_EXPONENT[UNIT_CORRESPONDENCE[info["HeightInfo"]["HeightDataUnitX"]]],2)
      step_y *= pow(10**UNIT_EXPONENT[UNIT_CORRESPONDENCE[info["HeightInfo"]["HeightDataUnitY"]]],2)
      height_data *= pow(10**UNIT_EXPONENT[UNIT_CORRESPONDENCE[info["HeightInfo"]["HeightDataUnitZ"]]],2)
  
      if read_image_layers:
          image_layers = {}
          image_layers['RGB'] = tif.pages[PAGE_CORRESPONDENCE["color"]].asarray()
          image_layers['Laser'] = tif.pages[PAGE_CORRESPONDENCE["laser"]].asarray()
      else:
          image_layers = None
  return RawSurface(data=height_data, step_x=step_x, step_y=step_y,metadata=metadata, image_layers=image_layers)