#***
# Incomplete
# ***


point_lyr = QgsProject.instance().mapLayersByName('rbg_image_locations')[0]

utm_crs = 'EPSG:28352'

utm_pt_lyr = point_lyr.materialize(QgsFeatureRequest().setDestinationCrs(QgsCoordinateReferenceSystem(utm_crs), QgsProject.instance().transformContext()))

no_grid_rows = 2
no_grid_cols = 3

buffer_dist = 50

grid_lyr = QgsVectorLayer('Polygon?crs=epsg:4326', f'{no_grid_rows*no_grid_cols}_cell_grid','memory')

flds = QgsFields()
flds.append(QgsField('ID', QVariant.Int))

grid_lyr.dataProvider().addAttributes(flds)
grid_lyr.updateFields()

#print(grid_lyr.isValid())
#print(grid_lyr.fields())

lyr_ext = utm_pt_lyr.extent()

print(lyr_ext)
