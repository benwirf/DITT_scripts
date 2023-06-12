
from PIL import Image
from PIL.TiffTags import TAGS# Unused

# print(TAGS)

folder_path = '/media/ben/GIS Data/Z1_Drone/19-05-23_Folder_3/DJI_202305191306_003_gate-pdk1'
folder_files = [file for file in os.scandir(folder_path)]
rgb_images = [f for f in folder_files if f.name.split('.')[1] == 'TIF']
image_file = rgb_images[0]
# print(image_file.name.split('.')[0])
img_path = image_file.path

# Open Image
img = Image.open(img_path)

xmp_string = img.tag[700].decode()

# print(xmp_string)

lat_string = xmp_string.split('GpsLatitude=')[1][2:14]
print(lat_string)

lon_string = xmp_string.split('GpsLongitude=')[1][2:15]
print(lon_string)

alt_string = xmp_string.split('AbsoluteAltitude=')[1][2:10].split('"')[0]
print(alt_string)