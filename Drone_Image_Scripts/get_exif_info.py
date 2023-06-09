#https://www.thepythoncode.com/article/extracting-image-metadata-in-python

from PIL import Image
from PIL.ExifTags import TAGS

folder_path = 'C:\\Users\\Ben\\Desktop\\gate-pdk_drone\\DJI_202305191306_003_gate-pdk1'
folder_files = [file for file in os.scandir(folder_path)]
rgb_images = [f for f in folder_files if f.name.split('.')[1] == 'JPG']
image_file = rgb_images[0]
img_path = image_file.path
img = Image.open(img_path)
# extract EXIF data
# exifdata = img._getexif()
# # print(exifdata)
# # iterating over all EXIF data fields
# for tag_id in exifdata:
#     # get the tag name, instead of human unreadable tag id
#     tag = TAGS.get(tag_id, tag_id)
#     data = exifdata.get(tag_id)
#     # decode bytes 
#     if isinstance(data, bytes):
#         data = data.decode()
#     print(f"{tag:25}: {data}")
    
########################################

#Get EXIF Data
exif_table={}

for k, v in img._getexif().items():
    tag=TAGS.get(k)
    exif_table[tag]=v
    
print(exif_table['DateTime'])
    
