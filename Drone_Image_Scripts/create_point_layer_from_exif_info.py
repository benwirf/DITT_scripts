from PIL import Image
from PIL.ExifTags import TAGS
from PIL.ExifTags import GPSTAGS


def get_exif_gps_info(image_file):
    exif_table={}
    
    for k, v in img._getexif().items():
        tag=TAGS.get(k)
        exif_table[tag]=v
        
    dt = exif_table['DateTime']

    gps_info={}

    for k, v in exif_table['GPSInfo'].items():
        geo_tag=GPSTAGS.get(k)
        gps_info[geo_tag]=v

    lat_dms = gps_info['GPSLatitude']
    lon_dms = gps_info['GPSLongitude']
    gps_alt = gps_info['GPSAltitude']
    
    lat_dd = round(float((lat_dms[0])+(lat_dms[1]/60)+(lat_dms[2]/3600)), 8)
    lon_dd = round(float((lon_dms[0])+(lon_dms[1]/60)+(lon_dms[2]/3600)), 8)
    
    return (dt, -lat_dd, lon_dd, gps_alt)

lyr = QgsVectorLayer('Point?crs=epsg:4326', 'Image_locations', 'memory')

fields = QgsFields()

fields_to_add = [QgsField('Name', QVariant.String),
                QgsField('Time', QVariant.String),
                QgsField('Latitude', QVariant.Double, len=12, prec=8),
                QgsField('Longitude', QVariant.Double, len=12, prec=8),
                QgsField('Altitude', QVariant.Double, len=7, prec=3)]
                
for fld in fields_to_add:
    fields.append(fld)
    
lyr.dataProvider().addAttributes(fields)

lyr.updateFields()
    
folder_path = 'gate-pdk_drone\\DJI_202305191306_003_gate-pdk1'
folder_files = [file for file in os.scandir(folder_path)]
rgb_images = [f for f in folder_files if f.name.split('.')[1] == 'JPG']

feats = []

cnt = 1

for image_file in rgb_images:
    img_name = image_file.name.split('.')[0]
    img_path = image_file.path
    img=Image.open(img_path)
    info_tup = get_exif_gps_info(img)
    date_time = info_tup[0]
    lat = info_tup[1]
    lon = info_tup[2]
    alt = info_tup[3]
    
    feat = QgsFeature(lyr.fields())
    pt = QgsPoint()
    pt.setX(lon)
    pt.setY(lat)
    pt.addZValue(alt)
    # print(pt.z())
    geom = QgsGeometry(pt)
    # print(geom)
    feat.setGeometry(geom)
    feat.setAttributes([img_name, date_time, str(lat), str(lon), str(alt)])
    feats.append(feat)
    
lyr.dataProvider().addFeatures(feats)
QgsProject.instance().addMapLayer(lyr)
    

