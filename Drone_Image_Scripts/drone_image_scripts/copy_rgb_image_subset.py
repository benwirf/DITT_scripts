import shutil

subset_layer = QgsProject.instance().mapLayersByName('rgb_selected')[0]

subset_names = [ft['Name'] for ft in subset_layer.getFeatures()]

destination_folder_path = '/home/ben/Drone_Beatrice/subset_1'

image_folders = ['/home/ben/Drone_Beatrice/RGB']

cnt = 0

for folder_path in image_folders:
    folder_files = [file for file in os.scandir(folder_path)]
    for f in folder_files:
        if cnt == 1600:
            break
        if f.name.split('.')[1] == 'JPG':
            if f.name.split('.')[0] in subset_names:
                src = f.path
                # print(src)
                shutil.copy2(src, destination_folder_path)
                cnt+=1
            
print(f'Copied {cnt} RGB images')