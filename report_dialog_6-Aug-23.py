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
        self.setMinimumWidth(1100)
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
                future_wpt_lyr.setRenderer(self.waterpointRenderer())
                map_layers.append(future_wpt_lyr)
            else:
                invalid_layer_names.append(future_wpt_lyr.name())
        return map_layers

    def paddockDetails(self, paddock_name, timeframe):
        pdks = [ft for ft in self.pdk_lyr.getFeatures() if ft['Name'] == paddock_name and ft['Timeframe'] == timeframe]
        if pdks:
            pdk = pdks[0]
            pdk_geom = pdk.geometry()
            pdk_area = pdk_geom.area()
            cc = pdk['AE']
            if timeframe == 'Current':
                num_wpts = self.currentNumWaterPoints(pdk_geom)
                wa_3km = self.currentWateredArea(pdk_geom, 3000)
                wa_5km = self.currentWateredArea(pdk_geom, 5000)
            elif timeframe == 'Future':
                num_wpts = self.futureNumWaterPoints(pdk_geom)
                wa_3km = self.plannedWateredArea(pdk_geom, 3000)
                wa_5km = self.plannedWateredArea(pdk_geom, 5000) 
            wa_3km_pcnt = (wa_3km/pdk_area)*100
            wa_5km_pcnt = (wa_5km/pdk_area)*100
            fence_length = pdk_geom.length()
            planned_fencing = self.paddockPlannedFence(pdk_geom)
            current_pipeline = self.paddockCurrentPipe(pdk_geom)
            planned_pipeline = self.paddockPlannedPipe(pdk_geom)

            return [pdk_area,
                    cc,
                    num_wpts,
                    wa_3km,
                    wa_3km_pcnt,
                    wa_5km,
                    wa_5km_pcnt,
                    fence_length,
                    planned_fencing,
                    current_pipeline,
                    planned_pipeline]

        return None

    def currentWateredArea(self, pdk_geom, buff_dist):
        pdk_wpt_buffers = [w.geometry().buffer(buff_dist, 25) for w in self.wpt_lyr.getFeatures() if w['Status'] == 'Built' and w.geometry().intersects(pdk_geom)]
        dissolved_wa = QgsGeometry.unaryUnion(pdk_wpt_buffers)
        wa_geom = dissolved_wa.intersection(pdk_geom)
        return wa_geom.area()
        
    def plannedWateredArea(self, pdk_geom, buff_dist):
        pdk_wpt_buffers = [w.geometry().buffer(buff_dist, 25) for w in self.wpt_lyr.getFeatures() if (w['Status'] == 'Built' or w['Status'] == 'Planned')and w.geometry().intersects(pdk_geom)]
        dissolved_wa = QgsGeometry.unaryUnion(pdk_wpt_buffers)
        wa_geom = dissolved_wa.intersection(pdk_geom)
        return wa_geom.area()
        
    def paddockPlannedFence(self, pdk_geom):
        planned_fences = [f for f in self.fence_lyr.getFeatures() if f['Status'] == 'Planned']
        intersecting_fence = [f.geometry().intersection(pdk_geom) for f in planned_fences]
        total_required_fencing = sum(i.length() for i in intersecting_fence)
        # Return planned fence length in meters
        return total_required_fencing
    
    def paddockCurrentPipe(self, pdk_geom):
        current_pipe = [f for f in self.pipe_lyr.getFeatures() if f['Status'] == 'Built']
        intersecting_pipe = [f.geometry().intersection(pdk_geom) for f in current_pipe]
        total_current_pipe = sum(i.length() for i in intersecting_pipe)
        # Return planned pipe length in meters
        return total_current_pipe
    
    def paddockPlannedPipe(self, pdk_geom):
        planned_pipe = [f for f in self.pipe_lyr.getFeatures() if f['Status'] == 'Planned']
        intersecting_pipe = [f.geometry().intersection(pdk_geom) for f in planned_pipe]
        total_planned_pipe = sum(i.length() for i in intersecting_pipe)
        # Return planned pipe length in meters
        return total_planned_pipe
        
    def currentNumWaterPoints(self, pdk_geom):
        return len([w for w in self.wpt_lyr.getFeatures() if w['Status'] == 'Built' and w.geometry().intersects(pdk_geom)])
        
    def futureNumWaterPoints(self, pdk_geom):
        return len([w for w in self.wpt_lyr.getFeatures() if (w['Status'] == 'Built' or w['Status'] == 'Planned') and w.geometry().intersects(pdk_geom)])
    
    def sign(self, num1, num2):
        diff = num2-num1
        if diff <= 0:
            return ''
        if diff > 0:
            return '+'
            
#####**************METHODS TO GENERATE HTML CONTENT**********************#####
    def basicReportHtml(self, paddock_name, development_name):
        html_text = "<html>\
                    <body>\
                    <h1>\
                    Paddock Power Investment Calculator Data\
                    </h1>"
        current_pdk_details = self.paddockDetails(paddock_name, 'Current')
        if not current_pdk_details:
            return None
        html_text+= f"<div id='current-info'>\
                        <h2>\
                        Current Situation\
                        </h2>\
                        <h3>\
                        {paddock_name}\
                        </h3>\
                        <p>Total paddock area (km²) = {round(current_pdk_details[0]/1000000, 3)}</p>\
                        <p>Recommended carrying capacity (AE/yr) = {round(current_pdk_details[1], 1)}</p>\
                        <p>Number of water points = {current_pdk_details[2]}</p>\
                        <p>3km Watered Area (km² and %) = {round(current_pdk_details[3]/1000000, 3)} | {round(current_pdk_details[4], 1)}</p>\
                        <p>5km Watered Area (km² and %) = {round(current_pdk_details[5]/1000000, 3)} | {round(current_pdk_details[6], 1)}</p>\
                        <p>Length of fencing (km) = {round(current_pdk_details[7]/1000, 3)}</p>\
                        </div>"
        html_text += f"<div id='proposed-development-info'>\
                        <h2>\
                        {development_name}\
                        </h2>"

        pdks = [ft for ft in self.pdk_lyr.getFeatures() if ft['Name'] == paddock_name]
        if pdks:
            pdk = pdks[0]
            pdk_geom = pdk.geometry()
            planned_pdks = [p for p in self.pdk_lyr.getFeatures() if p['Status'] == 'Planned' and p.geometry().intersects(pdk_geom)]
            if planned_pdks:
                # The original paddock has been split, so we need to return details for each new paddock
                all_3km_watered_areas = []
                all_5km_watered_areas = []
                all_ccs = []# Not used?
                all_potential_ccs = []# Not used?
                # Get length of intersecting planned fences here *************************
                total_required_fencing = self.paddockPlannedFence(pdk_geom)
                for pp in sorted(planned_pdks, key = lambda x: x['Name']):
                    pp_geom = pp.geometry()
                    pp_name = pp['Name']
                    pp_area = pp.geometry().area()# m2
                    pp_cc = pp['AE']
                    pp_potential_cc = pp['Potential AE']
                    pp_no_wpts = self.futureNumWaterPoints(pp_geom)
                    pp_3km_watered_area = self.paddockWateredArea(pp_geom, 3000)
                    all_3km_watered_areas.append(pp_3km_watered_area)
                    pp_3km_watered_pcnt = (pp_3km_watered_area/pp_area)*100
                    pp_5km_watered_area = self.paddockWateredArea(pp_geom, 5000)
                    all_5km_watered_areas.append(pp_5km_watered_area)
                    pp_5km_watered_pcnt = (pp_5km_watered_area/pp_area)*100
                    html_text += f"<h3>{pp_name} (planned)</h3>\
                                <p>Total paddock area (km²) = {round(pp_area/1000000, 3)}</p>\
                                <p>Recommended carrying capacity (AE/yr) = {round(pp_cc, 1)}</p>\
                                <p>Potential carrying capacity (AE/yr) = {round(pp_potential_cc, 1)}</p>\
                                <p>Number of water points = {pp_no_wpts}</p>\
                                <p>3km Watered Area (km² and %) = {round(pp_3km_watered_area/1000000, 3)} | {round(pp_3km_watered_pcnt, 1)}</p>\
                                <p>5km Watered Area (km² and %) = {round(pp_5km_watered_area/1000000, 3)} | {round(pp_5km_watered_pcnt, 1)}</p></br>"
                html_text += f"<h3>Planned paddocks</h3>\
                                <div id='totals'>\
                                <p>Total 3km watered area = {round(sum(all_3km_watered_areas)/1000000, 3)}km²</p>\
                                <p>Total 5km watered area = {round(sum(all_5km_watered_areas)/1000000, 3)}km²</p>\
                                <p>Additional fencing required = {round(total_required_fencing/1000, 3)}km</p>\
                                </div>"
                                
            else:
                #Paddock has not been split, so we just get the additional waterpoints, watered area etc.
                future_paddock_details = self.paddockDetails(paddock_name, 'Future')
                if not future_paddock_details:
                    return
                fp_area = future_paddock_details[0]
                future_cc = future_paddock_details[1]
                fp_no_wpts = future_paddock_details[2]
                fp_3km_watered_area = future_paddock_details[3]
                fp_3km_watered_pcnt = future_paddock_details[4]
                fp_5km_watered_area = future_paddock_details[5]
                fp_5km_watered_pcnt = future_paddock_details[6]
                future_fence_length = future_paddock_details[7]
                html_text += f"<p>Total paddock area (km²) = {round(fp_area/1000000, 3)}</p>\
                        <p>Recommended carrying capacity (AE/yr) = {round(future_cc, 1)}</p>\
                        <p>Number of water points = {fp_no_wpts}</p>\
                        <p>3km Watered Area (km² and %) = {round(fp_3km_watered_area/1000000, 3)} | {round(fp_3km_watered_pcnt, 1)}</p>\
                        <p>5km Watered Area (km² and %) = {round(fp_5km_watered_area/1000000, 3)} | {round(fp_5km_watered_pcnt, 1)}</p>\
                        <p>Length of fencing (km) = {round(future_fence_length/1000, 3)}</p>"
                
                                
            html_text += "</div>"
            html_text += "</body>"
            html_text += "</html>"
            return html_text
        return None
        
    def advancedReportTableHtml(self, paddock_name):
        # Current
        current_pdk_details = self.paddockDetails(paddock_name, 'Current')
        current_area = round(current_pdk_details[0]/1000000, 3)
        current_recommended_cc = round(current_pdk_details[1], 1)
        current_avg_AE = 'TODO'
        current_num_wpts = current_pdk_details[2]
        current_avg_AE_per_wpt = round(current_recommended_cc/current_num_wpts, 1)
        current_wa_3km = round(current_pdk_details[3]/1000000, 3)
        current_wa_3km_pcnt = round(current_pdk_details[4], 2)
        current_wa_3km_info = f'{current_wa_3km}km² | {current_wa_3km_pcnt}%'
        current_wa_5km = round(current_pdk_details[5]/1000000, 3)
        current_wa_5km_pcnt = round(current_pdk_details[6], 2)
        current_wa_5km_info = f'{current_wa_5km}km² | {current_wa_5km_pcnt}%'
        current_wa_stocking_rate = 'TODO'
        current_fencing = round(current_pdk_details[7]/1000, 3)
        current_pipeline = round(current_pdk_details[9]/1000, 3)
        ### Future

        ###
        pdks = [ft for ft in self.pdk_lyr.getFeatures() if ft['Name'] == paddock_name]
        if pdks:
            pdk = pdks[0]
            pdk_geom = pdk.geometry()
            planned_pdks = [p for p in self.pdk_lyr.getFeatures() if p['Status'] == 'Planned' and p.geometry().intersects(pdk_geom)]
            if planned_pdks:
                # The original paddock has been split, so we need to sum & return details for each new paddock
                all_areas = []
                all_ccs = []
                all_wpts = []
                all_3km_wa = []
                all_5km_wa = []
                for pp in sorted(planned_pdks, key = lambda x: x['Name']):
                    pp_name = pp['Name']
                    pp_geom = pp.geometry()
                    all_areas.append(pp_geom.area())
                    all_ccs.append(pp['AE'])
                    all_wpts.append(self.futureNumWaterPoints(pp_geom))
                    all_3km_wa.append(self.plannedWateredArea(pp_geom, 3000))
                    all_5km_wa.append(self.plannedWateredArea(pp_geom, 5000))
                    
                future_area = round(sum(all_areas)/1000000, 3)
                future_recommended_cc = round(sum(all_ccs), 2)
                future_num_wpts = sum(all_wpts)
                future_avg_AE_per_wpt = round(future_recommended_cc/future_num_wpts, 1)
                future_wa_3km = round(sum(all_3km_wa)/1000000, 3)
                future_wa_3km_pcnt = round(sum(all_3km_wa)/future_area*100, 1)
                future_wa_3km_info = f'{future_wa_3km}km² | {future_wa_3km_pcnt}%'
                future_wa_5km = round(sum(all_5km_wa)/1000000, 3)
                future_wa_5km_pcnt = round(sum(all_5km_wa)/future_area*100, 1)
                future_wa_5km_info = f'{future_wa_5km}km² | {future_wa_5km_pcnt}%'
            else:
                #Paddock has not been split, so we just get the additional waterpoints, watered area etc.
                future_pdk_details = self.paddockDetails(paddock_name, 'Future')
                if not future_pdk_details:
                    return
                future_area = round(future_pdk_details[0]/1000000, 3)
                future_recommended_cc = round(future_pdk_details[1], 1)
                future_num_wpts = future_pdk_details[2]
                future_avg_AE_per_wpt = round(future_recommended_cc/future_num_wpts, 1)
                future_wa_3km = round(future_pdk_details[3]/1000000, 3)
                future_wa_3km_pcnt = round(future_pdk_details[4], 2)
                future_wa_3km_info = f'{future_wa_3km}km² | {future_wa_3km_pcnt}%'
                future_wa_5km = round(future_pdk_details[5]/1000000, 3)
                future_wa_5km_pcnt = round(future_pdk_details[6], 2)
                future_wa_5km_info = f'{future_wa_5km}km² | {future_wa_5km_pcnt}%'
                future_wa_stocking_rate = 'TODO'
            # planned_fencing = round(current_pdk_details[8]/1000, 3)
            total_future_fencing = round((current_pdk_details[7]+current_pdk_details[8])/1000, 3)
            planned_fencing = round(total_future_fencing - current_fencing, 3)
            current_pipeline = round(current_pdk_details[9]/1000, 3)# Only Built Pipelines
            future_pipeline = round(current_pdk_details[10]/1000, 3)# Only Planned Pipelines
            total_future_pipeline = round(current_pipeline + future_pipeline, 3)
                
        
        #Differences
        area_diff = round(future_area - current_area, 3)
        area_sign = self.sign(current_area, future_area)
        cc_diff = round(future_recommended_cc - current_recommended_cc, 2)
        cc_sign = self.sign(current_recommended_cc, future_recommended_cc)
        wpt_diff = future_num_wpts - current_num_wpts
        wpt_sign = self.sign(current_num_wpts, future_num_wpts)
        avg_AE_per_wpt_diff = round(future_avg_AE_per_wpt - current_avg_AE_per_wpt, 2)
        avg_AE_per_wpt_sign = self.sign(current_avg_AE_per_wpt, future_avg_AE_per_wpt)
        wa_3km_diff = round(future_wa_3km - current_wa_3km, 2)
        wa_3km_pcnt_diff = round(future_wa_3km_pcnt - current_wa_3km_pcnt, 2)
        wa_3km_diff_info = f'{wa_3km_diff}km² | {wa_3km_pcnt_diff}%'
        wa_3km_sign = self.sign(current_wa_3km, future_wa_3km)
        wa_5km_diff = round(future_wa_5km - current_wa_5km)
        wa_5km_pcnt_diff = round(future_wa_5km_pcnt - current_wa_5km_pcnt, 2)
        wa_5km_diff_info = f'{wa_5km_diff}km² | {wa_5km_pcnt_diff}%'
        wa_5km_sign = self.sign(current_wa_5km, future_wa_5km)
                
        
        html_text = "<table>"
        html_text+="<tr><th>Paddock Development Proposal</th><th>Current</th><th>Proposed</th><th>Difference +/-</th></tr>"
        html_text+=f"<tr><td>Total paddock area</td><td>{current_area}km²</td><td>{future_area}km²</td><td>{area_sign}{area_diff}km²</td></tr>"
        html_text+=f"<tr><td>Recommended carrying capacity</td><td>{current_recommended_cc}AE/yr</td><td>{future_recommended_cc}AE/yr</td><td>{cc_sign}{cc_diff}AE/yr</td></tr>"
        # html_text+=f"<tr><td>Average adult equivalents carried now and planned for proposed development</td><td>{current_avg_AE}</td><td>B</td><td>C</td></tr>"
        html_text+=f"<tr><td>Number of water points in paddock</td><td>{current_num_wpts}</td><td>{future_num_wpts}</td><td>{wpt_sign}{wpt_diff}</td></tr>"
        html_text+=f"<tr><td>Average number of AE/water point</td><td>{current_avg_AE_per_wpt}</td><td>{future_avg_AE_per_wpt}</td><td>{avg_AE_per_wpt_sign}{avg_AE_per_wpt_diff}</td></tr>"
        html_text+=f"<tr><td>3km watered area</td><td>{current_wa_3km_info}</td><td>{future_wa_3km_info}</td><td>{wa_3km_sign}{wa_3km_diff_info}</td></tr>"
        html_text+=f"<tr><td>5km watered area</td><td>{current_wa_5km_info}</td><td>{future_wa_5km_info}</td><td>{wa_5km_sign}{wa_5km_diff_info}</td></tr>"
        # html_text+=f"<tr><td>Watered area stocking rate</td><td>{current_wa_stocking_rate} AE/km²</td><td>B</td><td>C</td></tr>"
        html_text+=f"<tr><td>Length of fencing (including terrain)</td><td>{current_fencing}km</td><td>{total_future_fencing}km</td><td>{self.sign(current_fencing, total_future_fencing)}{planned_fencing}km</td></tr>"
        html_text+=f"<tr><td>Length of pipeline (including terrain)</td><td>{current_pipeline}km</td><td>{total_future_pipeline}km</td><td>{self.sign(current_pipeline, total_future_pipeline)}{future_pipeline}km</td></tr>"
        html_text+="</table>"
        html_text+="</body></html>"
        html_text+="<style>\
                    table, th, td {border:1px solid black;}\
                    </style>"
        return html_text

##############################################################################
        
    def showPreview(self):
        #####BASIC REPORT TEMPLATE#####
        development_name = self.titleEdit.text()
        paddock_name = self.paddocksComboBox.currentText()
        if self.basicReportRadioButton.isChecked():
            basic_html = self.basicReportHtml(paddock_name, development_name)
            self.view.setHtml(basic_html)
        #####ADVANCED REPORT TEMPLATE#####
        elif self.advancedReportRadioButton.isChecked():
            advanced_html = "<html>"
            advanced_html+="<body>"
            advanced_html+="<h1>"
            advanced_html+="Paddock Power Investment Calculator Data"
            advanced_html+="</h1><br>"
            advanced_html += self.advancedReportTableHtml(paddock_name)
            
            # Create image tag for current layers
            current_layers = self.currentMapLayers(paddock_name)
            current_layers_ordered = [current_layers[2], current_layers[1], current_layers[0]]
            # print(current_layers_ordered)
            settings = QgsMapSettings()
            settings.setOutputDpi(350)
            settings.setLayers(current_layers_ordered)
            full_extent = settings.fullExtent()
            longest_dim = max([full_extent.width(), full_extent.height()])
            grow_factor = longest_dim/25
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
            grow_factor = longest_dim/25
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

            advanced_html+="<div class=\"image-div\">"
            advanced_html+=img_tag1
            advanced_html+=img_tag2
            advanced_html+="</div>"
            advanced_html+= "</body>\
                            </html>"
            advanced_html+= "<style>\
                        img{border: 5px solid #555;}\
                        </style>"
#            print(html_text)
            self.view.setHtml(advanced_html)


    def exportToPdf(self):
        pass
#            pdf_path = 'C:\\Users\\qw2\\Desktop\\MLA-PP\\Test_PDF\\BBB_test_report.pdf'
#            printer = QPrinter()
##            page_layout = QPageLayout()
##            page_layout.setPageSize(QPageSize(QPageSize.A4))
##            page_layout.setOrientation(QPageLayout.Landscape)
##            printer.setPageLayout(page_layout)
#            printer.setOrientation(QPrinter.Landscape)
#            printer.setOutputFormat(QPrinter.PdfFormat)
#            printer.setOutputFileName(pdf_path)
###          Here we want to 'print' the QWebView instead of the QTextDocument
###          Research how
#            txt_doc.print_(printer)

    def css(self):
        #This is not being used (using in line style)
        return 'body{background-color: gray;}\
                img{border: 5px solid black;}'

########################################################################################################
        
dlg = ExportToPdfDialog()
dlg.show()