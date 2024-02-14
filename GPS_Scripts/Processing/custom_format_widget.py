
class CustomFormatWidget(QWidget):
    def __init__(self):
        super(CustomFormatWidget, self).__init__()
        self.setGeometry(500, 300, 500, 200)
        self.format_cb_lbl = QLabel('Date String Format', self)
        self.format_cb = QComboBox(self)
        self.format_cb.addItems(self.common_formats())
        self.format_cb.setEditable(True)
        self.help_btn = QPushButton(QIcon(":images/themes/default/propertyicons/metadata.svg"), '', self)
        self.help_btn.setToolTip('Get Help')
        self.layout = QHBoxLayout(self)
        self.layout.addWidget(self.format_cb_lbl)
        self.layout.addWidget(self.format_cb, 1)
        self.layout.addWidget(self.help_btn)
        
        self.help_widget = HelpWidget(self)
        self.help_btn.clicked.connect(lambda: self.help_widget.show())
    
    def common_formats(self):
        return ['%Y-%m-%d %H:%M:%SZ',
                '%d/%m/%Y %H:%M:%S',
                '%d-%m-%Y',
                '%d/%m/%Y',
                '%Y-%m-%d',
                '%Y/%m/%d']
                
    def getFormat(self):
        return self.format_cb.currentText()
        
        
class HelpWidget(QWidget):
    def __init__(self, parent=None):
        super(HelpWidget, self).__init__()
        self.help_label = QLabel('See table below for common date/time strings \n\
        and corresponding datetime formats', self)
        self.rows = [['2022-05-18 20:35:20Z', '%Y-%m-%d %H:%M:%SZ'],
                    ['18/05/2022 00:06:02', '%d/%m/%Y %H:%M:%S'],
                    ['18-05-2022', '%d-%m-%Y'],
                    ['18/05/2022', '%d/%m/%Y'],
                    ['2022-05-18', '%Y-%m-%d'],
                    ['2022/05/18', '%Y/%m/%d']]
        self.tbl = QTableWidget()
        self.tbl.setColumnCount(2)
        self.tbl.setRowCount(6)
        self.tbl.setHorizontalHeaderLabels(['String Format', 'DateTime Format'])
        for row in range(self.tbl.rowCount()):
            for col in range(self.tbl.columnCount()):
                item = QTableWidgetItem(self.rows[row][col])
                self.tbl.setItem(row, col, item)
        self.tbl.resizeColumnsToContents()
        self.tbl.setStyleSheet('color: blue')
        self.setMinimumWidth(self.tbl.columnWidth(0)+self.tbl.columnWidth(1)+50)
        self.layout = QVBoxLayout(self)
        self.layout.addWidget(self.help_label, alignment=Qt.AlignCenter)
        self.layout.addWidget(self.tbl)
        
        
w = CustomFormatWidget()
#w = HelpWidget()
w.show()