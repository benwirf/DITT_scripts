class CustomWateredAreasWidget(QWidget):
    
    def __init__(self, parent):
        super(CustomWateredAreasWidget, self).__init__()
        self.parent = parent
        self.setGeometry(200, 100, 850, 550)
        
        # define nullptr temporary layer variables to hold watered area features
        self.wa3km_lyr = None
        self.wa5km_lyr = None
        
        self.layout = QVBoxLayout(self)
        # Input layers widget
        self.input_layers_widget = QWidget(self)
        self.input_layers_layout = QFormLayout(self.input_layers_widget)
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

        self.input_layers_layout.addRow(self.pdk_lbl, self.pdk_layer_mlcb)
        self.input_layers_layout.addRow(self.pdk_fld_lbl, self.pdk_fld_cb)
        self.input_layers_layout.addRow(self.waterpoint_lbl, self.waterpoint_mlcb)
        self.input_layers_layout.addRow(self.wp_fld_lbl, self.wp_fld_cb)
        
        ###Canvas widget
        self.canvas_widget = QWidget(self)
        self.canvas_widget_layout = QHBoxLayout(self.canvas_widget)
        self.canvas = QgsMapCanvas(self.canvas_widget)
        self.canvas.setMinimumWidth(800)
        self.canvas.setMinimumHeight(450)
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
        
        ###Checkbox widget
        self.checkbox_widget = QWidget(self)
        self.checkbox_layout = QHBoxLayout(self.checkbox_widget)
        self.report_checkbox = QCheckBox('Create report spreadsheet?', self.checkbox_widget)
        self.checkbox_conn = self.report_checkbox.stateChanged.connect(self.manage_checkboxes)
        self.load_checkbox = QCheckBox('Load outputs?', self.checkbox_widget)
        self.load_checkbox.setCheckState(Qt.Checked)
        self.checkbox_layout.addWidget(self.report_checkbox)
        self.checkbox_layout.addWidget(self.load_checkbox)
                
        self.file_widget = QgsFileWidget(self)
        self.file_widget.lineEdit().setPlaceholderText('Temporary Folder')
        self.file_widget.setStorageMode(QgsFileWidget.GetDirectory)
        self.file_widget_conn = self.file_widget.lineEdit().valueChanged.connect(self.manage_checkboxes)
        
        ### Outputs widget
        self.outputs_widget = QWidget(self)
        self.outputs_layout = QHBoxLayout(self.outputs_widget)
        self.close_btn = QPushButton(QIcon(':images/themes/default/mIconClose.svg'), '' , self.outputs_widget)
        self.close_btn.clicked.connect(lambda: self.close())
        self.export_btn = QPushButton(QIcon(':images/themes/default/mActionSharingExport.svg'), '' , self.outputs_widget)
        self.export_btn.clicked.connect(self.export)
        self.outputs_layout.addStretch()
        self.outputs_layout.addWidget(self.close_btn)
        self.outputs_layout.addWidget(self.export_btn)
        self.outputs_layout.addStretch()
                
        self.layout.addWidget(self.input_layers_widget)
        self.layout.addWidget(self.canvas_widget)
        self.layout.addWidget(self.tbl_widget)
        self.layout.addWidget(self.checkbox_widget)
        self.layout.addWidget(self.file_widget)
        self.layout.addWidget(self.outputs_widget)
        
        self.wp_lyr = self.waterpoint_mlcb.currentLayer()
        self.wp_conn1 = self.waterpoint_mlcb.layerChanged.connect(self.wp_lyr_changed)
        
        self.pdk_lyr = self.pdk_layer_mlcb.currentLayer()
        self.pdk_conn1 = self.pdk_layer_mlcb.layerChanged.connect(self.pdk_lyr_changed)
        
        self.wp_fld_cb.setLayer(self.wp_lyr)
        self.pdk_fld_cb.setLayer(self.pdk_lyr)
        
        self.canvas_layers = [self.wp_lyr, self.pdk_lyr]
        self.set_canvas_layers()
        
        self.reset_table()
        
        self.select_tool = SelectTool(self.canvas, self.pdk_lyr, self.wp_lyr, parent=self)
        self.select_tool_conn = self.select_tool.deactivated.connect(self.set_pan_tool)
        
            
    def manage_checkboxes(self):
        if self.file_widget.lineEdit().value() == '':
            if self.load_checkbox.checkState() == Qt.Unchecked:
                self.load_checkbox.setCheckState(Qt.Checked)
            if self.report_checkbox.checkState() == Qt.Checked:
                self.load_checkbox.setEnabled(False)
            elif self.report_checkbox.checkState() == Qt.Unchecked:
                self.load_checkbox.setEnabled(True)
        elif self.file_widget.lineEdit().value() != '':
            self.load_checkbox.setEnabled(True)
        
    def set_pan_tool(self):
        self.canvas.unsetMapTool(self.canvas.mapTool())
        self.canvas.setMapTool(self.pan_tool)
            
    def wp_lyr_changed(self):
        self.wp_lyr = self.waterpoint_mlcb.currentLayer()
        self.set_canvas_layers()
        self.wp_fld_cb.setLayer(self.wp_lyr)
        self.canvas.setMapTool(self.pan_tool)
        QObject.disconnect(self.select_tool_conn)
        self.select_tool = SelectTool(self.canvas, self.pdk_lyr, self.wp_lyr, self)
        self.select_tool_conn = self.select_tool.deactivated.connect(self.set_pan_tool)
        self.reset_table()
                
    def pdk_lyr_changed(self):
#        print('paddock layer changed')
        self.pdk_lyr = self.pdk_layer_mlcb.currentLayer()
        self.set_canvas_layers()
        self.pdk_fld_cb.setLayer(self.pdk_lyr)
        self.canvas.setMapTool(self.pan_tool)
        self.select_tool = SelectTool(self.canvas, self.pdk_lyr, self.wp_lyr, self)
        QObject.disconnect(self.select_tool_conn)
        self.select_tool = SelectTool(self.canvas, self.pdk_lyr, self.wp_lyr, self)
        self.select_tool_conn = self.select_tool.deactivated.connect(self.set_pan_tool)
        self.reset_table()
        
    def set_canvas_layers(self):
#        print('set_canvas_layers called')
        self.canvas_layers = [self.wp_lyr, self.pdk_lyr]
        if self.wa5km_lyr:
            self.canvas_layers.insert(1, self.wa5km_lyr)
        if self.wa3km_lyr:
            self.canvas_layers.insert(1, self.wa3km_lyr)
        self.canvas.setLayers(self.canvas_layers)
        self.canvas.zoomToFullExtent()
    
    def select_paddock(self):
        if self.canvas.mapTool() == self.select_tool:
            self.select_tool.counter = 0
        else:
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
                                                        QgsField('Water pts', QVariant.String)])
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
                                                        QgsField('Water pts', QVariant.String)])
            self.wa5km_lyr.updateFields()
            # Set 5km WA symbology
            r = self.wa5km_lyr.renderer().clone()
            sym = r.symbol().symbolLayer(0)
            sym.setFillColor(QColor(178,223,138,255))
            sym.setStrokeColor(QColor(51,160,44,255))
            sym.setStrokeWidth(0.35)
            self.wa5km_lyr.setRenderer(r)
            self.wa5km_lyr.triggerRepaint()
        
        self.wa3km_lyr.dataProvider().deleteFeatures([ft.id() for ft in self.wa3km_lyr.getFeatures()])
        self.wa5km_lyr.dataProvider().deleteFeatures([ft.id() for ft in self.wa5km_lyr.getFeatures()])
        
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
            
            # Then create features, add geometry from clipped buffers and add attributes
            # 3km
            feat_3km = QgsFeature(self.wa3km_lyr.fields())
            feat_3km.setGeometry(pdk_3km_wa)
            feat_3km.setAttributes([pdk_name, str(wp_info)])
            # and add feature to watered area layer.
            self.wa3km_lyr.dataProvider().addFeatures([feat_3km])
            self.wa3km_lyr.updateExtents()
            self.wa3km_lyr.triggerRepaint()
            # 5km
            feat_5km = QgsFeature(self.wa5km_lyr.fields())
            feat_5km.setGeometry(pdk_5km_wa)
            feat_5km.setAttributes([pdk_name, str(wp_info)])
            # and add feature to watered area layer.
            self.wa5km_lyr.dataProvider().addFeatures([feat_5km])
            self.wa5km_lyr.updateExtents()
            self.wa5km_lyr.triggerRepaint()
                        
        self.canvas.refresh()
        self.set_canvas_layers()
            
            
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
        
    def export(self):
        #TODO:
        # If output is set to Temporary Folder, it is not necessary to create or
        # load the spreadsheet report, so this option should only be available if
        # an actual file path is specified. And the Excel sheets should not be loaded
        # as tabular layers at all (since they will be identical to the attribute tables of the two output vector layers.
        if (not self.wa3km_lyr and not self.wa5km_lyr) or (self.wa3km_lyr.featureCount() == 0 and self.wa5km_lyr.featureCount() == 0):
            msg_box = QMessageBox(self)
            msg_box.setText('No watered areas to export!')
            msg_box.exec()
            return
        #QgsField('Area_ha', QVariant.Double, len=10, prec=3)
        elif self.wa3km_lyr and self.wa5km_lyr:
            # Create memory based copy of minimal WA layers
            wa_3km_output = self.wa3km_lyr.materialize(QgsFeatureRequest())
            wa_5km_output = self.wa5km_lyr.materialize(QgsFeatureRequest())
            # Add additional area fields for exporting
            wa_3km_output.dataProvider().addAttributes([QgsField('Area_m2', QVariant.Double, len=10, prec=3),
                                                        QgsField('Area_ha', QVariant.Double, len=10, prec=3),
                                                        QgsField('Area_km2', QVariant.Double, len=10, prec=5)])
            wa_3km_output.updateFields()
            wa_5km_output.dataProvider().addAttributes([QgsField('Area_m2', QVariant.Double, len=10, prec=3),
                                                        QgsField('Area_ha', QVariant.Double, len=10, prec=3),
                                                        QgsField('Area_km2', QVariant.Double, len=10, prec=5)])
            wa_5km_output.updateFields()
            # Calculate and fill area fields for each feature in both output layers
            wa_3km_flds = wa_3km_output.fields()
            wa_3km_att_map = {ft.id(): {wa_3km_flds.lookupField('Area_m2'): ft.geometry().area(), wa_3km_flds.lookupField('Area_ha'): ft.geometry().area()/10000, wa_3km_flds.lookupField('Area_km2'): ft.geometry().area()/1000000} for ft in wa_3km_output.getFeatures()}
            wa_3km_output.dataProvider().changeAttributeValues(wa_3km_att_map)
            
            wa_5km_flds = wa_5km_output.fields()
            wa_5km_att_map = {ft.id(): {wa_5km_flds.lookupField('Area_m2'): ft.geometry().area(), wa_5km_flds.lookupField('Area_ha'): ft.geometry().area()/10000, wa_5km_flds.lookupField('Area_km2'): ft.geometry().area()/1000000} for ft in wa_5km_output.getFeatures()}
            wa_5km_output.dataProvider().changeAttributeValues(wa_5km_att_map)
                        
            if self.file_widget.lineEdit().value() == '':
                # We are working with tempory outputs
                if self.report_checkbox.checkState() == Qt.Checked:
                    # We want to export layers to spreadsheet and point output to a temp folder
                    temp_dir = QTemporaryDir()
                    temp_dir.setAutoRemove(False)
                    if not temp_dir.isValid():
                        msg_box = QMessageBox(self)
                        msg_box.setText('Could not create temporary output directory!')
                        msg_box.exec()
                        return
                    report_path = os.path.join(temp_dir.path(), 'Watered_areas.xlsx')
#                    print(report_path)#****************************************************
                    
                    save_2_xlsx_params = {'LAYERS': [wa_3km_output, wa_5km_output],
                                        'USE_ALIAS':False,
                                        'FORMATTED_VALUES':False,
                                        'OUTPUT':report_path,
                                        'OVERWRITE':True}
                                        
                    processing.run("native:exporttospreadsheet", save_2_xlsx_params)
#                    print(os.path.exists(report_path))#****************************************************
                    if os.path.exists(report_path):
                        self.load_tabular_layers(report_path)
                                        
                # We want to set renderer and load layers to project
                wa_3km_output.setRenderer(self.wa3km_lyr.renderer().clone())
                wa_5km_output.setRenderer(self.wa5km_lyr.renderer().clone())
                QgsProject.instance().addMapLayers([wa_3km_output, wa_5km_output])
    
    def load_tabular_layers(self, path):
        uri_3km_wa_tbl = f'{path}|layername=3km_WA'
        uri_5km_wa_tbl = f'{path}|layername=5km_WA'
        report_tbl_3km = QgsVectorLayer(uri_3km_wa_tbl, 'Report_Table-3km_WA', 'ogr')
        report_tbl_5km = QgsVectorLayer(uri_5km_wa_tbl, 'Report_Table-5km_WA', 'ogr')
        if report_tbl_3km.isValid():
            QgsProject.instance().addMapLayers([report_tbl_3km])
        if report_tbl_5km.isValid():
            QgsProject.instance().addMapLayers([report_tbl_5km])
        
        
    def closeEvent(self, e):
        print('Widget closed')
        if self.wa3km_lyr:
            self.wa3km_lyr = None
        if self.wa5km_lyr:
            self.wa5km_lyr = None
        QObject.disconnect(self.wp_conn1)
        QObject.disconnect(self.pdk_conn1)
        QObject.disconnect(self.select_tool_conn)
        QObject.disconnect(self.checkbox_conn)
        QObject.disconnect(self.file_widget_conn)


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

        
cw = CustomWateredAreasWidget(iface.mainWindow())
cw.show()