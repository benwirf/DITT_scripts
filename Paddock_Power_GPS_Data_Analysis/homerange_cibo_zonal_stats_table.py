# THIS IS AN INCOMPLETE DRAFT SCRIPT

import os

months_dict = dict((month, index) for index, month in enumerate(calendar.month_name) if month)

homerange_source_folder = r'C:/Users/qw2/Desktop/Paddock_Power_GPS/home_range_geopackage_files'

cibo_tsdm_folder = r'C:/Users/qw2/Desktop/Paddock_Power_GPS/Cibo_TSDM'

period_1_months = ['June', 'July', 'August', 'September', 'October', 'November', 'December']
period_2_months = ['January', 'February', 'March', 'April', 'May']

def get_tsdm_layer_path():
    pass

for file in os.scandir(homerange_source_folder):
    if file.name.split('_')[1] == 'gpkg':
        paddock = file.name.split('_')[0][:-4]
        folder_year = file.name.split('_')[0][-4:]
        print(paddock, folder_year)
        # Folder names end in '_gpkg'
        subfolder = os.path.join(homerange_source_folder, file.name)
        for file in os.scandir(subfolder):
            print(file.name)
            # These are actual geopackages
            if file.name.split('.')[1] == 'gpkg':
                month = file.name.split('.')[0].split('_')[1]
                if month in period_1_months:
                    actual_year = str(int(folder_year) - 1)
                elif month in period_2_months:
                    actual_year = folder_year
#                gpkg_uri = os.path.join(subfolder, file.name)
#                pdk_lyr_uri = f'{gpkg_uri}|layername=paddock'
#                homerange_lyr_uri = f'{gpkg_uri}|layername=homerange'
#                pdk_lyr = QgsVectorLayer(pdk_lyr_uri, f'{paddock}', 'ogr')
#                homerange_lyr = QgsVectorLayer(pdk_lyr_uri, 'homerange', 'ogr')
#                print(f'{paddock} folder {folder_year} (actual year {actual_year}){month} is valid: {homerange_lyr.isValid()}')
                mnth_digit = months_dict[month]
                yr_and_mnth = f'{actual_year}{str(mnth_digit).zfill(2)}'
#                print(yr_and_mnth)
                tsdm_fnames = [file.name for file in os.scandir(cibo_tsdm_folder) if yr_and_mnth in file.name]
                if tsdm_fnames:
                    tsdm_fname = tsdm_fnames[0]
                    tsdm_uri = os.path.join(cibo_tsdm_folder, tsdm_fname)
#                    print(tsdm_fname)
#                    print(tsdm_uri)
