import csv

result_csv = r'C:\Users\qw2\Desktop\Pastoral_Properties_Burnt\Land_Systems_Burnt\Watered_Land_Systems_Burnt\watered_land_systems_burnt.csv'

csv_tbl = open(result_csv, mode='w', newline='')

writer = csv.writer(csv_tbl)

writer.writerow(['DISTRICT', 'LANDSYSTEM', 'TOTAL WATERED (5km) LAND SYSTEM KM2', 'WATERED LS AREA BURNT KM2', 'WATERED LS % BURNT'])

project = QgsProject.instance()

district_lyr = project.mapLayersByName('PASTORAL_DISTRICTS')[0]

bores_lyr = project.mapLayersByName('infra_points_bores')[0]

bore_sp_idx = QgsSpatialIndex(bores_lyr.getFeatures())

# Located in folder: 'C:\Users\qw2\Desktop\Pastoral_Properties_Burnt\Land_Systems_Burnt\All_Properties'
ls_lyr = project.mapLayersByName('property_land_systems')[0]

# This is output from pastoral properties burnt script
# (latest NAFI firescars (geoms repaired) clipped to pastoral properties, filtered Aug-current month and dissolved)
firescar_lyr = project.mapLayersByName('fs_dissolved')[0]

firescar_geom = [ft.geometry() for ft in firescar_lyr.getFeatures()][0]
#print(firescar_geom.area())

for ft in district_lyr.getFeatures():
    district = ft['DISTRICT']
#    print(district)
    # bores within distict bbox
    district_bore_candidate_ids = bore_sp_idx.intersects(ft.geometry().boundingBox())
    # bores within district boundary
    district_bore_geoms = [bore_ft.geometry() for bore_ft in bores_lyr.getFeatures(district_bore_candidate_ids) if bore_ft.geometry().intersects(ft.geometry())]
    # All bores buffered by 5km
    district_bores_buffered = [g.buffer(5000, 25) for g in district_bore_geoms]
    # All bore buffers dissolved
    district_bore_buffers_dissolved = QgsGeometry.unaryUnion(district_bores_buffered)
    # Dissolved buffer 'clipped' to district boundary
    district_watered_area_geom = district_bore_buffers_dissolved.intersection(ft.geometry())
        
    district_watered_land_system_names = set([ls['LANDSYSTEM'] for ls in ls_lyr.getFeatures() if ls.geometry().intersects(district_watered_area_geom)])
#    print(district_land_systems)
    for watered_ls_name in district_watered_land_system_names:
        watered_ls_feat_geoms = [ls.geometry().intersection(district_watered_area_geom) for ls in ls_lyr.getFeatures() if ls['LANDSYSTEM'] == watered_ls_name]
        watered_ls_geom = QgsGeometry.collectGeometry(watered_ls_feat_geoms)
#        watered_ls_geom = ls_geom.intersection(district_watered_area_geom)
        total_watered_ls_area = watered_ls_geom.area()
        watered_ls_burnt = watered_ls_geom.intersection(firescar_geom)
        watered_ls_burnt_area = watered_ls_burnt.area()
        pcnt_watered_ls_burnt = (watered_ls_burnt_area/total_watered_ls_area)*100
#        print(district, ls_name, pcnt_ls_burnt)
        writer.writerow([district,
                        watered_ls_name,
                        str(round(total_watered_ls_area/1000000, 5)),
                        str(round(watered_ls_burnt_area/1000000, 5)),
                        str(round(pcnt_watered_ls_burnt, 3))])

csv_tbl.close()
del writer
print('Done')