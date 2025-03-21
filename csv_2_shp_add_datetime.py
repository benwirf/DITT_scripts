import os
from datetime import datetime

dir_path = 'path/to/csv_files'

gpkg_out = 'path/to/gpkg'

kml_out = 'path/to/kml'

nt_extent = QgsRectangle(129.00047612800000252, -25.9986182724999999, 138.00119971199998758, -10.96591400600000021)

for file in os.listdir(dir_path):
#    print(file)
    uri = f'file:///{dir_path}/{file}?type=csv&maxFields=10000&detectTypes=yes&xField=Longitude&yField=Latitude&crs=EPSG:4326&spatialIndex=no&subsetIndex=no&watchFile=no'
    f_name = file.split('.')[0]
    lyr = QgsVectorLayer(uri, f_name, 'delimitedtext')
#    print(lyr.isValid())
    gpkg_point_path = os.path.join(gpkg_out, 'gps_points', f'{f_name}.gpkg')
    flds = lyr.fields()
    flds.append(QgsField('Date_Time', QVariant.DateTime))
    gpkg_writer = QgsVectorFileWriter(gpkg_point_path,
                                'utf-8',
                                flds,
                                QgsWkbTypes.Point,
                                QgsCoordinateReferenceSystem('epsg:4326'),
                                "GPKG")
    sp_idx = QgsSpatialIndex(lyr.getFeatures())
    outliers_removed = sp_idx.intersects(nt_extent)
    fts_to_write = []
    
    fts = [f for f in lyr.getFeatures(outliers_removed)]
    
    for f in fts:
        feat = QgsFeature()
        feat.setGeometry(f.geometry())
        atts = [a for a in f.attributes()]
        t = f['Time']
        dt = datetime.strptime(t, '%d/%m/%Y %I:%M:%S%p')
        atts.append(QDateTime(dt))
        feat.setAttributes(atts)
#        print(feat.attributes())
        fts_to_write.append(feat)
    
    gpkg_writer.addFeatures(fts_to_write)
    
    err = gpkg_writer.lastError()
    if err:
        print(err)
    
    del gpkg_writer
    break
