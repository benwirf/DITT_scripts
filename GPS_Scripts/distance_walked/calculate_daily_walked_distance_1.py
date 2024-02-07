# This approach gets all the unique dates for a collar
# then iterates over the layer and sums the values in the Distance
# column for each date. It works but is unreliable due to some
# very outlandish outliers in the Distance field e.g.670348.75m walked in 20m!

from datetime import datetime
import os

source_folder = r'C:\Users\qw2\Desktop\FireGraze_GPS\GPS data\FireGraze dry season 2023 GPS data\Conkerberry\Clipped_GeoPackages'

def parse_time(time_string):
    # String format like: 2023-05-10 05:56:30Z
    dtt = datetime.strptime(time_string, '%Y-%m-%d %H:%M:%SZ')
    return dtt.date()
    
def parse_date(date_string):
    # String format like: 2023/05/10
    dtd = datetime.strptime(date_string, '%Y/%m/%d')
    return dtd.date()

file_count = 0

for file in os.scandir(source_folder):
    if file_count == 1:
        break
    #print(file.name)
    collar_no = file.name.split('.')[0].split('_')[-1]
    if file.name.split('.')[1] != 'gpkg':
        continue
    uri = os.path.join(source_folder, file.name)
    lyr = QgsVectorLayer(uri, file.name, 'ogr')
    fld_names = [fld.name() for fld in lyr.fields()]
    if 'Date' in fld_names:
        date_fld = 'Date'
    elif 'Time' in fld_names:
        date_fld = 'Time'
    ft_count = 0
    
    all_dates = list(set([parse_date(ft[date_fld]) if date_fld == 'Date' else parse_time(ft[date_fld]) for ft in lyr.getFeatures()]))
    for date in sorted(all_dates):
        date_distances = []
        for ft in lyr.getFeatures():
            if date_fld == 'Date':
                ft_date = parse_date(ft[date_fld])
            elif date_fld == 'Time':
                ft_date = parse_time(ft[date_fld])
                if ft_date == date:
                    date_distances.append(int(float(ft['Distance'])))
        total_distance = sum(date_distances)
        print(f'{collar_no}---{date}---{total_distance/1000}km')

    file_count += 1