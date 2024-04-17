layout = QgsProject.instance().layoutManager().layoutByName('Mt_Sanford_RMC')
frame = layout.selectedItems()[0]
tbl = frame.multiFrame()
#print(tbl)
tbl_contents = tbl.contents()
#print(tbl_contents)
new_contents = []
for row in tbl_contents:
    new_row_contents = []
    if row[0] == 'Paddock':
        new_row_contents = [QgsTableCell(i) for i in row]
    else:
        new_row_contents.append(QgsTableCell(row[0].replace(' PDK', '')))
        for i in row[1:]:
            new_row_contents.append(QgsTableCell(i))
    new_contents.append(new_row_contents)
        
#print(new_contents)
tbl.setTableContents(new_contents)
tbl.refresh()