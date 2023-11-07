import csv

result_csv = r'C:\Users\qw2\Desktop\Pastoral_Properties_Burnt\Mt_Denison\mtd_5km_watered_land_systems_burnt.csv'

csv_tbl = open(result_csv, mode='w', newline='')

writer = csv.writer(csv_tbl)

writer.writerow(['LANDSYSTEM', 'TOTAL LAND SYSTEM KM2', 'AREA BURNT KM2', 'PERCENT BURNT'])

project = QgsProject.instance()

boundary_lyr = project.mapLayersByName('mtd_bdry')[0]

boundary_geom = [ft.geometry() for ft in boundary_lyr.getFeatures()][0]

ls_lyr = project.mapLayersByName('mtd_5km_watered_land_systems')[0]

firescar_lyr = project.mapLayersByName('firescars_oct_31_dissolved')[0]

firescar_geom = [ft.geometry() for ft in firescar_lyr.getFeatures()][0]
#print(firescar_geom.area())

land_system_names = set([ls['LandSystem'] for ls in ls_lyr.getFeatures() if ls.geometry().intersects(boundary_geom)])
#    print(district_land_systems)
for ls_name in land_system_names:
    ls_feat_geoms = [ls.geometry() for ls in ls_lyr.getFeatures() if ls.geometry().intersects(boundary_geom) and ls['LandSystem'] == ls_name]
    ls_geom = QgsGeometry.collectGeometry(ls_feat_geoms)
    total_ls_area = ls_geom.area()
    ls_burnt = ls_geom.intersection(firescar_geom).area()
    pcnt_ls_burnt = (ls_burnt/total_ls_area)*100
#        print(district, ls_name, pcnt_ls_burnt)
    writer.writerow([ls_name,
                    str(round(total_ls_area/1000000, 5)),
                    str(round(ls_burnt/1000000, 5)),
                    str(round(pcnt_ls_burnt, 3))])

csv_tbl.close()
del writer
print('Done')