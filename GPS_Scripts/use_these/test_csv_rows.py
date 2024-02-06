import os
import csv

source_folder = r'C:\Users\qw2\Desktop\FireGraze_GPS\GPS data\FireGraze dry season 2023 GPS data\Box'

output_folder = r'C:\Users\qw2\Desktop\FireGraze_GPS\GPS data\FireGraze dry season 2023 GPS data\Box'

count = 0

for file in os.scandir(source_folder):
    if count == 1:
        break
    #print(file.name)
    file_name = file.name
    csv_path = os.path.join(source_folder, file_name)
    csv_file = open(csv_path)
    csv_reader = csv.reader(x.replace('\0', '') for x in csv_file)
    row_count = 0
    for row in csv_reader:
        if row_count == 10:
            break
        if row_count == 0:
            print(row)
            row_count+=1
            continue
        print(str(row[0]))
        #print(len(row))
        #print(float(row[3].lstrip()))
        #TODO: discard rows with 0 lat/long, create a feature, set geometry from
        #Lat & Long columns, set attributes etc
        row_count+=1
    
    count+=1
    
    # Outside inner loop, save the temporary layer as a geopackage

print('Done')