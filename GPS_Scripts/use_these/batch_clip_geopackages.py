import os

source_folder = r'C:\Users\qw2\Desktop\FireGraze_GPS\GPS data\FireGraze dry season 2023 GPS data\Conkerberry\Raw_GeoPackages'

output_folder = r'C:\Users\qw2\Desktop\FireGraze_GPS\GPS data\FireGraze dry season 2023 GPS data\Conkerberry\Clipped_GeoPackages'

paddocks_uri = r'C:\Users\qw2\Desktop\FireGraze_GPS\DATA\Paddocks_buffered_350.gpkg'

pdk_lyr = QgsVectorLayer(paddocks_uri, '', 'ogr')

pdk_name = 'Conkerberry'

pdk_lyr.setSubsetString(f'"Name" LIKE \'{pdk_name}\'')

iface.layerTreeView().refreshLayerSymbology(pdk_lyr.id())

for file in os.scandir(source_folder):
    gps_lyr_uri = os.path.join(source_folder, file.name)
    gps_lyr = QgsVectorLayer(gps_lyr_uri, '', 'ogr')
    
    output_path = os.path.join(output_folder, file.name)
    clip_params = {'INPUT':gps_lyr,
                    'OVERLAY':pdk_lyr,
                    'OUTPUT':output_path}
    processing.run("native:clip", clip_params)
    
pdk_lyr.setSubsetString('')

iface.layerTreeView().refreshLayerSymbology(pdk_lyr.id())

print('Done')