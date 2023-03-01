from processing.gui.wrappers import WidgetWrapper

from qgis.PyQt.QtCore import (QCoreApplication,
                                QVariant,
                                Qt)
                                
from qgis.PyQt.QtWidgets import (QWidget,
                                QListWidget,
                                QTableWidget,
                                QVBoxLayout,
                                QListWidgetItem,
                                QTableWidgetItem)
                                
from qgis.core import (QgsField,
                        QgsProject,
                        QgsProcessing,
                        QgsProcessingAlgorithm,
                        QgsProcessingParameterVectorLayer,
                        QgsProcessingParameterField,
                        QgsProcessingParameterMatrix,
                        QgsProcessingParameterString,
                        QgsMapLayerProxyModel)
                        
from qgis.gui import QgsMapLayerComboBox
                       
class AddLayoutTable(QgsProcessingAlgorithm):
    INPUT_LAYER = 'INPUT_LAYER'
    INPUT_FIELDS = 'INPUT_FIELDS'
    LAYOUT = 'LAYOUT'
 
    def __init__(self):
        super().__init__()
 
    def name(self):
        return "testwidgetwrapper"
         
    def displayName(self):
        return "Test Widget Wrapper"
 
    def group(self):
        return "General"
 
    def groupId(self):
        return "general"
 
    def shortHelpString(self):
        return "Test a custom widget wrapper."
 
    def helpUrl(self):
        return "https://qgis.org"
         
    def createInstance(self):
        return type(self)()
   
    def initAlgorithm(self, config=None):
        test_param = QgsProcessingParameterMatrix('TEST_MATRIX', 'Test Matrix')
        test_param.setMetadata({'widget_wrapper': {'class': CustomParametersWidget}})
        self.addParameter(test_param)
        

    def processAlgorithm(self, parameters, context, feedback):
        test_string = self.parameterAsMatrix(parameters, 'TEST_STRING', context)
 
        return {}
        
class CustomParametersWidget(WidgetWrapper):

    def createWidget(self):
        self.cpw = MyWidget()
        return self.cpw
        
    def value(self):
        self.lyr = self.cpw.getLayer()
        self.flds = self.cpw.getFields()
        self.col_hdrs = self.cpw.getLayoutTableHeaders()
        return [self.lyr, self.flds, self.col_hdrs]

        
class MyWidget(QWidget):
    
    def __init__(self):
        super(MyWidget, self).__init__()
        self.setGeometry(500, 500, 500, 500)
        self.lyr_cb = QgsMapLayerComboBox(self)
        self.lyr_cb.setFilters(QgsMapLayerProxyModel.VectorLayer)
        self.lyr_cb.layerChanged.connect(self.populateListWidget)
        self.lw = QListWidget(self)
        self.lw.itemChanged.connect(self.fieldSelectionChanged)
        self.tbl = QTableWidget(self)
        layout = QVBoxLayout()
        layout.addWidget(self.lyr_cb)
        layout.addWidget(self.lw)
        layout.addWidget(self.tbl)
        self.setLayout(layout)
        self.populateListWidget()
        self.setUpTable()
    
    def populateListWidget(self):
        self.lw.clear()
        list_items = [f.name() for f in self.lyr_cb.currentLayer().fields()]
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
        return [self.tbl.item(i, 1).text() for i in range(self.tbl.rowCount())]
        
        