from pathlib import Path


class CustomWidget(QWidget):
    
    def __init__(self):
        super(CustomWidget, self).__init__()
        self.setGeometry(500, 200, 750, 300)
        ####Input radio buttons
        self.input_rb_layout = QHBoxLayout()
        self.input_rb_group = QButtonGroup(self)
        self.single_input_rb = QRadioButton('Single Input File', self)
        self.single_input_rb.setChecked(True)
        self.multi_input_rb = QRadioButton('Multiple Input Files', self)
        self.folder_input_rb = QRadioButton('Input Directory', self)
        self.input_rb_group.addButton(self.single_input_rb)
        self.input_rb_group.addButton(self.multi_input_rb)
        self.input_rb_group.addButton(self.folder_input_rb)
        self.input_rb_layout.addWidget(self.single_input_rb)
        self.input_rb_layout.addWidget(self.multi_input_rb)
        self.input_rb_layout.addWidget(self.folder_input_rb)
        self.input_rb_group.buttonToggled.connect(self.manageInputWidgets)
        ######################################
        ####Single input file widget
        self.input_layer_widget = InputLayerFileWidget(self)
        ######################################
        ####Multiple input file widget
        self.input_files_label = QLabel('Input Files:', self)
        self.input_files_label.setEnabled(False)
        self.input_files_widget = QgsFileWidget(self)
        self.input_files_widget.setStorageMode(QgsFileWidget.GetMultipleFiles)
        self.input_files_widget.setEnabled(False)
        ######################################
        ####Input folder widget
        self.input_folder_label = QLabel('Input Directory:', self)
        self.input_folder_label.setEnabled(False)
        self.input_folder_widget = QgsFileWidget(self)
        self.input_folder_widget.setStorageMode(QgsFileWidget.GetDirectory)
        self.input_folder_widget.setEnabled(False)
        ######################################
        self.main_layout = QVBoxLayout(self)
        self.main_layout.addLayout(self.input_rb_layout)
        self.main_layout.addWidget(self.input_layer_widget)
        self.main_layout.addWidget(self.input_files_label)
        self.main_layout.addWidget(self.input_files_widget)
        self.main_layout.addWidget(self.input_folder_label)
        self.main_layout.addWidget(self.input_folder_widget)
        
    def manageInputWidgets(self):
        if self.single_input_rb.isChecked():
            #Enable input layer widget
            self.input_layer_widget.enableWidgets()
            self.input_files_label.setEnabled(False)
            self.input_files_widget.setEnabled(False)
            self.input_folder_label.setEnabled(False)
            self.input_folder_widget.setEnabled(False)
        elif self.multi_input_rb.isChecked():
            #Enable input files widget
            self.input_layer_widget.disableWidgets()
            self.input_files_label.setEnabled(True)
            self.input_files_widget.setEnabled(True)
            self.input_folder_label.setEnabled(False)
            self.input_folder_widget.setEnabled(False)
        elif self.folder_input_rb.isChecked():
            #Enable input folder widget
            self.input_layer_widget.disableWidgets()
            self.input_files_label.setEnabled(False)
            self.input_files_widget.setEnabled(False)
            self.input_folder_label.setEnabled(True)
            self.input_folder_widget.setEnabled(True)

class InputLayerFileWidget(QWidget):
    
    def __init__(self, parent=None):
        self.parent = parent
        QWidget.__init__(self)
        self.v_layout = QVBoxLayout()
        self.lbl = QLabel('Input layer:')
        self.selection_widget = QWidget()
        self.h_layout = QHBoxLayout()
        self.mlcb = QgsMapLayerComboBox(self.selection_widget)
        self.mlcb.setFilters(QgsMapLayerProxyModel.PointLayer)
        self.file_selection_button = QPushButton("\u2026", self.selection_widget)
        self.file_selection_button.setMaximumWidth(25)
        self.file_selection_button.setToolTip('Select from file')
        for c in self.selection_widget.children():
            self.h_layout.addWidget(c)
        self.selection_widget.setLayout(self.h_layout)
        self.v_layout.addWidget(self.lbl)
        self.v_layout.addWidget(self.selection_widget)
        self.setLayout(self.v_layout)
        
        self.file_selection_button.clicked.connect(self.getFile)
        
    def enableWidgets(self):
        for c in self.children():
            if isinstance(c, QLabel) or isinstance(c, QWidget):
                c.setEnabled(True)
                
    def disableWidgets(self):
        for c in self.children():
            if isinstance(c, QLabel) or isinstance(c, QWidget):
                c.setEnabled(False)
        
    def getFile(self):
        file_name = QFileDialog.getOpenFileName(None, 'Select file', '', filter='*.shp; *.gpkg; *.tab')
        if file_name:
            self.mlcb.setAdditionalItems([file_name[0]])
            self.mlcb.setCurrentIndex(self.mlcb.model().rowCount()-1)
                
    def currentLayer(self):
        layer = self.mlcb.currentLayer()
        if layer is not None:
            return layer
        else:
            path = self.mlcb.currentText()
            name = Path(path).stem
            layer = QgsVectorLayer(path, name, 'ogr')
            if layer.isValid():
                return layer
        return None
        
w = CustomWidget()
w.show()

