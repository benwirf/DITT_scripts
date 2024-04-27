
class SummaryWidget(QWidget):
    def __init__(self):
        super(SummaryWidget, self).__init__()
        
        self.scale_lbl = QLabel('Regional categories:', self)
        
        self.scale_map = {'Northern Scale': ['<1000', '1000-2000', '2000-3000', '>3000'],
                            'Southern Scale': ['<250', '250-500', '500-1000', '>1000']}
        
        self.scale_tbl = QTableWidget(self)
        self.scale_tbl.setColumnCount(5)
        self.scale_tbl.setRowCount(len(self.scale_map))
        self.scale_tbl.setHorizontalHeaderLabels(['Region Scale', 'Low', 'Low/moderate', 'Moderate', 'High'])
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
        
        self.district_lbl = QLabel('District scales:', self)
        
        self.district_regions = ['Darwin', 'Katherine', 'V.R.D', 'Sturt Plateau', 'Roper', 'Gulf',
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
                cell_widget.setStyleSheet('Color: brown')
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
                cb.setStyleSheet('Color: brown')
        
        
        
w = SummaryWidget()
w.show()