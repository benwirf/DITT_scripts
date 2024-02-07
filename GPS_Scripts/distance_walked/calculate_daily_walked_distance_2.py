from datetime import datetime
import os

project = QgsProject.instance()

source_folder = r'C:\Users\qw2\Desktop\FireGraze_GPS\GPS data\FireGraze dry season 2023 GPS data\Conkerberry\Clipped_GeoPackages'

def parse_time(time_string):
    # String format like: 2023-05-10 05:56:30Z
    dtt = datetime.strptime(time_string, '%Y-%m-%d %H:%M:%SZ')
    return dtt.date()
    
def parse_date(date_string):
    # String format like: 2023/05/10
    dtd = datetime.strptime(date_string, '%Y/%m/%d')
    return dtd.date()

def transformed_geom(g):
    geom = QgsGeometry.fromWkt(g.asWkt())
    src_crs = QgsCoordinateReferenceSystem('epsg:4326')
    dest_crs = QgsCoordinateReferenceSystem('epsg:28352')
    xform = QgsCoordinateTransform(src_crs, dest_crs, project)
    geom.transform(xform)
    return geom

file_count = 0

for file in os.scandir(source_folder):
    if file_count == 1:
        break
    #print(file.name)
    ##########################################################################
    temp_lyr = QgsVectorLayer('LineString?crs=epsg:28352', 'Daily_Tracks', 'memory')
    flds_to_add = [QgsField('Paddock', QVariant.String),# Paddock
                    QgsField('Collar No', QVariant.String),# Collar
                    QgsField('Date', QVariant.String),# Date
                    QgsField('Distance', QVariant.Double, len=6, prec=3)]# Distance walked]
    temp_lyr.dataProvider().addAttributes(flds_to_add)
    temp_lyr.updateFields()
    ##########################################################################
    paddock = file.name.split('_')[0]
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
    
    all_track_features = []
    all_dates = list(set([parse_date(ft[date_fld]) if date_fld == 'Date' else parse_time(ft[date_fld]) for ft in lyr.getFeatures()]))
    for date in sorted(all_dates):
        date_points = []
        for ft in lyr.getFeatures():
            if date_fld == 'Date':
                ft_date = parse_date(ft[date_fld])
            elif date_fld == 'Time':
                ft_date = parse_time(ft[date_fld])
            if ft_date == date:
                date_points.append(ft.geometry().asMultiPoint()[0])
        line_geom = QgsGeometry.fromPolylineXY(date_points)
        transformed_line_geom = transformed_geom(line_geom)
        total_distance = round(transformed_line_geom.length()/1000, 3)
        #print(f'{collar_no}---{date}---{total_distance/1000}km')
        line_feat = QgsFeature(temp_lyr.fields())
        line_feat.setGeometry(transformed_line_geom)
        line_feat.setAttributes([paddock, collar_no, date.strftime('%Y-%m-%d'), str(total_distance)])
        all_track_features.append(line_feat)
        
    temp_lyr.dataProvider().addFeatures(all_track_features)
    temp_lyr.updateExtents()
    project.addMapLayer(temp_lyr)

    file_count += 1