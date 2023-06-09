folder_path = 'C:\\Users\\Ben\\Desktop\\gate-pdk_drone\\DJI_202305191306_003_gate-pdk1'
folder_files = [file for file in os.scandir(folder_path)]
rgb_images = [f for f in folder_files if f.name.split('.')[1] == 'JPG']
print(len(rgb_images))
image_file = rgb_images[0]
print(image_file.path)
    