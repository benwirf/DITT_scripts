import csv
import calendar

months_csv = 'C:\\Users\\qw2\\Desktop\\Sweet_Spot\\OMP\\OMP_all_fires\\5kmWA_fire_summary.csv'

years_csv = 'C:\\Users\\qw2\\Desktop\\Sweet_Spot\\OMP\\OMP_all_fires\\5kmWA_year_summary.csv'

tbl_months = open(months_csv, mode='w', newline='')

tbl_years = open(years_csv, mode='w', newline='')

writer_1 = csv.writer(tbl_months)

writer_2 = csv.writer(tbl_years)

writer_1.writerow(['Paddock Name', 'Fire Year', 'Fire Month', 'Total 5kmWA km2', 'Area burnt km2', 'Percent of 5kmWA burnt km2'])

writer_2.writerow(['Paddock Name', 'Fire Year', 'Total 5kmWA km2', 'Area burnt km2', 'Percent of 5kmWA burnt km2'])

month_names = [calendar.month_name[i] for i in range(1, 13)]

paddock_lyr = QgsProject.instance().mapLayersByName('OMP_5km_WA_main_paddocks')[0]
firescar_lyr = QgsProject.instance().mapLayersByName('fires_5kmWA_2000-Aug_22')[0]

xform = QgsCoordinateTransform(firescar_lyr.crs(), paddock_lyr.crs(), QgsProject.instance())

def transform_geom(g):
    g.transform(xform)
    return g

for ft in paddock_lyr.getFeatures():
    total_5km_watered_area = round(ft.geometry().area()/1000000, 5)
    fire_fts = [f for f in firescar_lyr.getFeatures() if transform_geom(f.geometry()).intersects(ft.geometry())]
    fire_years = set([f['year'] for f in fire_fts])
#    print(fire_years)
    for year in fire_years:
        all_burns_by_year = []
        months = set([f['month'] for f in fire_fts if f['year'] == year])
#        print(months)
        for m in months:
            burn_area = round(sum([transform_geom(f.geometry()).intersection(ft.geometry()).area() for f in fire_fts if f['month'] == m and f['year'] == year])/1000000, 5)
            all_burns_by_year.append(burn_area)
            pcnt_burnt = round(burn_area/total_5km_watered_area*100, 5)
            print(ft['padd_name'], year, month_names[m-1], f'{total_5km_watered_area} km2', f'{burn_area} km2', f'{pcnt_burnt}%')
            writer_1.writerow([ft['padd_name'], year, month_names[m-1], f'{total_5km_watered_area}', f'{burn_area}', f'{pcnt_burnt}'])
        total_by_year = sum(all_burns_by_year)
        pcnt_by_year = round(total_by_year/total_5km_watered_area*100, 5)
        writer_2.writerow([ft['padd_name'], year, f'{total_5km_watered_area}', f'{total_by_year}', f'{pcnt_by_year}'])
    print('--------------------------------------')
tbl_months.close()
tbl_years.close()