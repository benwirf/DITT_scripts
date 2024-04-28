
class SummaryWidget(QWidget):
    def __init__(self):
        super(SummaryWidget, self).__init__()
        
        self.scale_lbl = QLabel('Regional scale categories (edit table cells to use different values):', self)
        
        self.scale_map = {'Northern': ['<1000', '1000-2000', '2000-3000', '>3000'],
                            'Southern': ['<250', '250-500', '500-1000', '>1000']}
        
        self.scale_tbl = QTableWidget(self)
        self.scale_tbl.setColumnCount(5)
        self.scale_tbl.setRowCount(len(self.scale_map))
        self.scale_tbl.setHorizontalHeaderLabels(['Region', 'Low', 'Low/moderate', 'Moderate', 'High'])
        for i in range(self.scale_tbl.rowCount()):
            row_items = [QTableWidgetItem(list(self.scale_map.keys())[i]),
                        QTableWidgetItem(self.scale_map.get(list(self.scale_map.keys())[i])[0]),
                        QTableWidgetItem(self.scale_map.get(list(self.scale_map.keys())[i])[1]),
                        QTableWidgetItem(self.scale_map.get(list(self.scale_map.keys())[i])[2]),
                        QTableWidgetItem(self.scale_map.get(list(self.scale_map.keys())[i])[3]),]
            for j in range(self.scale_tbl.columnCount()):
                self.scale_tbl.setItem(i, j, row_items[j])
        self.scale_tbl.resizeColumnsToContents()
        self.scale_tbl.setMaximumHeight(100)
        
        self.district_lbl = QLabel('District regions:', self)
        
        self.district_regions = ['Darwin', 'Katherine', 'V.R.D.', 'Sturt Plateau', 'Roper', 'Gulf',
                                'Barkly', 'Tennant Creek', 'Northern Alice Springs', 'Plenty', 'Southern Alice Springs']
        
        self.district_tbl = QTableWidget(self)
        self.district_tbl.setColumnCount(2)
        self.district_tbl.setRowCount(len(self.district_regions))
        self.district_tbl.setHorizontalHeaderLabels(['District', 'Regional Scale'])
        for i in range(self.district_tbl.rowCount()):
            cell_item = QTableWidgetItem(self.district_regions[i])
            cell_widget = QComboBox(self)
            cell_widget.addItems(['Northern', 'Southern'])
            if i < 6:
                cell_widget.setCurrentIndex(0)
                cell_widget.setStyleSheet('Color: green')
            else:
                cell_widget.setCurrentIndex(1)
                cell_widget.setStyleSheet('Color: orange')
            cell_widget.currentTextChanged.connect(self.region_changed)
            self.district_tbl.setItem(i, 0, cell_item)
            self.district_tbl.setCellWidget(i, 1, cell_widget)
        self.district_tbl.resizeColumnsToContents()
        
        self.layout = QVBoxLayout(self)
        self.layout.addWidget(self.scale_lbl)
        self.layout.addWidget(self.scale_tbl)
        self.layout.addWidget(self.district_lbl)
        self.layout.addWidget(self.district_tbl)
        # self.setMinimumWidth(800)
        tbl_width = sum([self.scale_tbl.columnWidth(n) for n in range(self.scale_tbl.columnCount())])
        self.setMinimumWidth(tbl_width+50)
        
    def region_changed(self):
        for i in range(self.district_tbl.rowCount()):
            cb = self.district_tbl.cellWidget(i, 1)
            if cb.currentText() == 'Northern':
                cb.setStyleSheet('Color: green')
            elif cb.currentText() == 'Southern':
                cb.setStyleSheet('Color: orange')
        
    def get_scale_cat_vals(self)->dict:
        '''Here we get the cutoff values for the 4 bins, parsed from the
        custon widget scale table'''
        region_scales = {}
        for r in range(self.scale_tbl.rowCount()):
            cell_3 = self.scale_tbl.item(r, 2)
            low_val = cell_3.text().split('-')[0]
            mod_val = cell_3.text().split('-')[1]
            cell_4 = self.scale_tbl.item(r, 4)
            high_val = cell_4.text().split('>')[1]
            region_scales[list(self.scale_map.keys())[r]] = [0, int(low_val), int(mod_val), int(high_val)]
        return region_scales
        
    def get_district_regions(self)->dict:
        '''Here we return a dictionary of each district and its associated
        region from the custon widget district table'''
        district_regions = {}
        for r in range(self.district_tbl.rowCount()):
            pastoral_district = self.district_tbl.item(r, 0).text()
            region = self.district_tbl.cellWidget(r, 1).currentText()
            district_regions[pastoral_district] = region
            if pastoral_district == 'V.R.D.':
                district_regions['Victoria River'] = region
        return district_regions
        
        
w = SummaryWidget()
w.show()
print(w.get_scale_cat_vals())
print(w.get_district_regions())