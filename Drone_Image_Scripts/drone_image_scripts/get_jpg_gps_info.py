# https://medium.com/geekculture/extract-gps-information-from-photos-using-python-79288c58ccd9

from PIL import Image
from PIL.ExifTags import TAGS
from PIL.ExifTags import GPSTAGS

# print(TAGS)
# print(GPSTAGS)

folder_path = 'C:\\Users\\Ben\\Desktop\\gate-pdk_drone\\DJI_202305191306_003_gate-pdk1'
folder_files = [file for file in os.scandir(folder_path)]
rgb_images = [f for f in folder_files if f.name.split('.')[1] == 'JPG']
image_file = rgb_images[0]
print(image_file.name.split('.')[0])
img_path = image_file.path

# Open Image
img = Image.open(img_path)

def get_exif_gps_info(image_file):
    #Get EXIF Data
    exif_table={}

    for k, v in image_file._getexif().items():
        tag=TAGS.get(k)
        exif_table[tag]=v
        
    # print(exif_table)

    gps_info={}

    for k, v in exif_table['GPSInfo'].items():
        geo_tag=GPSTAGS.get(k)
        gps_info[geo_tag]=v
        
    print(gps_info)
    
    # Comma separated tuples (12.0, 38.0, 15.9706)    
    lat_dms = gps_info['GPSLatitude']
    lon_dms = gps_info['GPSLongitude']
    gps_alt = gps_info['GPSAltitude']
    
    lat_dd = round(float((lat_dms[0])+(lat_dms[1]/60)+(lat_dms[2]/3600)), 8)
    lon_dd = round(float((lon_dms[0])+(lon_dms[1]/60)+(lon_dms[2]/3600)), 8)
    
    return (lat_dd, lon_dd, gps_alt)
    
print(get_exif_gps_info(img))