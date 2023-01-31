import csv

lu_csv = 'R:\\LID-BigData\\SPATIAL DATA\\PROJECTS\\Kidman Springs\\Carrying Capacity\\Caz\\Kidman_LU_per_paddock.csv'

tbl_lu = open(lu_csv, mode='w', newline='')

writer = csv.writer(tbl_lu)

writer.writerow(['PADDOCK', 'LAND UNIT', 'AREA HA'])

project = QgsProject.instance()

pdk_lyr = project.mapLayersByName('Kidman_Paddocks')[0]

lu_lyr = project.mapLayersByName('Kidman_30k_land_units')[0]

lu_idx = QgsSpatialIndex(lu_lyr.getFeatures())

for p in pdk_lyr.getFeatures():
    if p['Name'] != NULL:
        writer.writerow([p['Name'], '', str(round(p.geometry().area()/10000, 3))])
        candidates = lu_idx.intersects(p.geometry().boundingBox())
        intersecting_land_units = [f for f in lu_lyr.getFeatures(candidates) if f.geometry().intersects(p.geometry())]
    #    print(intersecting_land_units)
        for f in intersecting_land_units:
            lu_area = round(f.geometry().intersection(p.geometry()).area()/10000, 3)
            writer.writerow(['', f['LAND_UNIT'], str(lu_area)])
        print(f"{p['Name']} done")

print('All done')
tbl_lu.close()