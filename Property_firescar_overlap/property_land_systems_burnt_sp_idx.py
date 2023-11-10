'''Using QgsSpatialIndex'''

import csv

result_csv = r'C:\Users\qw2\Desktop\Pastoral_Properties_Burnt\Land_Systems_Burnt\All_Properties\property_land_systems_burnt.csv'

csv_tbl = open(result_csv, mode='w', newline='')

writer = csv.writer(csv_tbl)

writer.writerow(['DISTRICT', 'PROPERTY', 'LANDSYSTEM', 'CLASS', 'TOTAL LAND SYSTEM KM2', 'AREA BURNT KM2', 'PERCENT BURNT'])

project = QgsProject.instance()

pastoral_prop_lyr = project.mapLayersByName('Pastoral_Property_Boundaries')[0]

property_ls_lyr = project.mapLayersByName('property_land_systems')[0]

firescar_lyr = project.mapLayersByName('fs_dissolved')[0]

firescar_geom = [ft.geometry() for ft in firescar_lyr.getFeatures()][0]
#print(firescar_geom.area())

ls_sp_idx = QgsSpatialIndex(property_ls_lyr.getFeatures())

for ft in pastoral_prop_lyr.getFeatures():
    district = ft['DISTRICT']
    property_name = ft['NAME']
#    print(district)
    prop_ls_candidate_ids = ls_sp_idx.intersects(ft.geometry().boundingBox())
    prop_ls_feats = [feat for feat in property_ls_lyr.getFeatures(prop_ls_candidate_ids) if feat.geometry().intersects(ft.geometry())]
    property_land_system_names = set([ls['LANDSYSTEM'] for ls in prop_ls_feats])
#    print(district_land_systems)
    for ls_name in property_land_system_names:
        ls_class = 'unknown'
        for i in prop_ls_feats:
            if i['LANDSYSTEM'] == ls_name:
                ls_class = i['CLASS']
        ls_feat_geoms = [ls.geometry().intersection(ft.geometry()) for ls in prop_ls_feats if ls['LANDSYSTEM'] == ls_name]
        ls_geom = QgsGeometry.collectGeometry(ls_feat_geoms)
        total_ls_area = ls_geom.area()
        ls_burnt = ls_geom.intersection(firescar_geom).area()
        pcnt_ls_burnt = (ls_burnt/total_ls_area)*100
#        print(district, ls_name, pcnt_ls_burnt)
        writer.writerow([district,
                        property_name,
                        ls_name,
                        ls_class,
                        str(round(total_ls_area/1000000, 5)),
                        str(round(ls_burnt/1000000, 5)),
                        str(round(pcnt_ls_burnt, 3))])

csv_tbl.close()
del writer
print('Done')