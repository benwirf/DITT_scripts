from qgis.PyQt.QtCore import QCoreApplication, QVariant
from qgis.PyQt.QtWidgets import QDialog, QTabWidget
from qgis.core import (QgsProcessing, QgsProcessingAlgorithm,
                        QgsProcessingParameterVectorLayer,
                        QgsProcessingParameterFileDestination)

from qgis.utils import iface
import csv


class ExportColorMapToCsv(QgsProcessingAlgorithm):
    LAYER = 'LAYER'
    COLUMN_HEADERS = 'COLUMN_HEADERS'
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
                The CSV will contain the renderer class values, hex codes and\
                RGB values of the associated category colors."
 
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
            
        self.addParameter(QgsProcessingParameterFileDestination(
            self.OUTPUT_CSV_PATH,
            "Output CSV file",
            "*.csv"))

 
    def processAlgorithm(self, parameters, context, feedback):
        layer = self.parameterAsVectorLayer(parameters, self.LAYER, context)
        result_csv = self.parameterAsFileOutput(parameters, self.OUTPUT_CSV_PATH, context)
        ################################
        csv_tbl = open(result_csv, mode='w', newline='')
        writer = csv.writer(csv_tbl)
        r = layer.renderer()
        if not isinstance(r, QgsCategorizedSymbolRenderer):
            return {}
        class_attribute = r.classAttribute()
        writer.writerow([class_attribute, 'Hex Code', 'RGB Values'])
        for cat in r.categories():
            ls = cat.value()
            col = cat.symbol().color()
            hex_code = col.name()
            writer.writerow([ls, hex_code])
        csv_tbl.close()
        ################################
 
        return {'Color map CSV': result_csv}
        
    def postProcessAlgorithm(self, context, feedback):
        # hack to work around ?bug where, if algorithm returns the NoThreading flag,
        # the dialog reverts to the Parameters tab instead of showing the Log tab with results
        alg_dlg = [d for d in iface.mainWindow().findChildren(QDialog)if d.objectName() == 'QgsProcessingDialogBase' and d.isVisible()]
        tab_widg = alg_dlg[0].findChildren(QTabWidget)
        current_tab = tab_widg[0].currentIndex()
        if current_tab == 0:
            tab_widg[0].setCurrentIndex(1)
        return {}
        