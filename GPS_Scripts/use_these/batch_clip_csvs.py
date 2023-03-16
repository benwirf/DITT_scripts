from pathlib import Path
import os

src_folder = 'C:\\Users\\qw2\\Desktop\\Paddock_Power_GPS\\GPS Data Aug21-March22\\CSVs'

for file in os.scandir(src_folder):
#    print(file.name)
    stem = Path(file).stem
#    print(stem)
    out_path = f'C:/Users/qw2/Desktop/Paddock_Power_GPS/heatmap_points/{stem}.gpkg'
    print(f'clipping {stem}')
    clip_params = {'INPUT':f'delimitedtext://file:///C:/Users/qw2/Desktop/Paddock_Power_GPS/GPS%20Data%20Aug21-March22/CSVs/{file.name}?type=csv&maxFields=10000&detectTypes=yes&xField=Longitude&yField=Latitude&crs=EPSG:4326&spatialIndex=no&subsetIndex=no&watchFile=no',
                    'OVERLAY':'C:/Users/qw2/Desktop/Paddock_Power_GPS/Rocklands_Data/Rocklands_paddocks.gpkg|layername=Rocklands_paddocks',
                    'OUTPUT':'TEMPORARY_OUTPUT'}
                    
    clipped = processing.run("native:clip", clip_params)
    print(f'saving {stem}')
    save_params = {'INPUT':clipped['OUTPUT'],
                    'OUTPUT':out_path,
                    'LAYER_NAME':'',
                    'DATASOURCE_OPTIONS':'',
                    'LAYER_OPTIONS':''}
    processing.run("native:savefeatures", save_params)
    
    iface.addVectorLayer(out_path, stem, 'ogr')
print('Done!')