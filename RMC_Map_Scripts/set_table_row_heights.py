layout = QgsProject.instance().layoutManager().layoutByName('Willeroo_RMC')
frame = layout.selectedItems()[0]
tbl = frame.multiFrame()
#print(tbl)
tbl_contents = tbl.contents()
#print(tbl_contents)
row_count = len(tbl_contents)
#print(row_count)
row_heights = [8 for i in range(row_count)]
tbl.setRowHeights(row_heights)
tbl.refresh()