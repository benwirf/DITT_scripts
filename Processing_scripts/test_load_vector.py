from qgis.PyQt.QtCore import QCoreApplication, QVariant
from qgis.core import (QgsFields, QgsField, QgsVectorLayer,
                        QgsProcessing, QgsProcessingAlgorithm,
                        QgsProcessingParameterFile,
                        QgsWkbTypes, QgsCoordinateReferenceSystem,
                        QgsProcessingContext)
                      
class ExampleAlgorithm(QgsProcessingAlgorithm):
    INPUT = 'INPUT'
    OUTPUT = 'OUTPUT'

    def __init__(self):
        super().__init__()

    def name(self):
        return "create_empty_layer"
    
    def tr(self, text):
        return QCoreApplication.translate("Processing", text)
        
    def displayName(self):
        return self.tr("Create empty layer")

    def group(self):
        return self.tr("Examples")

    def groupId(self):
        return "examples"

    def shortHelpString(self):
        return self.tr("Creates an empty layer and adds it to a new group")

    def helpUrl(self):
        return "https://qgis.org"
        
    def createInstance(self):
        return ExampleAlgorithm()
  
    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterFile(
            self.INPUT,
            self.tr("Source file"),
            behavior=QgsProcessingParameterFile.File))

    def processAlgorithm(self, parameters, context, feedback):
        uri = self.parameterAsString(parameters, self.INPUT, context)
        vl = QgsVectorLayer(uri, 'Test Layer', 'ogr')
        feedback.pushInfo(repr(vl.isValid()))
        if vl.isValid():
            context.temporaryLayerStore().addMapLayer(vl)
            context.addLayerToLoadOnCompletion(vl.id(), QgsProcessingContext.LayerDetails(vl.name(),
                                                                                        context.project(),
                                                                                        vl.name()))

        return {self.OUTPUT: vl.id()}
        
