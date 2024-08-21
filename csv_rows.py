import csv

file_path = r'C:\Users\qw2\Desktop\DITT_2\Huckitta_RMC\Huckitta_Color_Map.csv'

csv_file = open(file_path)

csv_reader = csv.reader(csv_file, delimiter=',')

all_rows = [row for row in csv_reader]

print(all_rows)

trc = 5 if len(all_rows)>5 else len(all_rows)

print(trc)