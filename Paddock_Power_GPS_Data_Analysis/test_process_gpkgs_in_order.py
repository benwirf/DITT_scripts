from datetime import date
import calendar
import os


months_dict = dict((month, index) for index, month in enumerate(calendar.month_name) if month)

homerange_source_folder = r'C:/Users/qw2/Desktop/Paddock_Power_GPS/home_range_geopackage_files'

period_1_months = ['June', 'July', 'August', 'September', 'October', 'November', 'December']
period_2_months = ['January', 'February', 'March', 'April', 'May']

for file in os.scandir(homerange_source_folder):
    if file.name.split('_')[1] == 'gpkg':
        paddock = file.name.split('_')[0][:-4]
        folder_year = file.name.split('_')[0][-4:]
        print(paddock, folder_year)
        # Folder names end in '_gpkg'
        subfolder = os.path.join(homerange_source_folder, file.name)
        file_dict = {}
        for file in os.scandir(subfolder):
            # These are actual geopackages
            if file.name.split('.')[1] == 'gpkg':
                month = file.name.split('.')[0].split('_')[1]
                if month in period_1_months:
                    actual_year = str(int(folder_year) - 1)
                elif month in period_2_months:
                    actual_year = folder_year
                mnth_digit = months_dict[month]
                yr_and_mnth = f'{actual_year}{str(mnth_digit).zfill(2)}'
                dt = date(int(actual_year), mnth_digit, 1)
                file_dict[file.name]=dt
        sorted_gpkgs = sorted(file_dict.items(), key=lambda x:x[1])
        for x in sorted_gpkgs:
            print(x[0])

