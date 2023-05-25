from osgeo import gdal

#lyr = QgsProject.instance().mapLayersByName('No_1_PDK')[0]

temp_layers = []

def calculate_areas_in_distance_to_water_bands(water_proximity_layer):
    options = QgsVectorLayer.LayerOptions()
    options.loadDefaultStyle=False
    report_lyr = QgsVectorLayer('Point', f'{layer.name()} distance to water bands', 'memory', options)
    flds = QgsFields()
    flds_to_add = [QgsField('Distance to water band', QVariant.String, len=254),
                QgsField('Area m2', QVariant.Double, len=10, prec=2),
                QgsField('Area ha', QVariant.Double, len=10, prec=3),
                QgsField('Area km2', QVariant.Double, len=10, prec=5)]
    for f in flds_to_add:
        flds.append(f)
    report_lyr.dataProvider().addAttributes(flds)
    report_lyr.updateFields()
    
    path = water_proximity_layer.source()
    ds = gdal.Open(path)
    arr = ds.ReadAsArray()
    pixel_x_size = ds.GetGeoTransform()[1]
    pixel_y_size = ds.GetGeoTransform()[5]
    pixel_area = pixel_x_size * -pixel_y_size
    b1 = ds.GetRasterBand(1)
    min_val = b1.GetMinimum()
    max_val = b1.GetMaximum()
    max_dist = math.ceil(max_val/500.0)*500.0
    no_classes = int(max_dist/500)
    class_min = min_val
    step = 500
    all_areas = []
    for i in range(no_classes):
        class_max = class_min + step
        class_count = ((arr > class_min)&(arr <= class_max)).sum()
        class_area = class_count*pixel_area
        all_areas.append(class_area)
        #TODO: Create a feature and write attributes e.g. DTW band (0-500m etc.), area m2, area ha & area km2
        print(f'Paddock area between {int(class_min)}m and {int(class_max)}m from water: {round(class_area/10000, 2)}ha')
        class_min+=step
        
    total_area = sum(all_areas)
    print(round(total_area, 2))