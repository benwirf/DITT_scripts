import csv

file_path = r'Path\to\Huckitta_RMC\Huckitta_Color_Map.csv'

csv_file = open(file_path)

csv_reader = csv.reader(csv_file, delimiter=',')

csv_items = {}

for row in csv_reader:
    csv_items[row[0]] = row[1]

print(csv_items)

csv_file.close()
