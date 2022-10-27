
layer = QgsProject.instance().mapLayersByName('Owen_Springs_Valley_LU')[0]

tbl_headers = ['Symbol', 'Map Unit', 'Description', 'Area']

tbl_rows = [[QgsTableCell(h) for h in tbl_headers]]

renderer = layer.renderer()
for cat in renderer.categories():
    ft = [f for f in layer.getFeatures() if str(f['MAPUNIT']) == str(cat.value())][0]
    cat_color = cat.symbol().color()
    symbol_cell = QgsTableCell()
    symbol_cell.setBackgroundColor(cat_color)
    mu = ft['MAPUNIT']
    desc = ft['Descrip']
    area = f"{ft['AREA_KM2']} km²"
    tbl_row = [symbol_cell, QgsTableCell(mu), QgsTableCell(desc), QgsTableCell(area)]
    tbl_rows.append(tbl_row)
    
#    print(cat.value(), cat.symbol().color().toRgb())
l = QgsProject.instance().layoutManager().layoutByName('Layout 2')
t = QgsLayoutItemManualTable.create(l)
l.addMultiFrame(t)
t.setTableContents(tbl_rows)

# Base class for frame items, which form a layout multiframe item.
frame = QgsLayoutFrame(l, t)
frame.attemptResize(QgsLayoutSize(100, 100), True)
t.addFrame(frame)

l.refresh()