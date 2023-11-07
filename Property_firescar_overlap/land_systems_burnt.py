import csv

result_csv = r'C:\Users\qw2\Desktop\Pastoral_Properties_Burnt\Land_Systems_Burnt\land_systems_burnt.csv'

csv_tbl = open(result_csv, mode='w', newline='')

writer = csv.writer(csv_tbl)

writer.writerow(['DISTRICT', 'LANDSYSTEM', 'TOTAL LAND SYSTEM KM2', 'AREA BURNT KM2', 'PERCENT BURNT'])

project = QgsProject.instance()

district_prop_lyr = project.mapLayersByName('district_props_dissolved')[0]

district_ls_lyr = project.mapLayersByName('district_prop_land_systems')[0]

firescar_lyr = project.mapLayersByName('firescars_dissolved')[0]

firescar_geom = [ft.geometry() for ft in firescar_lyr.getFeatures()][0]
#print(firescar_geom.area())

for ft in district_prop_lyr.getFeatures():
    district = ft['DISTRICT']
#    print(district)
    district_land_system_names = set([ls['LANDSYSTEM'] for ls in district_ls_lyr.getFeatures() if ls.geometry().intersects(ft.geometry())])
#    print(district_land_systems)
    for ls_name in district_land_system_names:
        ls_feat_geoms = [ls.geometry() for ls in district_ls_lyr.getFeatures() if ls.geometry().intersects(ft.geometry()) and ls['LANDSYSTEM'] == ls_name]
        ls_geom = QgsGeometry.collectGeometry(ls_feat_geoms)
        total_ls_area = ls_geom.area()
        ls_burnt = ls_geom.intersection(firescar_geom).area()
        pcnt_ls_burnt = (ls_burnt/total_ls_area)*100
#        print(district, ls_name, pcnt_ls_burnt)
        writer.writerow([district,
                        ls_name,
                        str(round(total_ls_area/1000000, 5)),
                        str(round(ls_burnt/1000000, 5)),
                        str(round(pcnt_ls_burnt, 3))])

csv_tbl.close()
del writer
print('Done')