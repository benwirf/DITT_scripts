###***CHECK LAYER AND LAYOUT NAMES***###

layer = QgsProject.instance().mapLayersByName('Kidman_LU_dissolved')[0]

tbl_headers = ['Symbol', 'Land Unit', 'Land Form', 'Soil', 'Description', 'Area']

tbl_rows = [[QgsTableCell(h) for h in tbl_headers]]

def transform_geom(g):
    xform_zone_test = QgsCoordinateTransform(QgsCoordinateReferenceSystem(layer.sourceCrs()), QgsCoordinateReferenceSystem('epsg:4326'), QgsProject.instance())
    if layer.sourceCrs().authid() != 'EPSG:4326':
        g.transform(xform_zone_test)
    z52_extent = QgsRectangle(125.99, -37.38, 132.00, -9.10)
    geom_z52_extent = QgsGeometry.fromRect(z52_extent)
    z53_extent = QgsRectangle(132.00, -40.71, 138.01, -8.88)
    geom_z53_extent = QgsGeometry.fromRect(z53_extent)
    if g.within(geom_z52_extent):
        utm_transform = QgsCoordinateTransform(QgsCoordinateReferenceSystem('epsg:4326'), QgsCoordinateReferenceSystem('epsg:28352'), QgsProject.instance())
    elif g.within(geom_z53_extent):
        utm_transform = QgsCoordinateTransform(QgsCoordinateReferenceSystem('epsg:4326'), QgsCoordinateReferenceSystem('epsg:28353'), QgsProject.instance())
    g.transform(utm_transform)
    return g

renderer = layer.renderer()
for cat in renderer.categories():
    ft = [f for f in layer.getFeatures() if str(f['LAND_UNIT']) == str(cat.value())][0]
    cat_color = cat.symbol().color()
    symbol_cell = QgsTableCell()
    symbol_cell.setBackgroundColor(cat_color)
    lu = ft['LAND_UNIT']
    lf = ft['LF_CLASS']
    soil = ft['SOIL']
    desc = ft['LF_DESC']
#    area = f"{ft['Area_km2']} km²"
    # Area calculated from geometry
    area = f"{round(transform_geom(ft.geometry()).area()/1000000, 3)} km²"
    tbl_row = [symbol_cell, QgsTableCell(lu), QgsTableCell(lf), QgsTableCell(soil), QgsTableCell(desc), QgsTableCell(area)]
    tbl_rows.append(tbl_row)
    
#    print(cat.value(), cat.symbol().color().toRgb())
#l = QgsProject.instance().layoutManager().layoutByName('land_units')
l = QgsProject.instance().layoutManager().layoutByName('avenza_a2_lu')
t = QgsLayoutItemManualTable.create(l)
l.addMultiFrame(t)
t.setTableContents(tbl_rows)

# Base class for frame items, which form a layout multiframe item.
frame = QgsLayoutFrame(l, t)
frame.attemptResize(QgsLayoutSize(100, 100), True)
t.addFrame(frame)

l.refresh()