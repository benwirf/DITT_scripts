#WKT Polygon:
#Polygon ((131.3189188116239734 -12.63764675771537505, 131.32450553217927336 -12.63759809170717041, 131.32453351422356036 -12.64069183931674445, 131.31894672656306966 -12.64074051761910766, 131.3189188116239734 -12.63764675771537505))

point_lyr = QgsProject.instance().mapLayersByName('rbg_image_locations')[0]

no_grid_rows = 2
no_grid_cols = 3

buffer_dist = 50# metres

grid_lyr = QgsVectorLayer('Polygon?crs=epsg:4326', f'{no_grid_rows*no_grid_cols}_cell_grid','memory')

flds = [QgsField('ID', QVariant.Int),
        QgsField('CELL_REF', QVariant.Int)]

grid_lyr.dataProvider().addAttributes(flds)
grid_lyr.updateFields()

lyr_ext = point_lyr.extent()

bottom_left_lon = lyr_ext.xMinimum()
bottom_left_lat = lyr_ext.yMinimum()

#print(bottom_left_lon, bottom_left_lat)

cell_width = lyr_ext.width()/no_grid_cols
cell_height = lyr_ext.height()/no_grid_rows

def create_grid_cell(bl_lon, bl_lat):
    # define vertices of grid cell polygon working counter-clockwise from bottom left
    p1 = (bl_lon, bl_lat)# bottom left
    p2 = (bl_lon + cell_width, bl_lat)# bottom right
    p3 = (bl_lon + cell_width, bl_lat + cell_height)# top right
    p4 = (bl_lon, bl_lat + cell_height)
    cell_wkt = f'Polygon (({p1[0]} {p1[1]}, {p2[0]} {p2[1]}, {p3[0]} {p3[1]}, {p4[0]} {p4[1]}, {p1[0]} {p1[1]}))'
    cell_geom = QgsGeometry.fromWkt(cell_wkt)
    return cell_geom

cnt = 1

def create_grid_row(bl_lon, bl_lat):
    global cnt
    for i in range(no_grid_cols):
        feat = QgsFeature(grid_lyr.fields())
        feat_geom = create_grid_cell(bl_lon, bl_lat)
        feat.setGeometry(feat_geom)
        feat.setAttributes([cnt, cnt])
        grid_lyr.dataProvider().addFeature(feat)
        bl_lon += cell_width
        cnt += 1
    
for j in range(no_grid_rows):
    create_grid_row(bottom_left_lon, bottom_left_lat)
    bottom_left_lat += cell_height
    
QgsProject.instance().addMapLayer(grid_lyr)
