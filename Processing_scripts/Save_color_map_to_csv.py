from qgis.PyQt.QtCore import QCoreApplication, QVariant
from qgis.core import (QgsProcessing, QgsProcessingAlgorithm,
                        QgsProcessingParameterVectorLayer,
                        QgsProcessingParameterFileDestination)

import csv


class ExportColorMapToCsv(QgsProcessingAlgorithm):
    LAYER = 'LAYER'
    OUTPUT_CSV_PATH = 'OUTPUT_CSV_PATH'
 
    def __init__(self):
        super().__init__()
 
    def name(self):
        return "exportcolormaptocsv"
         
    def displayName(self):
        return "Export color map to CSV"
 
    def group(self):
        return "General"
 
    def groupId(self):
        return "general"
 
    def shortHelpString(self):
        return "Export a color map from a categorised vector layer to a CSV file\
                The CSV will contain the renderer legend labels and the hex codes\
                of the associated category colors."
 
    def helpUrl(self):
        return "https://qgis.org"
         
    def createInstance(self):
        return type(self)()
        
    def flags(self):
        return super().flags() | QgsProcessingAlgorithm.FlagNoThreading
   
    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterVectorLayer(
            self.LAYER,
            "Input layer",
            [QgsProcessing.TypeVectorAnyGeometry]))
            
        self.addParameter()

 
    def processAlgorithm(self, parameters, context, feedback):
        layer = self.parameterAsVectorLayer(parameters, self.LAYER, context)
 
 
        return {}
        
    def postProcessAlgorithm(self, context, feedback):
        # hack to work around ?bug where, if algorithm returns the NoThreading flag,
        # the dialog reverts to the Parameters tab instead of showing the Log tab with results
        alg_dlg = [d for d in iface.mainWindow().findChildren(QDialog)if d.objectName() == 'QgsProcessingDialogBase' and d.isVisible()]
        tab_widg = alg_dlg[0].findChildren(QTabWidget)
        current_tab = tab_widg[0].currentIndex()
        if current_tab == 0:
            tab_widg[0].setCurrentIndex(1)
        return {}
        