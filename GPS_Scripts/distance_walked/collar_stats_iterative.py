from datetime import datetime
import statistics
import csv
import os

src_folder = r'C:\Users\qw2\Desktop\FireGraze_GPS\GPS data\FireGraze dry season 2023 GPS data\Conkerberry\Collar_Daily_Tracks'

csv_path = r'C:\Users\qw2\Desktop\FireGraze_GPS\GPS data\FireGraze dry season 2023 GPS data\Conkerberry\All_Collars_Summary\Conkerberry_Summary.csv'

csv_file = open(csv_path, mode='w', newline='')

writer = csv.writer(csv_file)

writer.writerow(['Paddock',
                'Collar',
                'Start Date',
                'End Date',
                'Duration',
                'Max Daily Total (km)',
                'On',
                'Min Daily Total (km)',
                'On',
                'Mean Daily Total (km)'])

for file in os.scandir(src_folder):
#    print(file.name)
    file_name = file.name.split('.')[0]
    file_ext = file.name.split('.')[-1]
    if file_ext == 'gpkg':
        #print(file.name)
        pdk_and_collar = file_name[13:]
        #print(pdk_and_collar)
        pdk = pdk_and_collar.split('_')[0]
        collar = pdk_and_collar.split('_')[1]
        src_uri = os.path.join(src_folder, file.name)
        #print(src_uri)
        lyr = QgsVectorLayer(src_uri, pdk_and_collar, 'ogr')
        feats = [ft for ft in lyr.getFeatures()]
        start_date = feats[0]['Date']
        # String format is 2023-05-10
        start_dt = datetime.strptime(start_date, '%Y-%m-%d')
        end_date = feats[-1]['Date']
        end_dt = datetime.strptime(end_date, '%Y-%m-%d')
        t_delta = str(end_dt-start_dt)
        t_delta_days = t_delta.split(',')[0]
        
        #print(f'Dates: {start_date} to {end_date}')
        daily_distances = [ft['Total_distance_km'] for ft in feats[:-1]]#Slice off last features (partial days of walking)
        
        max_dist = max(daily_distances)
        max_dist_dates = [ft['Date'] for ft in feats if ft['Total_distance_km'] == max_dist]
        max_dist_dates_att = ','.join(max_dist_dates)
        min_dist = min(daily_distances)
        min_dist_dates = [ft['Date'] for ft in feats if ft['Total_distance_km'] == min_dist]
        min_dist_dates_att = ', '.join(min_dist_dates)
        mean_dist = statistics.mean(daily_distances)
        #########################TEST OUTPUT####################################
        '''
        print(pdk_and_collar)
        print(f'Dates: {start_date} to {end_date}')
        print(f'Maximum daily distance walked: {max_dist} km')
        print(f'On: {max_dist_dates_att}')
        print(f'Minimum daily distance walked: {min_dist} km')
        print(f'On: {min_dist_dates_att}')
        print(f'Average daily distance walked: {round(mean_dist, 3)} km')
        print('-----------------------------------------')
        '''
        ########################################################################
        writer.writerow([pdk,
                        f'_{collar.zfill(4)}',
                        start_date,
                        end_date,
                        t_delta_days,
                        round(max_dist, 2),
                        max_dist_dates_att,
                        round(min_dist, 2),
                        min_dist_dates_att,
                        round(mean_dist, 2)])
        
        lyr = None
csv_file.close()
del writer
print('Done')
