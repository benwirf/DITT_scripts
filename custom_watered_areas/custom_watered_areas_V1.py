class CustomInputWidget(QWidget):
    
    def __init__(self):
        super(CustomInputWidget, self).__init__()
        self.setGeometry(300, 300, 800, 500)
        self.layout = QVBoxLayout(self)
        # Paddock layer input widgets
        self.pdk_lbl = QLabel('Paddock layer:', self)
        self.pdk_layer_mlcb = QgsMapLayerComboBox(self)
        self.pdk_layer_mlcb.setFilters(QgsMapLayerProxyModel.PolygonLayer)
        self.pdk_fld_lbl = QLabel('Field containing paddock names', self)
        self.pdk_fld_cb = QgsFieldComboBox(self)
        self.pdk_fld_cb.setFilters(QgsFieldProxyModel.String)
        # Waterpoint layer input widgets
        self.waterpoint_lbl = QLabel('Water point layer:', self)
        self.waterpoint_mlcb = QgsMapLayerComboBox(self)
        self.waterpoint_mlcb.setFilters(QgsMapLayerProxyModel.PointLayer)
        self.wp_fld_lbl = QLabel('Field containing waterpoint names', self)
        self.wp_fld_cb = QgsFieldComboBox(self)
        self.wp_fld_cb.setFilters(QgsFieldProxyModel.String)
        ###Canvas widget
        self.canvas_widget = QWidget(self)
        self.canvas_widget_layout = QHBoxLayout(self.canvas_widget)
        self.canvas = QgsMapCanvas(self.canvas_widget)
        self.canvas.setMinimumWidth(400)
        self.canvas.setMinimumHeight(400)
        self.canvas.setDestinationCrs(QgsProject.instance().crs())
        self.canvas_tool_bar = QToolBar('Canvas toolbar', self.canvas_widget)
        self.action_pan = QAction('Pan', self.canvas_tool_bar)
        self.pan_tool = QgsMapToolPan(self.canvas)
        self.action_pan.triggered.connect(lambda: self.canvas.setMapTool(self.pan_tool))
        self.canvas_tool_bar.addAction(self.action_pan)
        self.action_reset = QAction('Reset', self.canvas_tool_bar)
        self.action_reset.triggered.connect(lambda: self.canvas.zoomToFullExtent())
        self.canvas_tool_bar.addAction(self.action_reset)
        self.canvas_tool_bar.setOrientation(Qt.Vertical)
        self.canvas_widget_layout.addWidget(self.canvas)
        self.canvas_widget_layout.addWidget(self.canvas_tool_bar)
        ###Table widget
        self.tbl_widget = QWidget(self)
        self.tbl_widget_layout = QHBoxLayout(self.tbl_widget)
        self.tbl = QTableWidget(self)
        self.reset_table()
        self.tbl_tool_bar = QToolBar('Table toolbar', self.tbl_widget)
        self.action_add = QAction('Plus', self.tbl_tool_bar)
        self.action_add.triggered.connect(self.select_paddock)
        self.tbl_tool_bar.addAction(self.action_add)
        self.action_remove = QAction('Minus', self.tbl_tool_bar)
#        self.action_remove.triggered.connect()
        self.tbl_tool_bar.addAction(self.action_remove)
        self.tbl_tool_bar.setOrientation(Qt.Vertical)
        self.tbl_widget_layout.addWidget(self.tbl)
        self.tbl_widget_layout.addWidget(self.tbl_tool_bar)
        ###
        self.layout.addWidget(self.pdk_lbl)
        self.layout.addWidget(self.pdk_layer_mlcb)
        self.layout.addWidget(self.pdk_fld_lbl)
        self.layout.addWidget(self.pdk_fld_cb)
        self.layout.addWidget(self.waterpoint_lbl)
        self.layout.addWidget(self.waterpoint_mlcb)
        self.layout.addWidget(self.wp_fld_lbl)
        self.layout.addWidget(self.wp_fld_cb)
        self.layout.addWidget(self.canvas_widget)
        self.layout.addWidget(self.tbl_widget)
        
        self.wp_lyr = self.waterpoint_mlcb.currentLayer()
        wp_conn1 = self.waterpoint_mlcb.layerChanged.connect(self.wp_lyr_changed)
        
        self.pdk_lyr = self.pdk_layer_mlcb.currentLayer()
        pdk_conn1 = self.pdk_layer_mlcb.layerChanged.connect(self.pdk_lyr_changed)
        
        self.wp_fld_cb.setLayer(self.wp_lyr)
        self.pdk_fld_cb.setLayer(self.pdk_lyr)
        self.set_canvas_layers()
        
        self.select_tool = SelectTool(self.canvas, self.pdk_lyr, self.wp_lyr, self)
        self.select_tool.deactivated.connect(lambda: self.canvas.setMapTool(self.pan_tool))
        
        # set up temporary layer to hold watered area features
        self.wa_lyr = None
            
    def wp_lyr_changed(self):
        self.wp_lyr = self.waterpoint_mlcb.currentLayer()
        self.set_canvas_layers()
        self.wp_fld_cb.setLayer(self.wp_lyr)
        self.canvas.setMapTool(self.pan_tool)
        self.select_tool = SelectTool(self.canvas, self.pdk_lyr, self.wp_lyr, self)
        self.reset_table()
                
    def pdk_lyr_changed(self):
        self.pdk_lyr = self.pdk_layer_mlcb.currentLayer()
        self.set_canvas_layers()
        self.pdk_fld_cb.setLayer(self.pdk_lyr)
        self.canvas.setMapTool(self.pan_tool)
        self.select_tool = SelectTool(self.canvas, self.pdk_lyr, self.wp_lyr, self)
        self.select_tool.deactivated.connect(lambda: self.canvas.setMapTool(self.pan_tool))
        self.reset_table()
        
    def set_canvas_layers(self):
        self.canvas.setLayers([self.wp_lyr, self.pdk_lyr])
        self.canvas.zoomToFullExtent()
    
    def select_paddock(self):
        self.canvas.setMapTool(self.select_tool)
        
    def reset_table(self):
        self.tbl.clear()
        self.tbl.setRowCount(0)
        self.tbl.setColumnCount(2)
        self.tbl.setHorizontalHeaderLabels(['Paddock', 'Water points'])
        
    def create_paddock_watered_areas(self):
        pass
    

class SelectTool(QgsMapTool):
    def __init__(self, canvas, pdk_layer, wp_layer, parent=None):
        self.canvas = canvas
        self.pdk_layer = pdk_layer
        self.wp_layer = wp_layer
        self.parent = parent
        QgsMapTool.__init__(self, self.canvas)
        self.counter = 0
        
    def canvasPressEvent(self, e):
        if e.button() == Qt.LeftButton:
            self.counter+=1
            if self.counter == 1:
                # we are selcting a paddock
                click_point = self.toLayerCoordinates(self.pdk_layer, e.mapPoint())
                paddock_feat = [ft for ft in self.pdk_layer.getFeatures() if ft.geometry().contains(click_point)][0]
                self.add_paddock_to_table(paddock_feat)
            elif self.counter > 1:
                # we are selecting waterpoints
                click_point = self.toLayerCoordinates(self.wp_layer, e.mapPoint())
                buffer = 50
                if self.wp_layer.sourceCrs().isGeographic():
                    buffer = 0.001
                waterpoint_feats = [ft for ft in self.wp_layer.getFeatures() if ft.geometry().buffer(buffer, 25).contains(click_point)]
                if waterpoint_feats:
                    waterpoint_feat = waterpoint_feats[0]
                    self.add_waterpoints_to_table(waterpoint_feat)
        elif e.button() == Qt.RightButton:
            self.canvas.unsetMapTool(self)
            self.deactivate()
                
        
    def add_paddock_to_table(self, feat):
        row_count = self.parent.tbl.rowCount()
        self.parent.tbl.setRowCount(row_count + 1)
        idx = row_count
        i = QTableWidgetItem(f'{feat[self.parent.pdk_fld_cb.currentField()]}({feat.id()})')
        self.parent.tbl.setItem(idx, 0, i)
        self.parent.tbl.resizeColumnsToContents()
        
    def add_waterpoints_to_table(self, feat):
        row_count = self.parent.tbl.rowCount()
        row_idx = row_count-1
        item = self.parent.tbl.item(row_idx, 1)
        if not item:
            item = QTableWidgetItem(f'{feat[self.parent.wp_fld_cb.currentField()]}({feat.id()})')
            self.parent.tbl.setItem(row_idx, 1, item)
        else:
            current_data = item.data(Qt.DisplayRole)
            if current_data:
                current_data+=f'; {feat[self.parent.wp_fld_cb.currentField()]}({feat.id()})'
                item.setData(Qt.DisplayRole, current_data)
        self.parent.tbl.resizeColumnsToContents()

    def deactivate(self):
        self.counter = 0
        self.deactivated.emit()

        
cw = CustomInputWidget()
cw.show()