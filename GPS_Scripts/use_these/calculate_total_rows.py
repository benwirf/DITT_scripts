import os
import csv

dir_path = r'R:\LID\Common-AZRI\PROJECTS\04 GRAZING SYSTEMS\04-01 Quality Graze\04-01-07 Rain Ready Rangelands\05. Mt Denison\Data\GPS Data\Mt Denison Download 20230907'

row_count = 0

file_count = 0

for folder in os.scandir(dir_path):
    if file_count == 100:
        break
    folder_path = os.path.join(dir_path, folder.name)
#    print(folder_path)
    for file in os.scandir(folder_path):
#        print(file.name)
        file_path = os.path.join(folder_path, file.name)
        csv_file = open(file_path)
        csv_reader = csv.reader(csv_file)
        row_count+=len([row for row in csv_reader])
    file_count+=1

csv_file.close()
del(csv_reader)
print('Done...')
print(file_count)
print(row_count)
