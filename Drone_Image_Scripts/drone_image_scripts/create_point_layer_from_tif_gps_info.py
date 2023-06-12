from PIL import Image


def get_tif_gps_info(image_file):
    
    xmp_string = image_file.tag[700].decode()

    lat_string = xmp_string.split('GpsLatitude=')[1][2:14]

    lon_string = xmp_string.split('GpsLongitude=')[1][2:15]

    alt_string = xmp_string.split('AbsoluteAltitude=')[1][2:10].split('"')[0]
    
    return (-float(lat_string), float(lon_string), float(alt_string))

lyr = QgsVectorLayer('Point?crs=epsg:4326', 'MS_img_locations', 'memory')

fields = QgsFields()

fields_to_add = [QgsField('Name', QVariant.String),
                QgsField('Latitude', QVariant.Double, len=12, prec=8),
                QgsField('Longitude', QVariant.Double, len=12, prec=8),
                QgsField('Altitude', QVariant.Double, len=7, prec=3)]
                
for fld in fields_to_add:
    fields.append(fld)
    
lyr.dataProvider().addAttributes(fields)

lyr.updateFields()
################################################################################
image_folders = [
    '/media/ben/GIS Data/Z1_Drone/19-05-23_Folder_1/DJI_202305191156_001_gate-pdk1',
    '/media/ben/GIS Data/Z1_Drone/19-05-23_Folder_2/DJI_202305191233_002_gate-pdk1',
    '/media/ben/GIS Data/Z1_Drone/19-05-23_Folder_3/DJI_202305191306_003_gate-pdk1'
                ]

feats = []

################################################################################
for folder_path in image_folders:
    folder_files = [file for file in os.scandir(folder_path)]
    rgb_images = [f for f in folder_files if f.name.split('.')[1] == 'TIF']

    for image_file in rgb_images:
        img_name = image_file.name.split('.')[0]
        img_path = image_file.path
        img=Image.open(img_path)
        info_tup = get_tif_gps_info(img)
        lat = info_tup[0]
        lon = info_tup[1]
        alt = info_tup[2]
        
        feat = QgsFeature(lyr.fields())
        pt = QgsPoint()
        pt.setX(lon)
        pt.setY(lat)
        pt.addZValue(alt)
        # print(pt.z())
        geom = QgsGeometry(pt)
        # print(geom)
        feat.setGeometry(geom)
        feat.setAttributes([img_name, str(lat), str(lon), str(alt)])
        feats.append(feat)
    
lyr.dataProvider().addFeatures(feats)
QgsProject.instance().addMapLayer(lyr)