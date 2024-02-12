'''
This version sorts daily features by time before creating the track lines.
The files we are working with have 2 different formats. some have a single Time field
With string values like 2023-05-10 05:56:30Z containing date and time, while some
have separate Date & Time fields with values like [2023/05/10 for date] and [05:55:50 for time]
Includes calculations for Max, Min & Mean distance and speed per day
'''

from datetime import datetime
import os
import statistics

start_time = datetime.now()

project = QgsProject.instance()

source_folder = r'C:\Users\qw2\Desktop\FireGraze_GPS\GPS data\FireGraze dry season 2023 GPS data\Conkerberry\Clipped_GeoPackages'

source_files = ["Conkerberry_FireGraze20230904_1106.gpkg",#Done
                "Conkerberry_FireGraze20230904_1155.gpkg",#Done
                "Conkerberry_FireGraze_20230904_0049.gpkg",#Done (only 5 days of data in this file)
                "Conkerberry_FireGraze_20230904_1089.gpkg",#Done
                "Conkerberry_FireGraze_20230904_1094.gpkg",#Done
                "Conkerberry_FireGraze_20230904_1095.gpkg",#Done
                "Conkerberry_FireGraze_20230904_1103.gpkg",#Done
                "Conkerberry_FireGraze_20230904_1112.gpkg",#Done
                "Conkerberry_FireGraze_20230904_1117.gpkg",#Done
                "Conkerberry_FireGraze_20230904_1121.gpkg",#Done
                "Conkerberry_FireGraze_20230904_1126.gpkg",#Done
                "Conkerberry_FireGraze_20230904_1128.gpkg",#Done (only 6 days of data in this file)
                "Conkerberry_FireGraze_20230904_1132.gpkg",#Done
                "Conkerberry_FireGraze_20230904_1141.gpkg",#Done
                "Conkerberry_FireGraze_20230904_1152.gpkg",#Done
                "Conkerberry_FireGraze_20230904_1153.gpkg",#Done
                "Conkerberry_FireGraze_20230904_1154.gpkg",#Done
                "Conkerberry_FireGraze_20230904_1157.gpkg",#Done
                "Conkerberry_FireGraze_20230904_1172.gpkg",#Done
                "Conkerberry_FireGraze_20230904_1195.gpkg",#Done
                "Conkerberry_FireGraze_20230904_1199.gpkg",#Done
                "Conkerberry_FireGraze_20230904_1206.gpkg",#Done
                "Conkerberry_FireGraze_20230904_1211.gpkg",#Done
                "Conkerberry_FireGraze_20230904_1213.gpkg"]#Done
                
output_folder = r'C:\Users\qw2\Desktop\FireGraze_GPS\GPS data\FireGraze dry season 2023 GPS data\Conkerberry\Collar_Daily_Tracks'

def parse_datetime(datetime_string):
    # String format like: 2023-05-10 05:56:30Z
    dtt = datetime.strptime(datetime_string, '%Y-%m-%d %H:%M:%SZ')
    return (dtt.date(), dtt.time())
    
def parse_date(date_string):
    # String format like: 2023/05/10
    dtd = datetime.strptime(date_string, '%Y/%m/%d')
    return dtd.date()
    
def parse_time(time_string):
    # String format like: 06:17:02
    t = datetime.strptime(time_string, '%H:%M:%S')
    return t

def transformed_geom(g):
    geom = QgsGeometry.fromWkt(g.asWkt())
    src_crs = QgsCoordinateReferenceSystem('epsg:4326')
    dest_crs = QgsCoordinateReferenceSystem('epsg:28352')
    xform = QgsCoordinateTransform(src_crs, dest_crs, project)
    geom.transform(xform)
    return geom
    
def calculate_distance_and_speed(ft1, ft2):
    '''
    Returns the distance and (approx) speed between 2 consecutive features
    '''
    geom1 = QgsGeometry.fromWkt(ft1.geometry().asWkt())
    geom2 = QgsGeometry.fromWkt(ft2.geometry().asWkt())
    geom1_utm = transformed_geom(geom1)
    geom2_utm = transformed_geom(geom2)
    dist = geom1_utm.distance(geom2_utm)# Meters
    if 'Date' in [fld.name() for fld in ft1.fields()]:
        ft1_date = parse_date(ft1['Date'])
        ft1_time = parse_time(ft1['Time'])
        ft1_dt = datetime.combine(ft1_date, ft1_time.time())# Errors on this line
        ft2_date = parse_date(ft2['Date'])
        ft2_time = parse_time(ft2['Time'])
        ft2_dt = datetime.combine(ft2_date, ft2_time.time())
    else:
        ft1_date = parse_datetime(ft1['Time'])[0]
        ft1_time = parse_datetime(ft1['Time'])[1]
        ft1_dt = datetime.combine(ft1_date, ft1_time)
        ft2_date = parse_datetime(ft2['Time'])[0]
        ft2_time = parse_datetime(ft2['Time'])[1]
        ft2_dt = datetime.combine(ft2_date, ft2_time)
    t_diff = ft2_dt-ft1_dt
    delta_secs = t_diff.seconds
    speed_meters_per_second = dist/delta_secs
    speed_kmh = speed_meters_per_second*3.6
    return delta_secs, dist, speed_kmh

file_name = source_files[23]# **********************************************************************Enter index of input file

paddock = file_name.split('_')[0]
collar_no = file_name.split('.')[0].split('_')[-1]
##########################################################################
temp_lyr = QgsVectorLayer('LineString?crs=epsg:28352', f'Daily_Tracks_{paddock}_{collar_no}', 'memory')
flds_to_add = [QgsField('Paddock', QVariant.String),# Paddock
                QgsField('Collar_No', QVariant.String),# Collar
                QgsField('Date', QVariant.String),# Date
                QgsField('Total_Distance_km', QVariant.Double, len=6, prec=3),# Total distance walked
                QgsField('Max_T_Delta_mins', QVariant.Double, len=4, prec=1),
                QgsField('Min_Dist_m', QVariant.Double, len=6, prec=3),
                QgsField('Max_Dist_m', QVariant.Double, len=6, prec=3),
                QgsField('Mean_Dist_m', QVariant.Double, len=6, prec=3),
                QgsField('Min_Speed_kph', QVariant.Double, len=5, prec=2),
                QgsField('Max_Speed_kph', QVariant.Double, len=5, prec=2),
                QgsField('Mean_Speed_kph', QVariant.Double, len=5, prec=2)]
temp_lyr.dataProvider().addAttributes(flds_to_add)
temp_lyr.updateFields()
##########################################################################
uri = os.path.join(source_folder, file_name)
lyr = QgsVectorLayer(uri, file_name, 'ogr')
fld_names = [fld.name() for fld in lyr.fields()]
if 'Date' in fld_names:
    date_fld = 'Date'
elif 'Time' in fld_names:
    date_fld = 'Time'

all_track_features = []
all_dates = list(set([parse_date(ft[date_fld]) if date_fld == 'Date' else parse_datetime(ft[date_fld])[0] for ft in lyr.getFeatures()]))

counter = 0

for date in sorted(all_dates):
#    print(date)
#    if counter == 10:
#        break
    date_feats = []
    for ft in lyr.getFeatures():
        if date_fld == 'Date':
            ft_date = parse_date(ft[date_fld])
        elif date_fld == 'Time':
            ft_date = parse_datetime(ft[date_fld])[0]# parse_datetime returns a tuple; date is 0th item
        if ft_date == date:
            date_feats.append(ft)
    if len(date_feats)<2:
        # There is only one feature for this date (calculating time gaps etc won't work)
        continue
    # Sort the features for each day period by time to ensure tracklines are constructed in the correct order
    # Otherwise distance will not be correct. This should be a redundant safeguard since fid order should also match
    # chronological order.
    if date_fld == 'Date':
        date_feats_chronological = sorted(date_feats, key=lambda ft: parse_time(ft['Time']))
    elif date_fld == 'Time':
        date_feats_chronological = sorted(date_feats, key=lambda ft: parse_datetime(ft['Time'])[1])
    #print(date_feats_chronological)
    
    date_points = [ft.geometry().asMultiPoint()[0] for ft in date_feats_chronological]# Geom is MultiPointXY; PointXY is 0th element
    line_geom = QgsGeometry.fromPolylineXY(date_points)
    transformed_line_geom = transformed_geom(line_geom)
    total_distance = round(transformed_line_geom.length()/1000, 3)
    #print(f'{collar_no}---{date}---{total_distance/1000}km')
    ########################################################################
    # Calculate distance and speed between gps pings for each day
    day_time_gaps = []
    day_distances = []
    day_speeds = []
    ids = [f.id() for f in date_feats_chronological]
    last_id = ids[-1]
    for i, feat in enumerate(date_feats_chronological):
        if feat.id() == last_id:
            break
        gap, dist, speed = calculate_distance_and_speed(feat, date_feats_chronological[i+1])
        day_time_gaps.append(gap)
        day_distances.append(dist)
        day_speeds.append(speed)
    max_time_gap = round(max(day_time_gaps)/60, 1)# Divide by 60 to convert from seconds to minutes
    min_dist = round(min(day_distances), 2)
    max_dist = round(max(day_distances), 2)
    mean_dist = round(statistics.mean(day_distances), 2)
    min_speed = round(min(day_speeds), 2)
    max_speed = round(max(day_speeds), 2)
    mean_speed = round(statistics.mean(day_speeds), 2)
    ########################################################################
    line_feat = QgsFeature(temp_lyr.fields())
    line_feat.setGeometry(transformed_line_geom)
    line_feat.setAttributes([paddock,
                            collar_no,
                            date.strftime('%Y-%m-%d'),
                            str(total_distance),
                            max_time_gap,
                            min_dist,
                            max_dist,
                            mean_dist,
                            min_speed,
                            max_speed,
                            mean_speed])
    all_track_features.append(line_feat)
    
    counter+=1
    
temp_lyr.dataProvider().addFeatures(all_track_features)
temp_lyr.updateExtents()
#project.addMapLayer(temp_lyr)

# Release input file
lyr = None

# Save output temporary layer to gpkg and xlsx spreadsheet
save_2_gpkg_params = {'INPUT':temp_lyr,
                        'OUTPUT':os.path.join(output_folder, f'{temp_lyr.name()}.gpkg'),
                        'LAYER_NAME':'',
                        'DATASOURCE_OPTIONS':'',
                        'LAYER_OPTIONS':''}

processing.run("native:savefeatures", save_2_gpkg_params)

save_2_xlsx_params = {'LAYERS':[temp_lyr],
                        'USE_ALIAS':False,
                        'FORMATTED_VALUES':False,
                        'OUTPUT':os.path.join(output_folder, f'{temp_lyr.name()}.xlsx'),
                        'OVERWRITE':False}

processing.run("native:exporttospreadsheet", save_2_xlsx_params)

print(f'{collar_no} completed in {datetime.now()-start_time} secs')
print('Done')