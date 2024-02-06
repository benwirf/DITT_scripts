'''
Iterate over CSV files of raw GPS collar data in a source folder.
Discard any rows with 0 in the Latitude or Longitude columns, and
add the valid rows as features to a temporary layer and save as gpkg.
'''
import os
import csv

FIELD_TYPES = {'Index': QgsField('Index', QVariant.Int),
                'Date': QgsField('Date', QVariant.String),
                'Time': QgsField('Time', QVariant.String),
                'Latitude': QgsField('Latitude', QVariant.Double, len=8, prec=6),
                'Longitude': QgsField('Longitude', QVariant.Double, len=9, prec=6),
                'Altitude': QgsField('Altitude', QVariant.Double, len=5, prec=2),
                'Speed': QgsField('Speed', QVariant.Double, len=6, prec=2),
                'Course': QgsField('Course', QVariant.Double, len=5, prec=2),
                'Distance': QgsField('Distance', QVariant.Double, len=6, prec=3),
                'Type': QgsField('Type', QVariant.String),
                'Timeout': QgsField('Timeout', QVariant.Int),
                'MSVs_QCN': QgsField('MSVs_QCN', QVariant.String),
                'Weight Criteria': QgsField('Weight Criteria', QVariant.String),
                'SleepTime': QgsField('SleepTime', QVariant.Int),
                'EHPE': QgsField('EHPE', QVariant.Double, len=5, prec=1),
                'Satelite ID': QgsField('Satelite ID', QVariant.Int),
                'Satelite': QgsField('Satelite', QVariant.String),
                'Satellites': QgsField('Satellites', QVariant.Int),
                'QCN': QgsField('QCN', QVariant.Int)}

def convert_att(header, val):
    if header == 'Index':
        return int(val.lstrip())# Index
    elif header == 'Date':
        return val.lstrip()# Date
    elif header == 'Time':
        if val[0] == '=':
            return val.lstrip()[2:][:-1]
        return val.lstrip()# Time
    elif header == 'Latitude':
        return round(float(val.lstrip()), 6)# Lat
    elif header == 'Longitude':
        return round(float(val.lstrip()), 6)# Long
    elif header == 'Altitude':
        return round(float(val.lstrip()), 2)# Alt
    elif header == 'Speed':
        return round(float(val.lstrip()), 2)# Speed
    elif header == 'Course':
        return round(float(val.lstrip()), 2)# Course
    elif header == 'Distance':
        return round(float(val.lstrip()), 3)# Distance
    elif header == 'Type':
        return val.lstrip()# Type
    elif header == 'Timeout':
        return int(val.lstrip())# Timeout
    elif header == 'MSVs_QCN':
        return val.lstrip()# MSVs_QCN
    elif header == 'Weight Criteria':
        return val.lstrip()# Weight Criteria
    elif header == 'SleepTime':
        return int(val.lstrip())# SleepTime
    elif header == 'EHPE':
        return round(float(val.lstrip()), 1)# EHPE
    elif header == 'Satelite ID':
        return int(val.lstrip())# Satelite ID
    elif header == 'Satelite':
        return val.lstrip()# Satelite
    elif header == 'Satellites':
        return int(val.lstrip())# Satellites
    elif header == 'QCN':
        return int(val.lstrip())# QCN

source_folder = r'C:\Users\qw2\Desktop\FireGraze_GPS\GPS data\FireGraze dry season 2023 GPS data\Box'

output_folder = r'C:\Users\qw2\Desktop\FireGraze_GPS\GPS data\FireGraze dry season 2023 GPS data\Box\Raw_Geopackages'

count = 0

for file in os.scandir(source_folder):
    if not 'csv' in file.name:
        continue
    temp_layer = QgsVectorLayer('Point?crs=epsg:4326', file.name.split('.')[0], 'memory')
    
    all_feats = []
    
#    if count == 3:
#        break
    #print(file.name)
    file_name = file.name
    csv_path = os.path.join(source_folder, file_name)
    csv_file = open(csv_path)
    csv_reader = csv.reader(x.replace('\0', '') for x in csv_file)
    row_count = 0
    for row in csv_reader:
        if not row:
            row_count+=1
            continue
        if row_count == 0:
            col_headers = [h.lstrip() for h in row]
            flds_to_add = [FIELD_TYPES[col_name.lstrip()] for col_name in row]
            temp_layer.dataProvider().addAttributes(flds_to_add)
            temp_layer.updateFields()
            row_count+=1
            continue
        #print(row)
        # Occasionally a csv may have duplicate rows (entire data set is repeated)
        # So let's check if the row is the same as the header row and break out of the loop
        if [h.lstrip() for h in row] == col_headers:
            break
        lat_idx = col_headers.index('Latitude')
        lon_idx = col_headers.index('Longitude')
        if float(row[lat_idx].lstrip()) == 0.0 or float(row[lon_idx].lstrip()) == 0.0:
            row_count+=1
            continue
        feat = QgsFeature(temp_layer.fields())
        geom = QgsGeometry.fromPointXY(QgsPointXY(float(row[lon_idx]), float(row[lat_idx])))
        feat.setGeometry(geom)
        feat.setAttributes([convert_att(hdr, row[col_headers.index(hdr)]) for hdr in col_headers])
        #print(feat.attributes())
        all_feats.append(feat)
        row_count+=1
    
    csv_file.close()
    del csv_reader
    
    temp_layer.dataProvider().addFeatures(all_feats)
    temp_layer.updateExtents()
    #QgsProject.instance().addMapLayer(temp_layer)
    count+=1
    
    save_path = os.path.join(output_folder, f'{temp_layer.name()}.gpkg')
    
    save_params = {'INPUT':temp_layer,
                    'OUTPUT':save_path,
                    'LAYER_NAME':'',
                    'DATASOURCE_OPTIONS':'',
                    'LAYER_OPTIONS':''}
    
    processing.run("native:savefeatures", save_params)

print('Done')