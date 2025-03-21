import os
from datetime import *

dir_path = 'Path\\to\\csv_files'

gpkg_out = 'Path\\to\\gpkg'

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
    gpkg_point_path = os.path.join(gpkg_out, 'gps_points', f'{f_name}.gpkg')
    flds = lyr.fields()
    gpkg_writer = QgsVectorFileWriter(gpkg_point_path,
                                'utf-8',
                                flds,
                                QgsWkbTypes.Point,
                                QgsCoordinateReferenceSystem('epsg:4326'),
                                "GPKG")
#    QgsProject.instance().addMapLayer(lyr)
    sp_idx = QgsSpatialIndex(lyr.getFeatures())
    outliers_removed = sp_idx.intersects(nt_extent)
    fts_to_write = [f for f in lyr.getFeatures(outliers_removed)]
    gpkg_writer.addFeatures(fts_to_write)
    
    err = gpkg_writer.lastError()
    if err:
        print(err)
    
    del gpkg_writer
    
    # run Points To Path
    
    print('Done')
#    break
