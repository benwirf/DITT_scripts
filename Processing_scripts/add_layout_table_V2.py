from processing.gui.wrappers import WidgetWrapper

from qgis.PyQt.QtCore import (QCoreApplication,
                                QVariant,
                                Qt)
                                
from qgis.PyQt.QtWidgets import (QWidget,
                                QLabel,
                                QListWidget,
                                QTableWidget,
                                QVBoxLayout,
                                QListWidgetItem,
                                QTableWidgetItem)
                                
from qgis.core import (QgsField,
                        QgsProject,
                        QgsProcessing,
                        QgsProcessingAlgorithm,
                        QgsProcessingParameterMatrix,
                        QgsProcessingParameterLayout,
                        QgsProcessingParameterBoolean,
                        QgsProcessingParameterEnum,
                        QgsMapLayerProxyModel,
                        QgsTableCell,
                        QgsLayoutItemManualTable,
                        QgsLayoutFrame,
                        QgsLayoutSize,
                        QgsRenderContext)
                        
from qgis.gui import QgsMapLayerComboBox

from qgis.utils import iface
                       
class AddLayoutTable(QgsProcessingAlgorithm):
    INPUT_PARAMETERS = 'INPUT_PARAMETERS'
    LAYOUT = 'LAYOUT'
    ADD_SYMBOL_COLUMN = 'ADD_SYMBOL_COLUMN'
    OPTIONAL_AREA_COLUMNS = 'OPTIONAL_AREA_COLUMNS'
    
    area_column_options = ['Area m2', 'Area ha', 'Area km2']
 
    def __init__(self):
        super().__init__()
 
    def name(self):
        return "addtabletolayout"
         
    def displayName(self):
        return "Add Table To Layout"
 
    def group(self):
        return "General"
 
    def groupId(self):
        return "general"
 
    def shortHelpString(self):
        return "Add a custom table of field values and derived attributes\
        to a print layout."
 
    def helpUrl(self):
        return "https://qgis.org"
         
    def createInstance(self):
        return type(self)()
        
    def flags(self):
        return super().flags() | QgsProcessingAlgorithm.FlagNoThreading
        
    def checkParameterValues(self, parameters, context):
        input_layer_name = parameters[self.INPUT_PARAMETERS][0]
        input_layer = context.project().mapLayersByName(input_layer_name)
        if not input_layer:
            return (False, 'Missing parameter value for Input layer')
        if input_layer.featureCount()>50:
            return(False, 'Input layer has more than 50 features; resulting\
                            table will be large! You may wish to dissolve\
                            input layer before proceeding.')
        if (input_layer[0].geometryType() != 2) and (parameters[self.OPTIONAL_AREA_COLUMNS]):
            return (False, 'Area values can only be calculated for polygon layers')
        return (True, '')
   
    def initAlgorithm(self, config=None):
        source_params = QgsProcessingParameterMatrix(self.INPUT_PARAMETERS, 'Input parameters')
        source_params.setMetadata({'widget_wrapper': {'class': CustomParametersWidgetWrapper}})
        self.addParameter(source_params)
        
        self.addParameter(QgsProcessingParameterLayout(self.LAYOUT, 'Print layout to add table'))
        
        self.addParameter(QgsProcessingParameterBoolean(self.ADD_SYMBOL_COLUMN, 'Add symbol color column?'))
        
        self.addParameter(QgsProcessingParameterEnum(self.OPTIONAL_AREA_COLUMNS,
                                                        'Calculate area attributes (polygon layers only)',
                                                        self.area_column_options,
                                                        allowMultiple=True,
                                                        optional=True))

    def processAlgorithm(self, parameters, context, feedback):
        # parse all input parameters***********************************
        source_param_array = self.parameterAsMatrix(parameters, self.INPUT_PARAMETERS, context)
        
        lyr_name = source_param_array[0]
        fld_arr = source_param_array[1]
        hdr_map = source_param_array[2]
        
        layout_name = self.parameterAsString(parameters, self.LAYOUT, context)
        
        add_symbol_column = self.parameterAsBool(parameters, self.ADD_SYMBOL_COLUMN, context)
        
        area_columns = self.parameterAsEnums(parameters, self.OPTIONAL_AREA_COLUMNS, context)
        #**************************************************************
        lyr = context.project().mapLayersByName(lyr_name)[0]
        
        header_strings = [hdr_map[k] for k in fld_arr]
        
        header_row = [QgsTableCell(v) for v in header_strings]
        
        if add_symbol_column:
            header_row.insert(0, QgsTableCell('Symbol'))
        
        tbl_rows = [header_row]

        if add_symbol_column:
            canvas = iface.mapCanvas()
            settings = canvas.mapSettings()
            render_context = QgsRenderContext.fromMapSettings(settings)
            renderer = lyr.renderer()
            renderer.startRender(render_context, lyr.fields())
        
        for f in lyr.getFeatures():
            tbl_row = []
            if add_symbol_column:
                symbol = renderer.symbolForFeature(f, render_context)
                symbol_color = symbol.color()
                symbol_cell = QgsTableCell()
                symbol_cell.setBackgroundColor(symbol_color)
                tbl_row.append(symbol_cell)
            for fld in fld_arr:
                tbl_row.append(QgsTableCell(f[fld]))
            tbl_rows.append(tbl_row)
        
        if add_symbol_column:
            renderer.stopRender(render_context)
            
        l = context.project().layoutManager().layoutByName(layout_name)
        t = QgsLayoutItemManualTable.create(l)
        l.addMultiFrame(t)
        t.setTableContents(tbl_rows)

        # Base class for frame items, which form a layout multiframe item.
        frame = QgsLayoutFrame(l, t)
        frame.attemptResize(QgsLayoutSize(150, 100), True)
        t.addFrame(frame)

        l.refresh()
         
        return {'layer': lyr,
                'rows': tbl_rows,
                'layout': l}

        
class CustomParametersWidgetWrapper(WidgetWrapper):

    def createWidget(self):
        self.cpw = CustomParametersWidget()
        return self.cpw
        
    def value(self):
        self.lyr = self.cpw.getLayer()
        self.flds = self.cpw.getFields()
        self.col_hdrs = self.cpw.getLayoutTableHeaders()
        return [self.lyr, self.flds, self.col_hdrs]

        
class CustomParametersWidget(QWidget):
    
    def __init__(self):
        super(CustomParametersWidget, self).__init__()
        self.lyr_lbl = QLabel('Input layer', self)
        self.lyr_cb = QgsMapLayerComboBox(self)
        self.lyr_cb.setFilters(QgsMapLayerProxyModel.VectorLayer)
        self.lyr_cb.layerChanged.connect(self.populateListWidget)
        self.fld_lbl = QLabel("Fields to add as table columns", self)
        self.lw = QListWidget(self)
        self.lw.itemChanged.connect(self.fieldSelectionChanged)
        self.tbl_lbl = QLabel('Enter table column headers')
        self.tbl = QTableWidget(self)
        layout = QVBoxLayout()
        layout.addWidget(self.lyr_lbl)
        layout.addWidget(self.lyr_cb)
        layout.addWidget(self.fld_lbl)
        layout.addWidget(self.lw)
        layout.addWidget(self.tbl_lbl)
        layout.addWidget(self.tbl)
        self.setLayout(layout)
        self.populateListWidget()
        self.setUpTable()
    
    def populateListWidget(self):
        self.lw.clear()
        current_lyr = self.lyr_cb.currentLayer()
        if not current_lyr:
            return
        list_items = [f.name() for f in current_lyr.fields()]
        if list:
            for fld in list_items:
                li = QListWidgetItem(fld)
                li.setFlags(li.flags() | Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
                li.setCheckState(Qt.Unchecked)
                self.lw.addItem(li)
        self.fieldSelectionChanged()
    
    def setUpTable(self):
        self.tbl.setColumnCount(2)
        self.tbl.setHorizontalHeaderLabels(['Field Name', 'Alias'])
        
    def fieldSelectionChanged(self):
        checked_items = [self.lw.item(i) for i in range(self.lw.count()) if self.lw.item(i).checkState() == Qt.Checked]
        self.tbl.setRowCount(len(checked_items))
        for current, item in enumerate(checked_items):
            tbl_item = QTableWidgetItem(item.text())
            self.tbl.setItem(current, 0, tbl_item)
            
    def getLayer(self):
        return self.lyr_cb.currentLayer().name()
        
    def getFields(self):
        return [self.lw.item(i).text() for i in range(self.lw.count()) if self.lw.item(i).checkState() == Qt.Checked]
        
    def getLayoutTableHeaders(self):
        header_map = {}
        for i in range(self.tbl.rowCount()):
            cell1 = self.tbl.item(i, 0)
            if cell1:
                fld_name = cell1.text()
            else:
                fld_name = ''
            cell2 = self.tbl.item(i, 1)
            if cell2:
                fld_alias = cell2.text()
            else:
                fld_alias = ''
            header_map[fld_name] = fld_alias
        return header_map