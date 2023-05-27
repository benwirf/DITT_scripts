from osgeo import gdal

#lyr = QgsProject.instance().mapLayersByName('No_1_PDK')[0]

temp_layers = []

def calculate_areas_in_distance_to_water_bands(water_proximity_layer, band_dist):
    options = QgsVectorLayer.LayerOptions()
    options.loadDefaultStyle=False
    report_lyr = QgsVectorLayer('Point', water_proximity_layer.name(), 'memory', options)
    flds = QgsFields()
    flds_to_add = [QgsField('Pdk Name', QVariant.String),
                QgsField('PdkArea Ha', QVariant.Double, len=10, prec=2),
                QgsField('DTW Band', QVariant.String),
                QgsField('Area m2', QVariant.Double, len=10, prec=2),
                QgsField('Area ha', QVariant.Double, len=10, prec=3),
                QgsField('Area km2', QVariant.Double, len=10, prec=5),
                QgsField('Percent', QVariant.Double, len=10, prec=7)]
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
    max_dist = math.ceil(max_val/float(band_dist))*float(band_dist)
    no_classes = int(max_dist/int(band_dist))
    class_min = min_val
    paddock_area = (arr > min_val).sum()*pixel_area
    for i in range(no_classes):
        class_max = class_min + int(band_dist)
        class_count = ((arr > class_min)&(arr <= class_max)).sum()
        class_area = class_count*pixel_area
        # all_areas.append(class_area)
        #TODO: Create a feature and write attributes e.g. DTW band (0-500m etc.), area m2, area ha & area km2
        # print(f'Paddock area between {int(class_min)}m and {int(class_max)}m from water: {round(class_area/10000, 2)}ha')        
        atts = [water_proximity_layer.name(),
                            float(round(paddock_area/10000, 2)),
                            f'{int(class_min)}m - {int(class_max)}m',
                            float(round(class_area, 2)),
                            float(round(class_area/10000, 3)),
                            float(round(class_area/1000000, 5)),
                            float(round((class_area/paddock_area)*100, 7))]
        # print(atts)
        print([f.name() for f in report_lyr.fields()])
        feat = QgsFeature(report_lyr.fields())
        feat.setAttributes(atts)
        ok = report_lyr.dataProvider().addFeatures([feat])
        if ok[0] == False:
            print(report_lyr.dataProvider().lastError())
        class_min+=int(band_dist)
        
    return report_lyr
    
# Iterate over water_proximity output rasters in layer tree group (or a folder), call the function
# and append the result layer to temp layers list, then use processing.run(export to spreadsheet)
# on the temp layers...
# root_group = iface.layerTreeView().layerTreeModel().rootGroup()
root_group = QgsProject.instance().layerTreeRoot()
water_proximity_group = root_group.findGroup('Water proximity')
water_proximity_rasters = [lyr.layer() for lyr in water_proximity_group.findLayers() if lyr.layer().type() == QgsMapLayerType.RasterLayer]
# print(water_proximity_rasters)
for water_proximity_raster in water_proximity_rasters:
    temp_layers.append(calculate_areas_in_distance_to_water_bands(water_proximity_raster, 500))
# print(temp_layers)
# QgsProject.instance().addMapLayers(temp_layers)
output_xlsx_path = r'/home/ben/DITT/Mulga_Park/For_Robyn/MDTW_test/watered_bands_spreadsheet/watered_band_areas.xlsx'
save_2_xlsx_params = {'LAYERS':temp_layers,
            'USE_ALIAS':False,
            'FORMATTED_VALUES':False,
            'OUTPUT':output_xlsx_path,
            'OVERWRITE':True}

processing.run("native:exporttospreadsheet", save_2_xlsx_params)


