import csv

result_csv = r'C:\Users\qw2\Desktop\DITT_2\Huckitta_RMC\Huckitta_Color_Map.csv'

csv_tbl = open(result_csv, mode='w', newline='')

writer = csv.writer(csv_tbl)

writer.writerow(['LandSystem', 'Color'])

layer = QgsProject().instance().mapLayersByName('Huckitta_Land_Systems_250')[0]
r = layer.renderer()
for cat in r.categories():
    ls = cat.label()
    col = cat.symbol().color()
    hex_code = col.name()
    writer.writerow([ls, hex_code])


csv_tbl.close()
csv_tbl.close()
print('Done')