class CustomInputWidget(QWidget):
    
    def __init__(self):
        super(CustomInputWidget, self).__init__()
        self.setGeometry(300, 300, 850, 550)
        
        # set up temporary layers to hold watered area features
        self.wa3km_lyr = None
        self.wa5km_lyr = None
        
        self.layout = QVBoxLayout(self)
        # Paddock layer input widgets
        self.pdk_lbl = QLabel('Paddock layer:', self)
        self.pdk_layer_mlcb = QgsMapLayerComboBox(self)
        self.pdk_layer_mlcb.setFilters(QgsMapLayerProxyModel.PolygonLayer)
        self.pdk_fld_lbl = QLabel('Field containing paddock names:', self)
        self.pdk_fld_cb = QgsFieldComboBox(self)
        self.pdk_fld_cb.setFilters(QgsFieldProxyModel.String)
        # Waterpoint layer input widgets
        self.waterpoint_lbl = QLabel('Water point layer:', self)
        self.waterpoint_mlcb = QgsMapLayerComboBox(self)
        self.waterpoint_mlcb.setFilters(QgsMapLayerProxyModel.PointLayer)
        self.wp_fld_lbl = QLabel('Field containing waterpoint names:', self)
        self.wp_fld_cb = QgsFieldComboBox(self)
        self.wp_fld_cb.setFilters(QgsFieldProxyModel.String)
        ###Canvas widget
        self.canvas_widget = QWidget(self)
        self.canvas_widget_layout = QHBoxLayout(self.canvas_widget)
        self.canvas = QgsMapCanvas(self.canvas_widget)
        self.canvas.setMinimumWidth(400)
        self.canvas.setMinimumHeight(350)
        self.canvas.setDestinationCrs(QgsProject.instance().crs())
        self.canvas_tool_bar = QToolBar('Canvas toolbar', self.canvas_widget)
        self.action_pan = QAction(QIcon(":images/themes/default/mActionPan.svg"), '', self.canvas_tool_bar)
        self.pan_tool = QgsMapToolPan(self.canvas)
        self.action_pan.triggered.connect(self.set_pan_tool)
        self.canvas_tool_bar.addAction(self.action_pan)
        self.action_reset = QAction(QIcon(":images/themes/default/mActionZoomFullExtent.svg"), '', self.canvas_tool_bar)
        self.action_reset.triggered.connect(lambda: self.canvas.zoomToFullExtent())
        self.canvas_tool_bar.addAction(self.action_reset)
        self.canvas_tool_bar.setOrientation(Qt.Vertical)
        self.canvas_widget_layout.addWidget(self.canvas)
        self.canvas_widget_layout.addWidget(self.canvas_tool_bar)
        ###Table widget
        self.tbl_widget = QWidget(self)
        self.tbl_widget_layout = QHBoxLayout(self.tbl_widget)
        self.tbl = QTableWidget(self)
        self.tbl.setMinimumHeight(80)
        self.tbl_tool_bar = QToolBar('Table toolbar', self.tbl_widget)
        self.action_add = QAction(QIcon(":images/themes/default/symbologyAdd.svg"), '', self.tbl_tool_bar)
        self.action_add.triggered.connect(self.select_paddock)
        self.tbl_tool_bar.addAction(self.action_add)
        self.action_remove = QAction(QIcon(":images/themes/default/symbologyRemove.svg"), '', self.tbl_tool_bar)
        self.action_remove.triggered.connect(self.remove_table_row)
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
        
        self.canvas_layers = [self.wp_lyr, self.pdk_lyr]
        self.set_canvas_layers()
        
        self.reset_table()
        
        self.select_tool = SelectTool(self.canvas, self.pdk_lyr, self.wp_lyr, parent=self)
        self.select_tool_con = self.select_tool.deactivated.connect(self.set_pan_tool)
        
    def set_pan_tool(self):
        self.canvas.setMapTool(self.pan_tool)
            
    def wp_lyr_changed(self):
        self.wp_lyr = self.waterpoint_mlcb.currentLayer()
        self.set_canvas_layers()
        self.wp_fld_cb.setLayer(self.wp_lyr)
        self.canvas.setMapTool(self.pan_tool)
        QObject.disconnect(self.select_tool_con)
        self.select_tool = SelectTool(self.canvas, self.pdk_lyr, self.wp_lyr, self)
        self.select_tool_con = self.select_tool.deactivated.connect(self.set_pan_tool)
        self.reset_table()
                
    def pdk_lyr_changed(self):
        self.pdk_lyr = self.pdk_layer_mlcb.currentLayer()
        self.set_canvas_layers()
        self.pdk_fld_cb.setLayer(self.pdk_lyr)
        self.canvas.setMapTool(self.pan_tool)
        self.select_tool = SelectTool(self.canvas, self.pdk_lyr, self.wp_lyr, self)
        QObject.disconnect(self.select_tool_con)
        self.select_tool = SelectTool(self.canvas, self.pdk_lyr, self.wp_lyr, self)
        self.select_tool_con = self.select_tool.deactivated.connect(self.set_pan_tool)
        self.reset_table()
        
    def set_canvas_layers(self):
        self.canvas_layers = [self.wp_lyr, self.pdk_lyr]
        if self.wa5km_lyr:
            self.canvas_layers.insert(1, self.wa5km_lyr)
        if self.wa3km_lyr:
            self.canvas_layers.insert(1, self.wa3km_lyr)
        self.canvas.setLayers(self.canvas_layers)
        self.canvas.zoomToFullExtent()
    
    def select_paddock(self):
        self.canvas.setMapTool(self.select_tool)
        
    def remove_table_row(self):
        selected_indexes = self.tbl.selectedIndexes()
        selected_rows = list(set([i.row() for i in selected_indexes]))
        # print(selected_rows)
        for row in selected_rows:
            pdk_data = self.tbl.item(row, 0).data(Qt.DisplayRole)
            pdk = pdk_data.split('(')[0]
            if self.wa3km_lyr:
                self.wa3km_lyr.dataProvider().deleteFeatures([ft.id() for ft in self.wa3km_lyr.getFeatures() if ft['Pdk_Name'] == pdk])
                self.wa3km_lyr.updateExtents()
                self.wa3km_lyr.triggerRepaint()
                
            if self.wa5km_lyr:
                self.wa5km_lyr.dataProvider().deleteFeatures([ft.id() for ft in self.wa5km_lyr.getFeatures() if ft['Pdk_Name'] == pdk])
                self.wa5km_lyr.updateExtents()
                self.wa5km_lyr.triggerRepaint()
            
        self.canvas.refresh()
        for i in sorted(selected_rows, reverse=True):
            self.tbl.removeRow(i)
        self.set_pan_tool()
        
    def reset_table(self):
        self.tbl.clear()
        self.tbl.setRowCount(0)
        self.tbl.setColumnCount(2)
        self.tbl.setHorizontalHeaderLabels(['Paddock', 'Water points'])
        if self.wa3km_lyr:
            self.canvas_layers.remove(self.wa3km_lyr)
            self.wa3km_lyr = None
        if self.wa5km_lyr:
            self.canvas_layers.remove(self.wa5km_lyr)
            self.wa5km_lyr = None
        self.set_canvas_layers()
        
    def create_paddock_watered_areas(self):
        wp_crs = self.wp_lyr.sourceCrs()
        pdk_crs = self.pdk_lyr.sourceCrs()

        if not wp_crs.isGeographic():
            # Waterpoint layer is projected, we make the watered area crs the same.
            # We will need to transform the paddock geometries to this one for clipping.
            wa_crs = wp_crs
        elif wp_crs.isGeographic():
            if not pdk_crs.isGeographic():
                # Waterpoint layer is geographic, paddock layer is projected
                # We will make the watered area layer the same as the paddock layer
                # and transform the waterpoint geometries.
                wa_crs = pdk_crs
            elif pdk_crs.isGeographic():
                # Both input layers are geographic- make watered area layer epsg:9473 GDA2020 Australian Albers
                # We will need to transform both input geometries.
                wa_crs = QgsCoordinateReferenceSystem('EPSG:9473')

        # Create 3km WA temporary layer
        if not self.wa3km_lyr:
            self.wa3km_lyr = QgsVectorLayer(f'Polygon?crs={wa_crs.authid()}', '3km_WA', 'memory')
            self.wa3km_lyr.dataProvider().addAttributes([QgsField('Pdk_Name', QVariant.String),
                                                        QgsField('Area_ha', QVariant.Double, len=10, prec=3)])
            self.wa3km_lyr.updateFields()
            # Set 3km WA symbology
            r = self.wa3km_lyr.renderer().clone()
            sym = r.symbol().symbolLayer(0)
            sym.setFillColor(QColor(166,206,227,255))
            sym.setStrokeColor(QColor(31,120,180,255))
            sym.setStrokeWidth(0.35)
            self.wa3km_lyr.setRenderer(r)
            self.wa3km_lyr.triggerRepaint()
        
        # Create 5km WA temporary layer
        if not self.wa5km_lyr:
            self.wa5km_lyr = QgsVectorLayer(f'Polygon?crs={wa_crs.authid()}', '5km_WA', 'memory')
            self.wa5km_lyr.dataProvider().addAttributes([QgsField('Pdk_Name', QVariant.String),
                                                        QgsField('Area_ha', QVariant.Double, len=10, prec=3)])
            self.wa5km_lyr.updateFields()
            # Set 5km WA symbology
            r = self.wa5km_lyr.renderer().clone()
            sym = r.symbol().symbolLayer(0)
            sym.setFillColor(QColor(178,223,138,255))
            sym.setStrokeColor(QColor(51,160,44,255))
            sym.setStrokeWidth(0.35)
            self.wa5km_lyr.setRenderer(r)
            self.wa5km_lyr.triggerRepaint()
        
        for row in range(self.tbl.rowCount()):
            # Get data from first cell of each row
            pdk_info = self.tbl.item(row, 0).data(Qt.DisplayRole)
            pdk_name = pdk_info.split('(')[0]
#            print(pdk_info)
            pdk_id = int(pdk_info.split('(')[1].split(')')[0])
#            print(pdk_id)
            pdk_ft = self.pdk_lyr.getFeature(pdk_id)
            pdk_geom = self.transformed_geom(pdk_ft.geometry(), pdk_crs, wa_crs)
#            print(pdk_geom)
            # get data from second cell of each row,
            wp_info = self.tbl.item(row, 1).data(Qt.DisplayRole)
            # extract ids as integers
            wp_ids = self.parse_waterpoints(wp_info)
            # get list of water point features
            wp_fts = [self.wp_lyr.getFeature(id) for id in wp_ids]
            # get list of waterpoint geometries
            wp_geoms = [self.transformed_geom(ft.geometry(), wp_crs, wa_crs) for ft in wp_fts]
#            print(wp_geoms)
            # collect
            all_wp_geom = QgsGeometry.collectGeometry(wp_geoms)
            # buffer 3km
            buff_geom_3km = all_wp_geom.buffer(3000.0, 25)
            # buffer 5km
            buff_geom_5km = all_wp_geom.buffer(5000.0, 25)
            # and clip with transformed paddock geometry.
            pdk_3km_wa = buff_geom_3km.intersection(pdk_geom)
            # and clip with transformed paddock geometry.
            pdk_5km_wa = buff_geom_5km.intersection(pdk_geom)
            
            # Then, create features, add geometry from clipped buffers, add attributes
            # 3km
            feat_3km = QgsFeature(self.wa3km_lyr.fields())
            feat_3km.setGeometry(pdk_3km_wa)
            feat_3km.setAttributes([pdk_name, pdk_3km_wa.area()])
            # and add feature to watered area layer.
            self.wa3km_lyr.dataProvider().addFeatures([feat_3km])
            self.wa3km_lyr.updateExtents()
            self.wa3km_lyr.triggerRepaint()
            # 5km
            feat_5km = QgsFeature(self.wa5km_lyr.fields())
            feat_5km.setGeometry(pdk_5km_wa)
            feat_5km.setAttributes([pdk_name, pdk_5km_wa.area()])
            # and add feature to watered area layer.
            self.wa5km_lyr.dataProvider().addFeatures([feat_5km])
            self.wa5km_lyr.updateExtents()
            self.wa5km_lyr.triggerRepaint()
                        
            self.canvas.refresh()
            self.set_canvas_layers()
#        print('PING')
            
            
    def transformed_geom(self, g, orig_crs, target_crs):
        geom_copy = QgsGeometry().fromWkt(g.asWkt())
        if orig_crs != target_crs:
            xform = QgsCoordinateTransform(orig_crs, target_crs, QgsProject.instance())
            geom_copy.transform(xform)
        return geom_copy
            

    def parse_waterpoints(self, data_string):
        '''extracts waterpoint ids from string contents of table item'''
        wp_ids = []
        wp_items = data_string.split(';')
        for wp in wp_items:
            wp_id = wp.split('(')[1].split(')')[0]
            wp_ids.append(int(wp_id))
        return wp_ids


class SelectTool(QgsMapTool):
    def __init__(self, canvas, pdk_layer, wp_layer, parent=None):
        self.canvas = canvas
        self.pdk_layer = pdk_layer
        self.wp_layer = wp_layer
        self.parent = parent
        QgsMapTool.__init__(self, self.canvas)
        self.counter = 0
    
    ########################################
    # Manipulate map tool cursor to assist with selecting paddocks and waterpoint
    def canvasMoveEvent(self, e):
        if self.counter == 0:
            # Selecting paddock
            cursor_pos = self.toLayerCoordinates(self.pdk_layer, e.mapPoint())
            if [ft for ft in self.pdk_layer.getFeatures() if ft.geometry().contains(cursor_pos)]:
                self.setCursor(QCursor(Qt.PointingHandCursor))
            else:
                self.setCursor(QCursor(Qt.ArrowCursor))
        elif self.counter > 0:
            # Selecting water points
            cursor_pos = self.toLayerCoordinates(self.wp_layer, e.mapPoint())
            buffer = 100
            if self.wp_layer.sourceCrs().isGeographic():
                buffer = 0.001
            if [ft for ft in self.wp_layer.getFeatures() if ft.geometry().buffer(buffer, 25).contains(cursor_pos)]:
                self.setCursor(QCursor(Qt.CrossCursor))
            else:
                self.setCursor(QCursor(Qt.ArrowCursor))
    ########################################
        
    def canvasPressEvent(self, e):
        if e.button() == Qt.LeftButton:
            self.counter+=1
            if self.counter == 1:
                # we are selecting a paddock
                click_point = self.toLayerCoordinates(self.pdk_layer, e.mapPoint())
                paddock_feat = [ft for ft in self.pdk_layer.getFeatures() if ft.geometry().contains(click_point)][0]
                self.add_paddock_to_table(paddock_feat)
            elif self.counter > 1:
                # we are selecting waterpoints
                click_point = self.toLayerCoordinates(self.wp_layer, e.mapPoint())
                buffer = 100
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
        self.parent.create_paddock_watered_areas()

    def deactivate(self):
        self.counter = 0
        self.deactivated.emit()

        
cw = CustomInputWidget()
cw.show()