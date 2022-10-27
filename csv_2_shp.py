import os

dir_path = 'C:\\Users\\qw2\\Desktop\\Pain_Trial_GPS\\csv_files'

shp_out = 'C:\\Users\\qw2\\Desktop\\Pain_Trial_GPS\\shp'

#kml_out = '/home/ben/DITT/Pain_Trial_GPS/kml'

nt_extent = QgsRectangle(129.00047612800000252, -25.9986182724999999, 138.00119971199998758, -10.96591400600000021)

for file in os.listdir(dir_path):
#    print(file)
    f_path = os.path.join(dir_path, file)
    print(f_path)
    uri = f'file:///{f_path}?type=csv&maxFields=10000&detectTypes=yes&xField=Longitude&yField=Latitude&crs=EPSG:4326&spatialIndex=no&subsetIndex=no&watchFile=no'
    f_name = file.split('.')[0]
    lyr = QgsVectorLayer(uri, f_name, 'delimitedtext')
    if not lyr.isValid():
        print(f'layer {f_name} is not valid')
        continue
    shp_point_path = os.path.join(shp_out, f'{f_name}.shp')
    flds = lyr.fields()
    shp_writer = QgsVectorFileWriter(shp_point_path,
                                'utf-8',
                                flds,
                                QgsWkbTypes.Point,
                                QgsCoordinateReferenceSystem('epsg:4326'),
                                'ESRI Shapefile')
#    QgsProject.instance().addMapLayer(lyr)
    sp_idx = QgsSpatialIndex(lyr.getFeatures())
    outliers_removed = sp_idx.intersects(nt_extent)
    fts_to_write = [f for f in lyr.getFeatures(outliers_removed)]
    shp_writer.addFeatures(fts_to_write)
    
    err = shp_writer.lastError()
    if err:
        print(err)
    
    del shp_writer
    
    print('Done')
#    break