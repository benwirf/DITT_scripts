import csv

result_csv = r'C:\Users\qw2\Desktop\Southern_NT_Fires_2023\Results_July_1-EOY\Percent_of_southern_estate_burnt_by_district.csv'

csv_tbl = open(result_csv, mode='w', newline='')

writer = csv.writer(csv_tbl)

writer.writerow(['DISTRICT', 'TOTAL ESTATE AREA KM2', 'TOTAL ESTATE BURNT KM2', '% OF ESTATE BURNT'])

project = QgsProject.instance()

property_lyr = project.mapLayersByName('Pastoral_Property_Boundaries')[0]

firescar_lyr = project.mapLayersByName('fs_dissolved')[0]

firescar_geom = firescar_lyr.getFeature(1).geometry()
'''
district_names = ['Darwin', 'Katherine', 'Roper', 'Victoria River', 'Gulf', 'Sturt Plateau',
                    'Barkly', 'Tennant Creek', 'Northern Alice Springs', 'Plenty', 'Southern Alice Springs']
'''
district_names = ['Tennant Creek', 'Northern Alice Springs', 'Plenty', 'Southern Alice Springs']

for district in district_names:
    district_properties = [p for p in property_lyr.getFeatures() if p['DISTRICT'] == district]
    properties_geom = QgsGeometry.unaryUnion([p.geometry() for p in district_properties])
    total_area = properties_geom.area()
    total_area_km2 = round(total_area/1000000, 3)
    fire_ix = properties_geom.intersection(firescar_geom).area()
    fire_ix_km2 = round(fire_ix/1000000, 3)
    pcnt_of_district_pastoral_estate_burnt = round((fire_ix/total_area)*100, 1)
#    print([district, total_area_km2, fire_ix_km2, pcnt_of_district_pastoral_estate_burnt])
    writer.writerow([district, total_area_km2, fire_ix_km2, pcnt_of_district_pastoral_estate_burnt])
    
csv_tbl.close()
del writer
print('Done')
