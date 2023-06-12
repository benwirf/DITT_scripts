image_folders = [
    '/media/ben/GIS Data/Z1_Drone/19-05-23_Folder_1/DJI_202305191156_001_gate-pdk1',
    '/media/ben/GIS Data/Z1_Drone/19-05-23_Folder_2/DJI_202305191233_002_gate-pdk1',
    '/media/ben/GIS Data/Z1_Drone/19-05-23_Folder_3/DJI_202305191306_003_gate-pdk1'
                ]

for folder_path in image_folders:
    folder_files = [file for file in os.scandir(folder_path)]
    rgb_images = [f for f in folder_files if f.name.split('.')[1] == 'JPG']

    tif_images = [f for f in folder_files if f.name.split('.')[1] == 'TIF']

    print(f'{folder_path.split("/")[-1]} contains {len(rgb_images)} RGB images and {len(tif_images)} multispectral images')