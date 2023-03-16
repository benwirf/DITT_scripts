from pathlib import Path
import os

src_folder = 'C:\\Users\\qw2\\Desktop\\Paddock_Power_GPS\\GPS Data Aug21-March22\\CSVs'

for file in os.scandir(src_folder):
#    print(file.name)
    stem = Path(file).stem
#    print(stem)
    out_path = f'C:/Users/qw2/Desktop/Paddock_Power_GPS/GPS Data Aug21-March22/gpkgs/{stem}.gpkg'
    
    save_params = {'INPUT':f'delimitedtext://file:///C:/Users/qw2/Desktop/Paddock_Power_GPS/GPS%20Data%20Aug21-March22/CSVs/{file.name}?type=csv&maxFields=10000&detectTypes=yes&xField=Longitude&yField=Latitude&crs=EPSG:4326&spatialIndex=no&subsetIndex=no&watchFile=no',
                    'OUTPUT':out_path,
                    'LAYER_NAME':'',
                    'DATASOURCE_OPTIONS':'',
                    'LAYER_OPTIONS':''}
    processing.run("native:savefeatures", save_params)
    
    iface.addVectorLayer(out_path, stem, 'ogr')
print('Done!')

