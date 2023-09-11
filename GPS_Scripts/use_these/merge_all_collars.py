from datetime import datetime
import os
import csv

all_collars = QgsVectorLayer('Point?crs=epsg:4326', 'All_collars_merged', 'memory')

flds = [QgsField('Collar_ID', QVariant.String),
        QgsField('Date_Time', QVariant.DateTime),
        QgsField('Latitude', QVariant.Double, len=10, prec=6),
        QgsField('Longitude', QVariant.Double, len=10, prec=6),
        QgsField('Altitude', QVariant.Double, len=10, prec=3),
        QgsField('Speed', QVariant.Double, len=10, prec=2),
        QgsField('Course', QVariant.Int),
        QgsField('Distance', QVariant.Double, len=10, prec=2),
        QgsField('Detected Satellites', QVariant.Int),
        QgsField('Satellites(CN>22)', QVariant.Int),
        QgsField('EHPE', QVariant.Double, len=10, prec=2)]

all_collars.dataProvider().addAttributes(flds)

all_collars.updateFields()

dir_path = r'C:\Users\qw2\Desktop\Lakota_GPS\MT_DENISON\Mt Denison Download 20230907'

file_count = 0

all_feats = []

for folder in os.scandir(dir_path):
#    if file_count == 1:
#        break
    folder_path = os.path.join(dir_path, folder.name)
    for file in os.scandir(folder_path):
        collar_id = file.name.split('_')[1].split('.')[0]
        row_count = 0
        file_path = os.path.join(folder_path, file.name)
        csv_file = open(file_path)
        csv_reader = csv.reader(csv_file)
        csv_rows = [row for row in csv_reader][1:]
        for row in csv_rows:
            feat = QgsFeature(all_collars.fields())
            geom = QgsGeometry().fromPointXY(QgsPointXY(float(row[2]), float(row[1])))
            feat.setGeometry(geom)
            atts = [row[i+1] for i in range(len(row)-1)]
            atts.insert(0, collar_id)
#            if row_count == 100:
#                break
#            print(row)
            raw_dt = row[0][2:-2]
            if raw_dt:
                dt = datetime.strptime(str(raw_dt), '%Y-%m-%d %H:%M:%S')
                atts.insert(1, QDateTime(dt))
            feat.setAttributes(atts)
            all_feats.append(feat)
            row_count+=1
    file_count+=1

csv_file.close()
del(csv_reader)

all_collars.dataProvider().addFeatures(all_feats)
QgsProject.instance().addMapLayer(all_collars)