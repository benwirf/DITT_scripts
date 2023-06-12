import shutil

subset_layer = QgsProject.instance().mapLayersByName('selected')[0]

subset_names = [ft['Name'] for ft in subset_layer.getFeatures()]

destination_folder_path = '/home/ben/Drone_Images/Beatrice_Gate_Paddock_2023/Multi_Spectral_Subset'

image_folders = [
    '/media/ben/GIS Data/Z1_Drone/19-05-23_Folder_1/DJI_202305191156_001_gate-pdk1',
    '/media/ben/GIS Data/Z1_Drone/19-05-23_Folder_2/DJI_202305191233_002_gate-pdk1',
    '/media/ben/GIS Data/Z1_Drone/19-05-23_Folder_3/DJI_202305191306_003_gate-pdk1'
                ]

cnt = 0

for folder_path in image_folders:
    folder_files = [file for file in os.scandir(folder_path)]
    for f in folder_files:
        if cnt == 1600:
            break
        if f.name.split('.')[1] == 'TIF':
            if f.name.split('.')[0] in subset_names:
                src = f.path
                # print(src)
                shutil.copy2(src, destination_folder_path)
                cnt+=1
            
print(f'Copied {cnt} Multi-Spectral images')