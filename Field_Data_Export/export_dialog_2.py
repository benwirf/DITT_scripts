
from osgeo import ogr

from pathlib import Path

import os

class DataExportDialog(QDialog):
    
    def __init__(self):
        super(DataExportDialog, self).__init__()
        self.setWindowTitle('Export Field Data')
        self.setMinimumWidth(750)
        self.setMinimumHeight(350)
        self.setGeometry(QStyle.alignedRect(
            Qt.LeftToRight,
            Qt.AlignCenter,
            self.size(),
            qApp.desktop().availableGeometry()))
        
        self.file_lbl = QLabel('Select data geopackage')
        self.file_widget = QgsFileWidget(self)
        self.file_widget.setFilter('*.gpkg')
        self.file_widget.fileChanged.connect(self.file_changed)
        
        self.lw_lbl = QLabel('Select layers to export')
        self.lw = QListWidget(self)
        self.lw.setMaximumHeight(100)
        self.lw.itemChanged.connect(self.populate_table)
        
        self.tbl = QTableWidget(self)
        self.tbl.setColumnCount(5)
        self.tbl.setHorizontalHeaderLabels(['Layer', 'Observer', 'Date', 'Export Folder', 'File Config'])
        
        self.layout = QGridLayout(self)
        self.layout.addWidget(self.file_lbl, 0, 0, 1, 1)
        self.layout.addWidget(self.file_widget, 0, 1, 1, 1)
        self.layout.addWidget(self.lw_lbl, 1, 0, 1, 1)
        self.layout.addWidget(self.lw, 1, 1, 1, 1)
        self.layout.addWidget(self.tbl, 2, 0, 2, 2)
        
        self.export_btn = QPushButton('Export', self)
        self.export_btn.setMaximumWidth(75)
        
        self.close_btn = QPushButton('Close', self)
        self.close_btn.setMaximumWidth(75)
        self.close_btn.clicked.connect(lambda: self.close())
        
        self.btn_layout = QHBoxLayout()
        self.btn_layout.addStretch()
        self.btn_layout.addWidget(self.export_btn)
        self.btn_layout.addWidget(self.close_btn)
        
        self.layout.addLayout(self.btn_layout, 4, 1)

        self.file_path = None
        self.lw_flags = Qt.ItemFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
        self.checked_layer_names = []
        
        self.export_paths = {}

    def file_changed(self, f):
        self.export_paths.clear()
        self.lw.clear()
        # self.tbl.clear()
        self.tbl.setRowCount(0)
        self.file_path = f
        sub_lyr_names = [l.GetName() for l in ogr.Open(self.file_path)]
        self.checked_layer_names = sub_lyr_names
        for n in sub_lyr_names:
            if n.split('_')[0] != 'log':
                li = QListWidgetItem(n)
                li.setFlags(self.lw_flags)
                li.setCheckState(0)
                self.lw.addItem(li)
            
    def populate_table(self, i):
        layer_names = []
        for r in range(self.lw.count()):
            lwi = self.lw.item(r)
            if lwi.checkState() == Qt.Checked:
                l_name = lwi.data(0).split('_')[0]
                layer_names.append(l_name)
                
        if not layer_names:
            self.export_paths.clear()
            
        self.tbl.setRowCount(len(layer_names))
        for i, n in enumerate(layer_names):
            tbl_itm = QTableWidgetItem(n)
            self.tbl.setItem(i, 0, tbl_itm)
            observers = self.get_observers(n)
            # print(observers)
            if observers[0]:
                obs_cb = QComboBox()
                obs_cb.addItems(observers[1])
                self.tbl.setCellWidget(i, 1, obs_cb)
            dates = self.get_dates(n)
            if dates[0]:
                date_cb = QComboBox()
                date_cb.addItems(dates[1])
                self.tbl.setCellWidget(i, 2, date_cb)
            export_file_widget = QgsFileWidget()
            if not observers[1] or not dates[1]:
                export_file_widget.setEnabled(False)
            export_file_widget.setStorageMode(QgsFileWidget.GetDirectory)
            export_file_widget.fileChanged.connect(self.export_path_changed)
            self.tbl.setCellWidget(i, 3, export_file_widget)
            
            if self.export_paths and n in self.export_paths.keys():
                self.tbl.cellWidget(i, 3).setFilePath(self.export_paths[n])
        
        self.tbl.resizeColumnsToContents()
                
                
    def get_observers(self, layer_name):
        gpkg_tbl_name = [name for name in self.checked_layer_names if name.startswith(layer_name)][0]
        if not gpkg_tbl_name:
            return [False, 'Layer not found']
        sub_layer_uri = f'{self.file_path}|layername={gpkg_tbl_name}'
        # print(sub_layer_uri)
        sub_layer = QgsVectorLayer(sub_layer_uri, '', 'ogr')
        if not sub_layer.isValid():
            return [False, 'Layer not valid']
        obs_fld_idx = sub_layer.fields().lookupField('Observer')
        # if obs_fld_idx == -1:
        #     return [False, 'Observer field not found']
        observers = list(sub_layer.uniqueValues(obs_fld_idx))
        return [True, observers]
        
    def get_dates(self, layer_name):
        gpkg_tbl_name = [name for name in self.checked_layer_names if name.startswith(layer_name)][0]
        if not gpkg_tbl_name:
            return [False, 'Layer not found']
        sub_layer_uri = f'{self.file_path}|layername={gpkg_tbl_name}'
        sub_layer = QgsVectorLayer(sub_layer_uri, '', 'ogr')
        if not sub_layer.isValid():
            return [False, 'Layer not valid']
        date_fld_idx = sub_layer.fields().lookupField('Date')
        # if date_fld_idx == -1:
        #     return [False, 'Date field not found']
        dates = list(sub_layer.uniqueValues(date_fld_idx))
        date_strings = [dd.toString() if dd!= NULL else 'NULL' for dd in dates]
        return [True, date_strings]
    
    def export_path_changed(self, path):
        for i in range(self.tbl.rowCount()):
            # print(i)
            # print(self.tbl.item(i, 0))
            cell_item = self.tbl.item(i, 0)
            if cell_item:
                lyr_name = cell_item.text()
                self.export_paths[lyr_name] = self.tbl.cellWidget(i, 3).filePath()
        existing_spreadsheets = [file for file in os.scandir(path) if Path(file).suffix == '.xlsx']
        # print(existing_spreadsheets)
        
                
    def export(self):
        pass
    
dlg = DataExportDialog()
dlg.show()
