
pdk_lyr = QgsProject.instance().mapLayersByName('Mt_Sanford_Paddocks')[0]

wa_lyr = QgsProject.instance().mapLayersByName('Mt_Sanford_3km_WA')[0]

tbl_headers = ['Paddock', 'Total Area', '3km WA', 'Maximum DTW']

tbl_rows = [[QgsTableCell(h) for h in tbl_headers]]

for lyr in QgsProject.instance().mapLayers().values():
    if lyr.providerType() == 'gdal':
#        print(lyr.name())
        area = [f['KM_SQ'] for f in pdk_lyr.getFeatures() if f['PDK_NAME'] == lyr.name()][0]
        area = f'{round(area, 3)}km²'
        wa = [f['AREA_KM2'] for f in wa_lyr.getFeatures() if f['PDK_NAME'] == lyr.name()][0]
        wa = f'{round(wa, 3)}km²'
        max = lyr.dataProvider().bandStatistics(1).maximumValue
        max = f'{round(max/1000, 3)}km'
        tbl_row = [QgsTableCell(lyr.name()), QgsTableCell(area), QgsTableCell(wa), QgsTableCell(max)]
        tbl_rows.append(tbl_row)
    
#    print(cat.value(), cat.symbol().color().toRgb())
l = QgsProject.instance().layoutManager().layoutByName('Layout 1')
t = QgsLayoutItemManualTable.create(l)
l.addMultiFrame(t)
t.setTableContents(tbl_rows)

# Base class for frame items, which form a layout multiframe item.
frame = QgsLayoutFrame(l, t)
frame.attemptResize(QgsLayoutSize(100, 100), True)
t.addFrame(frame)

l.refresh()