from qgis.PyQt.QtCore import QCoreApplication, QVariant, Qt

from qgis.PyQt.QtWidgets import (QWidget, QVBoxLayout, QLabel, QDialog,
                                QTableWidget, QComboBox, QTableWidgetItem,
                                QTabWidget)
                                
from qgis.PyQt.QtGui import QBrush, QColor

from qgis.core import (QgsProcessing, QgsProcessingAlgorithm,
                        QgsProcessingParameterMatrix,
                        QgsProcessingParameterVectorLayer,
                        QgsProcessingParameterField,
                        QgsProcessingParameterEnum,
                        QgsStyle, QgsSymbol,
                        QgsRendererCategory,
                        QgsCategorizedSymbolRenderer)
                        
from qgis.gui import QgsFileWidget

from qgis.utils import iface
                        
from processing.gui.wrappers import WidgetWrapper
from collections import OrderedDict
import csv
import re

                       
class CategoriseLayerFromCsv(QgsProcessingAlgorithm):
    PARAMS = 'PARAMS'
    LAYER = 'LAYER'
    FIELD = 'FIELD'
    SORT_BEHAVIOUR = 'SORT_BEHAVIOUR'
    
    sort_options = ['Sort categories alphabetically', 'keep order from .csv file']
 
    def __init__(self):
        super().__init__()
 
    def name(self):
        return "categorisefromcsv"
         
    def displayName(self):
        return "Categorise layer from CSV"
 
    def group(self):
        return "General"
 
    def groupId(self):
        return "general"
 
    def shortHelpString(self):
        return "Apply a categorised renderer to a vector layer\
                e.g. Land Systems with colours\
                loaded from a csv file containing hex codes and unique\
                values found in a classification field."
 
    def helpUrl(self):
        return "https://qgis.org"
         
    def createInstance(self):
        return type(self)()
        
    def flags(self):
        return super().flags() | QgsProcessingAlgorithm.FlagNoThreading
   
    def initAlgorithm(self, config=None):
        source_params = QgsProcessingParameterMatrix(self.PARAMS, 'Color map')
        source_params.setMetadata({'widget_wrapper': {'class': CustomParametersWidgetWrapper}})
        self.addParameter(source_params)
        #########################################################
        self.addParameter(QgsProcessingParameterVectorLayer(
            self.LAYER,
            "Input layer",
            [QgsProcessing.TypeVectorAnyGeometry]))
        
        self.addParameter(QgsProcessingParameterField(self.FIELD,
            'Field containing values for classification',
            parentLayerParameterName = self.LAYER,
            type = QgsProcessingParameterField.String))
            
        self.addParameter(QgsProcessingParameterEnum(
            self.SORT_BEHAVIOUR,
            "",
            self.sort_options, defaultValue=1))
            
        self.parameterDefinition(self.SORT_BEHAVIOUR).setMetadata({
            'widget_wrapper': {
                'useCheckBoxes': True,
                'columns': 2}})
             
    def processAlgorithm(self, parameters, context, feedback):
        param_list = self.parameterAsMatrix(parameters, self.PARAMS, context)
        color_map = param_list[0]
        layer = self.parameterAsVectorLayer(parameters, self.LAYER, context)
        cat_fld = self.parameterAsFields(parameters, self.FIELD, context)[0]
        sort_behaviour = self.parameterAsEnum(parameters, self.SORT_BEHAVIOUR, context)
        ###############################################

        default_style = QgsStyle().defaultStyle()

        field_index = layer.fields().lookupField(cat_fld)
        if sort_behaviour == 0:# Sort aplphabetically
            cat_values = sorted(color_map.keys())
        if sort_behaviour == 1:# Keep order in csv
            cat_values = color_map.keys()
        
        categories = []
        for value in cat_values:
            symbol = QgsSymbol.defaultSymbol(layer.geometryType())
            col_hex = color_map[value]
            qcol = QColor(col_hex)
            symbol.setColor(qcol)
            category = QgsRendererCategory(value, symbol, str(value))
            categories.append(category)

        renderer = QgsCategorizedSymbolRenderer(cat_fld, categories) 
        layer.setRenderer(renderer)
        layer.triggerRepaint()
        ###############################################

        return {'Color Map': color_map}
        
    def postProcessAlgorithm(self, context, feedback):
        # hack to work around ?bug where, if algorithm returns the NoThreading flag,
        # the dialog reverts to the Parameters tab instead of showing the Log tab with results
        alg_dlg = [d for d in iface.mainWindow().findChildren(QDialog)if d.objectName() == 'QgsProcessingDialogBase' and d.isVisible()]
        tab_widg = alg_dlg[0].findChildren(QTabWidget)
        current_tab = tab_widg[0].currentIndex()
        if current_tab == 0:
            tab_widg[0].setCurrentIndex(1)
        return {}

class CustomParametersWidgetWrapper(WidgetWrapper):

    def createWidget(self):
        self.cpw = ClassifyFromCsvWidget()
        return self.cpw
        
    def value(self):
        self.color_map = OrderedDict((k, v) for k, v in self.cpw.color_map().items())
        return [self.color_map]
        
class ClassifyFromCsvWidget(QWidget):
    def __init__(self):
        super(ClassifyFromCsvWidget, self).__init__()
        self.main_layout = QVBoxLayout(self)
        self.setMinimumWidth(600)
        
        self.file_label = QLabel('Select colour map file (.csv)', self)
        self.file_widget = QgsFileWidget(self)
        self.file_widget.setStorageMode(QgsFileWidget.GetFile)
        self.file_widget.setFilter('*.csv')
        
        self.table_label = QLabel('File data', self)
        self.table_widget = QTableWidget(self)
        
        self.color_cb_label = QLabel('CSV column containing color hexcode', self)
        self.color_column_cb = QComboBox(self)
        
        self.class_val_label = QLabel('CSV column containing unique classification values', self)
        self.class_val_cb = QComboBox(self)
        
        self.main_layout.addWidget(self.file_label)
        self.main_layout.addWidget(self.file_widget)
        self.main_layout.addWidget(self.table_label)
        self.main_layout.addWidget(self.table_widget)
        self.main_layout.addWidget(self.color_cb_label)
        self.main_layout.addWidget(self.color_column_cb)
        self.main_layout.addWidget(self.class_val_label)
        self.main_layout.addWidget(self.class_val_cb)
        
        self.file_widget.fileChanged.connect(self.populate_sample)
        
    def populate_sample(self, f_path):
        csv_file = open(f_path)
        csv_reader = csv.reader(csv_file, delimiter=',')
        csv_rows = [row for row in csv_reader]
        
        table_row_count = len(csv_rows)
        table_col_count = len(csv_rows[0])
        
        self.table_widget.setColumnCount(table_col_count)
        hdr_items = [csv_rows[0][i] for i in range(table_col_count)]
        self.table_widget.setHorizontalHeaderLabels(hdr_items)
        self.table_widget.setRowCount(table_row_count-1)
        cols_to_resize = []
        color_col_idx = None
        for i in range(1, table_row_count):
            for j in range(table_col_count):
                cell_item = QTableWidgetItem(csv_rows[i][j])
                if re.match('#[a-zA-Z0-9]+$', csv_rows[i][j]):
                    color_col_idx = j
                    cell_brush = QBrush()
                    cell_brush.setStyle(Qt.SolidPattern)
                    cell_brush.setColor(QColor(csv_rows[i][j]))
                    cell_item.setBackground(cell_brush)
                    cell_item.setTextAlignment(Qt.AlignCenter)
                else:
                    cols_to_resize.append(j)
                self.table_widget.setItem(i-1, j, cell_item)
                
        for x in cols_to_resize:
            self.table_widget.resizeColumnToContents(x)
        
        self.color_column_cb.clear()
        self.color_column_cb.addItems(hdr_items)
        if color_col_idx:
            self.color_column_cb.setCurrentIndex(color_col_idx)
        
        self.class_val_cb.clear()
        self.class_val_cb.addItems(hdr_items)
            
    def color_map(self):
        color_map = {}
        hdr_labels = [self.table_widget.horizontalHeaderItem(i).text() for i in range(self.table_widget.columnCount())]
        if not hdr_labels:
            return color_map
        uv_col_idx = hdr_labels.index(self.class_val_cb.currentText())
        c_col_idx = hdr_labels.index(self.color_column_cb.currentText())
        for i in range(self.table_widget.rowCount()):
            color_map[self.table_widget.item(i, uv_col_idx).text()] = self.table_widget.item(i, c_col_idx).text()

        return color_map
        