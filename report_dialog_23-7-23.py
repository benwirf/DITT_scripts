from PyQt5.QtPrintSupport import QPrintDialog, QPrinter
from PyQt5.QtWebKitWidgets import QWebView
import base64


class ExportToPdfDialog(QDialog):
    def __init__(self):
        super(ExportToPdfDialog, self).__init__()
        
        self.project = QgsProject.instance()
        self.pdk_lyr = self.project.mapLayersByName('Paddocks')[0]
        self.wpt_lyr = self.project.mapLayersByName('Waterpoints')[0]
        self.fence_lyr = self.project.mapLayersByName('Fences')[0]
        self.pipe_lyr = self.project.mapLayersByName('Pipelines')[0]
        self.wa_lyr = self.project.mapLayersByName('Watered Areas')[0]
        
        self.setWindowTitle('Paddock Development Report')
        self.setMinimumWidth(800)
        self.setMinimumHeight(800)
        self.setGeometry(QStyle.alignedRect(
                            Qt.LeftToRight,
                            Qt.AlignCenter,
                            self.size(),
                            qApp.desktop().availableGeometry()))
                            
        self.paddocksLabel = QLabel('Developed Paddocks:', self)
        self.paddocksComboBox = QComboBox(self)
        self.titleLabel = QLabel('Development Title:', self)
        self.titleEdit = QLineEdit('Proposed Development Option', self)
        self.reportOptionLabel = QLabel('Report Template:', self)
        self.basicReportRadioButton = QRadioButton('Basic Report', self)
        self.basicReportRadioButton.setChecked(True)
        self.advancedReportRadioButton = QRadioButton('Advanced Report', self)
        self.previewButton = QPushButton('Preview', self)
#        self.exportButton = QPushButton('Export', self)
        self.paddocksComboBox.addItems(self.getDevelopedPaddocks())
        self.previewButton.clicked.connect(self.showPreview)
        self.widget_layout = QGridLayout()
        self.widget_layout.addWidget(self.paddocksLabel, 0, 0, 1, 1)
        self.widget_layout.addWidget(self.paddocksComboBox, 0, 1, 1, 3)
        self.widget_layout.addWidget(self.titleLabel, 1, 0, 1, 1)
        self.widget_layout.addWidget(self.titleEdit, 1, 1, 1, 3)
        self.widget_layout.addWidget(self.reportOptionLabel, 2, 0, 1, 1)
        self.widget_layout.addWidget(self.basicReportRadioButton, 2, 1, 1, 1)
        self.widget_layout.addWidget(self.advancedReportRadioButton, 2, 2, 1, 1)
        self.widget_layout.addWidget(self.previewButton, 2, 3, 1, 1)
#        self.widget_layout.addWidget(self.exportButton, 3, 2, 1, 1)
        self.view = QWebView(self)
        self.master_layout = QVBoxLayout(self)
        self.master_layout.addLayout(self.widget_layout)
        self.master_layout.addWidget(self.view)
        
    def getDevelopedPaddocks(self):
        developed_paddocks = []
        planned_waterpoints = [wp for wp in self.wpt_lyr.getFeatures() if wp['Status'] == 'Planned']
        for wpt in planned_waterpoints:
            paddock = [pdk for pdk in self.pdk_lyr.getFeatures() if wpt.geometry().within(pdk.geometry())][0]
            if not paddock['Name'] in developed_paddocks:
                developed_paddocks.append(paddock['Name'])
        planned_fences = [f for f in self.fence_lyr.getFeatures() if f['Status'] == 'Planned']
        for f in planned_fences:
            paddock = [pdk for pdk in self.pdk_lyr.getFeatures() if f.geometry().intersection(pdk.geometry()).length()>5][0]
            if not paddock['Name'] in developed_paddocks:
                developed_paddocks.append(paddock['Name'])
        planned_pipelines = [pl for pl in self.pipe_lyr.getFeatures() if pl['Status'] == 'Planned']
        for pl in planned_pipelines:
            paddock = [pdk for pdk in self.pdk_lyr.getFeatures() if pl.geometry().intersection(pdk.geometry()).length()>5][0]
            if not paddock['Name'] in developed_paddocks:
                developed_paddocks.append(paddock['Name'])
        return developed_paddocks
        
    
    def paddockRenderer(self):
        symbol = QgsFillSymbol.createSimple({'border_width_map_unit_scale': '3x:0,0,0,0,0,0',
                                            'color': '60,179,113,255',
                                            'joinstyle': 'bevel',
                                            'offset': '0,0',
                                            'offset_map_unit_scale': '3x:0,0,0,0,0,0',
                                            'offset_unit': 'MM',
                                            'outline_color': '35,35,35,178',
                                            'outline_style': 'solid',
                                            'outline_width': '0.4',
                                            'outline_width_unit': 'MM',
                                            'style': 'solid'})
        renderer = QgsSingleSymbolRenderer(symbol)
        return renderer
        
    def paddockLabels(self):
        settings = QgsPalLayerSettings()
        txt_format = QgsTextFormat()
        txt_format.setFont(QFont('Arial'))
        txt_format.setSize(10)
        txt_format.setColor(QColor('black'))
        txt_buffer = QgsTextBufferSettings()
        txt_buffer.setSize(0.8)
        txt_buffer.setEnabled(True)
        txt_format.setBuffer(txt_buffer)
        settings.setFormat(txt_format)
        settings.fieldName = """ title(concat("Name",'\n',round("Area (km²)",1),'km²'))"""
        settings.isExpression = True
        settings.drawLabels = True
        labels = QgsVectorLayerSimpleLabeling(settings)
        return labels

    def waterpointRenderer(self):
        fld_name = 'Waterpoint Type'
        categories = []
        base_simple_marker_symbol_layer = QgsSimpleMarkerSymbolLayer.create({'angle': '0', 'cap_style': 'square', 'color': '9,211,251,255', 'horizontal_anchor_point': '1', 'joinstyle': 'bevel', 'name': 'circle', 'offset': '0,0', 'offset_map_unit_scale': '3x:0,0,0,0,0,0', 'offset_unit': 'MM', 'outline_color': '35,35,35,0', 'outline_style': 'solid', 'outline_width': '0', 'outline_width_map_unit_scale': '3x:0,0,0,0,0,0', 'outline_width_unit': 'MM', 'scale_method': 'diameter', 'size': '5', 'size_map_unit_scale': '3x:0,0,0,0,0,0', 'size_unit': 'MM', 'vertical_anchor_point': '1'})
        base_font_marker_symbol_layer = QgsFontMarkerSymbolLayer.create({'angle': '0', 'chr': '', 'color': '0,0,0,255', 'font': 'Calibri', 'font_style': 'Bold', 'horizontal_anchor_point': '1', 'joinstyle': 'bevel', 'offset': '0,-1.59999999999999987', 'offset_map_unit_scale': '3x:0,0,0,0,0,0', 'offset_unit': 'Point', 'outline_color': '0,0,0,255', 'outline_width': '0', 'outline_width_map_unit_scale': '3x:0,0,0,0,0,0', 'outline_width_unit': 'Point', 'size': '8', 'size_map_unit_scale': '3x:0,0,0,0,0,0', 'size_unit': 'Point', 'vertical_anchor_point': '1'})
        ###
        value_map = {'Bore':'B', 'Dam':'D', 'Trough':'T', 'Turkey Nest':'TN', 'Water Tank':'WT', 'Waterhole':'WH',}
        for k, v in value_map.items():
            waterpoint_symbol = QgsMarkerSymbol()
            waterpoint_symbol.appendSymbolLayer(base_simple_marker_symbol_layer.clone())
            waterpoint_font_marker = base_font_marker_symbol_layer.clone()
            waterpoint_font_marker.setCharacter(v)
            waterpoint_symbol.appendSymbolLayer(waterpoint_font_marker)
            waterpoint_cat = QgsRendererCategory(k, waterpoint_symbol, k)
            categories.append(waterpoint_cat)
        renderer = QgsCategorizedSymbolRenderer(fld_name, categories)
        return renderer

    def currentMapLayers(self, pdk_name):
        map_layers = []
        invalid_layer_names = []
        pdk_feats = [ft for ft in self.pdk_lyr.getFeatures() if ft['Name'] == pdk_name and ft['Timeframe'] == 'Current']
        if not pdk_feats:
            return False
        pdk_feat = pdk_feats[0]
        current_pdk_lyr = self.pdk_lyr.materialize(QgsFeatureRequest([pdk_feat.id()]))
        if current_pdk_lyr.isValid():
            current_pdk_lyr.setRenderer(self.paddockRenderer())
            current_pdk_lyr.setLabeling(self.paddockLabels())
            current_pdk_lyr.setLabelsEnabled(True)
            map_layers.append(current_pdk_lyr)
        else:
            invalid_layer_names.append(current_pdk_lyr.name())
        current_wa_feats = [ft for ft in self.wa_lyr.getFeatures() if ft['Paddock Name'] == pdk_name and ft['Timeframe'] == 'Current']
        if current_wa_feats:
            current_wa_lyr = self.wa_lyr.materialize(QgsFeatureRequest([f.id() for f in current_wa_feats]))
            if current_wa_lyr.isValid():
                renderer = self.wa_lyr.renderer().clone()
                renderer.setClassAttribute('Watered')
                current_wa_lyr.setRenderer(renderer)
                current_wa_lyr.triggerRepaint()
                map_layers.append(current_wa_lyr)
            else:
                invalid_layer_names.append(current_wa_lyr.name())
        built_pipeline_feats = [ft for ft in self.pipe_lyr.getFeatures() if ft['Status'] == 'Built' and ft.geometry().intersects(pdk_feat.geometry())]
        if built_pipeline_feats:
            built_pipeline_lyr = self.pipe_lyr.materialize(QgsFeatureRequest([f.id() for f in built_pipeline_feats]))
            if built_pipeline_lyr.isValid():
                built_pipeline_lyr.setRenderer(self.pipe_lyr.renderer().clone())
                map_layers.append(built_pipeline_lyr)
            else:
                invalid_layer_names.append(built_pipeline_lyr.name())
#        built_fences = [ft for ft in self.fence_lyr.getFeatures() if ft['Status'] == 'Built' and ft.geometry().intersection()]
        pdk_wpt_feats = [ft for ft in self.wpt_lyr.getFeatures() if ft['Status'] == 'Built' and ft.geometry().intersects(pdk_feat.geometry())]
        if pdk_wpt_feats:
            current_wpt_lyr = self.wpt_lyr.materialize(QgsFeatureRequest([f.id() for f in pdk_wpt_feats]))
            if current_wpt_lyr.isValid():
                current_wpt_lyr.setRenderer(self.waterpointRenderer())
                map_layers.append(current_wpt_lyr)
            else:
                invalid_layer_names.append(self.wpt_lyr.name())
        return map_layers
        
        
    def futureMapLayers(self, pdk_name):
        map_layers = []
        invalid_layer_names = []
        # Get current paddock feature (for spatial retrieval of future features)
        current_pdk_feats = [ft for ft in self.pdk_lyr.getFeatures() if ft['Name'] == pdk_name and ft['Timeframe'] == 'Current']
        if not current_pdk_feats:
            return False
        current_pdk_feat = current_pdk_feats[0]
        current_pdk_geom = current_pdk_feat.geometry()
        
        future_pdk_ids = [ft.id() for ft in self.pdk_lyr.getFeatures() if ft['Timeframe'] == 'Future' and (ft.geometry().intersection(current_pdk_geom).area()>1)]
        # print(future_pdk_ids)
        if not future_pdk_ids:
            future_pdk_ids = [ft.id() for ft in current_pdk_feats]
        future_pdk_lyr = self.pdk_lyr.materialize(QgsFeatureRequest(future_pdk_ids))
        if future_pdk_lyr.isValid():
            future_pdk_lyr.setRenderer(self.paddockRenderer())
            future_pdk_lyr.setLabeling(self.paddockLabels())
            future_pdk_lyr.setLabelsEnabled(True)
            map_layers.append(future_pdk_lyr)
        else:
            invalid_layer_names.append(future_pdk_lyr.name())
            
        future_pdk_names = [ft['Name'] for ft in future_pdk_lyr.getFeatures()]
        future_wa_feats = [ft for ft in self.wa_lyr.getFeatures() if ft['Paddock Name'] in future_pdk_names and ft['Timeframe'] == 'Future']
        if future_wa_feats:
            future_wa_lyr = self.wa_lyr.materialize(QgsFeatureRequest([f.id() for f in future_wa_feats]))
            if future_wa_lyr.isValid():
                renderer = self.wa_lyr.renderer().clone()
                renderer.setClassAttribute('Watered')
                future_wa_lyr.setRenderer(renderer)
                future_wa_lyr.triggerRepaint()
                map_layers.append(future_wa_lyr)
            else:
                invalid_layer_names.append(future_wa_lyr.name())
        built_pipeline_feats = [ft for ft in self.pipe_lyr.getFeatures() if ft['Status'] == 'Built' and ft.geometry().intersects(pdk_feat.geometry())]
        if built_pipeline_feats:
            built_pipeline_lyr = self.pipe_lyr.materialize(QgsFeatureRequest([f.id() for f in built_pipeline_feats]))
            if built_pipeline_lyr.isValid():
                built_pipeline_lyr.setRenderer(self.pipe_lyr.renderer().clone())
                map_layers.append(built_pipeline_lyr)
            else:
                invalid_layer_names.append(self.pipe_lyr.name())
#        built_fences = [ft for ft in self.fence_lyr.getFeatures() if ft['Status'] == 'Built' and ft.geometry().intersection()]
        future_wpt_feats = [ft for ft in self.wpt_lyr.getFeatures() if ft['Status'] in ['Planned', 'Built'] and ft.geometry().intersects(current_pdk_geom)]
        if future_wpt_feats:
            future_wpt_lyr = self.wpt_lyr.materialize(QgsFeatureRequest([f.id() for f in future_wpt_feats]))
            if future_wpt_lyr.isValid():
                future_wpt_lyr.setRenderer(self.wpt_lyr.renderer().clone())
                map_layers.append(future_wpt_lyr)
            else:
                invalid_layer_names.append(future_wpt_lyr.name())
        return map_layers
        
        
    def showPreview(self):
        if self.advancedReportRadioButton.isChecked():
            # Create image tag for current layers
            current_layers = self.currentMapLayers(self.paddocksComboBox.currentText())
            current_layers_ordered = [current_layers[2], current_layers[1], current_layers[0]]
            # print(current_layers_ordered)
            settings = QgsMapSettings()
            settings.setOutputDpi(350)
            settings.setLayers(current_layers_ordered)
            settings.setExtent(current_layers[0].extent())
            settings.setBackgroundColor(QColor(255, 255, 255))
            settings.setOutputSize(QSize(1200, 1200))
            render = QgsMapRendererParallelJob(settings)
            # Start the rendering
            render.start()
            render.waitForFinished()
            img = render.renderedImage()
            byte_array = QByteArray()
            buffer = QBuffer(byte_array)
            buffer.open(QIODevice.WriteOnly)
            img.save(buffer, "PNG")
            img_tag1 = "<img src='data:image/png;base64,{}' width='500' height='500'>".format(base64.b64encode(byte_array).decode())
            
            # Create image tag for future layers
            future_layers = self.futureMapLayers(self.paddocksComboBox.currentText())
            future_layers_ordered = [future_layers[2], future_layers[1], future_layers[0]]
            print(future_layers_ordered)
            settings = QgsMapSettings()
            settings.setOutputDpi(350)
            settings.setLayers(future_layers_ordered)
            full_extent = settings.fullExtent()
            longest_dim = max([full_extent.width(), full_extent.height()])
            grow_factor = longest_dim/20
            full_extent.grow(grow_factor)
            settings.setExtent(full_extent)
            settings.setBackgroundColor(QColor(255, 255, 255))
            settings.setOutputSize(QSize(1200, 1200))
            render = QgsMapRendererParallelJob(settings)
            # Start the rendering
            render.start()
            render.waitForFinished()
            img = render.renderedImage()
            byte_array = QByteArray()
            buffer = QBuffer(byte_array)
            buffer.open(QIODevice.WriteOnly)
            img.save(buffer, "PNG")
            img_tag2 = "<img src='data:image/png;base64,{}' width='500' height='500'>".format(base64.b64encode(byte_array).decode())
            
            html_text = "<html>\
                        <body>\
                        <h1>\
                        Paddock Power Investment Calculator Data\
                        </h1><br>"
            html_text+="<div class=\"image-div\">"
            html_text+=img_tag1
            html_text+=img_tag2
            html_text+="</div>"
            html_text += "</body>\
                            </html>"
            html_text += "<style>\
                        img{border: 5px solid #555;}\
                        </style>"
#            print(html_text)
#            txt_doc = QTextDocument()
#            
#            css_sheet = self.css()
#            self.view.setStyleSheet(css_sheet)
#            txt_doc.setHtml(html_text)
#            txt_item = QGraphicsTextItem()
#            txt_item.setDocument(txt_doc)
#            graphics_scene = QGraphicsScene()
#            graphics_scene.addItem(txt_item)
#            self.view.setScene(graphics_scene)
            self.view.setHtml(html_text)
            
#            pdf_path = 'C:\\Users\\qw2\\Desktop\\MLA-PP\\Test_PDF\\BBB_test_report.pdf'
#            printer = QPrinter()
##            page_layout = QPageLayout()
##            page_layout.setPageSize(QPageSize(QPageSize.A4))
##            page_layout.setOrientation(QPageLayout.Landscape)
##            printer.setPageLayout(page_layout)
#            printer.setOrientation(QPrinter.Landscape)
#            printer.setOutputFormat(QPrinter.PdfFormat)
#            printer.setOutputFileName(pdf_path)
#            txt_doc.print_(printer)

    def css(self):
        #This is not being used (using in line style)
        return 'body{background-color: gray;}\
                img{border: 5px solid black;}'

########################################################################################################
        
dlg = ExportToPdfDialog()
dlg.show()
