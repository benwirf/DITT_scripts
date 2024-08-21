import csv

file_path = r'C:\Users\qw2\Desktop\DITT_2\Huckitta_RMC\Huckitta_Color_Map.csv'

csv_file = open(file_path)

csv_reader = csv.reader(csv_file, delimiter=',')

csv_items = {}

for row in csv_reader:
    csv_items[row[0]] = row[1]

csv_file.close()

default_style = QgsStyle().defaultStyle()

layer = QgsProject().instance().mapLayersByName('Huckitta_Land_Systems_250')[0]
field_index = layer.fields().lookupField('LandSystem')
unique_values = list(layer.uniqueValues(field_index))
categories = []
for value in sorted(unique_values):
    symbol = QgsSymbol.defaultSymbol(layer.geometryType())
    col_hex = csv_items[value]
    qcol = QColor(col_hex)
    symbol.setColor(qcol)
    category = QgsRendererCategory(value, symbol, str(value))
    categories.append(category)

#print(categories)
renderer = QgsCategorizedSymbolRenderer('LandSystem', categories) 
layer.setRenderer(renderer)
layer.triggerRepaint()
