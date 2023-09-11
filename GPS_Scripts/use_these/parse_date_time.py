from datetime import datetime
import os
import csv

dir_path = r'R:\LID\Common-AZRI\PROJECTS\04 GRAZING SYSTEMS\04-01 Quality Graze\04-01-07 Rain Ready Rangelands\05. Mt Denison\Data\GPS Data\Mt Denison Download 20230907'

file_count = 0

for folder in os.scandir(dir_path):
    if file_count == 1:
        break
    folder_path = os.path.join(dir_path, folder.name)
#    print(folder_path)
    for file in os.scandir(folder_path):
#        print(file.name)
        row_count = 0
        file_path = os.path.join(folder_path, file.name)
        csv_file = open(file_path)
        csv_reader = csv.reader(csv_file)
        csv_rows = [row for row in csv_reader][1:]
        for row in csv_rows:
            print(len(row))
            if row_count == 5:
                break
            raw_dt = row[0][2:-2]
            if raw_dt:
                dt = datetime.strptime(str(raw_dt), '%Y-%m-%d %H:%M:%S')
                print(QDateTime(dt))
            row_count+=1
    file_count+=1

csv_file.close()
del(csv_reader)