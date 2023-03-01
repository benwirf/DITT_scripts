from qgis.PyQt.QtCore import QCoreApplication, QVariant
from qgis.core import (QgsField,
                        QgsProject,
                        QgsProcessing,
                        QgsProcessingAlgorithm,
                        QgsProcessingParameterFeatureSource,
                        QgsProcessingParameterField,
                        QgsProcessingParameterLayout,
                        QgsProcessingParameterEnum)
                       
class AddLayoutTable(QgsProcessingAlgorithm):
    INPUT_LAYER = 'INPUT_LAYER'
    INPUT_FIELDS = 'INPUT_FIELDS'
    LAYOUT = 'LAYOUT'
 
    def __init__(self):
        super().__init__()
 
    def name(self):
        return "addlayouttable"
         
    def displayName(self):
        return "Add layout table"
 
    def group(self):
        return "General"
 
    def groupId(self):
        return "general"
 
    def shortHelpString(self):
        return "Add a table to a print layout, showing attributes from\
        selected fields in a vector layer. E.g. Land Systems/ Units."
 
    def helpUrl(self):
        return "https://qgis.org"
         
    def createInstance(self):
        return type(self)()
        
    def flags(self):
        return super().flags() | QgsProcessingAlgorithm.FlagNoThreading
   
    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterFeatureSource(
            self.INPUT_LAYER,
            "Input layer",
            [QgsProcessing.TypeVector]))
            
        self.addParameter(QgsProcessingParameterField(
            self.INPUT_FIELDS,
            "Fields to add as table columns",
            parentLayerParameterName=self.INPUT_LAYER,
            allowMultiple=True,
            defaultToAllFields=True))
        
        project_layouts = QgsProject.instance().layoutManager().layouts()
        if project_layouts:
            default_layout = project_layouts[0].name()
        else:
            default_layout = ''
                        
        layout_param = QgsProcessingParameterLayout(
            self.LAYOUT,
            "Layout",
            defaultValue=default_layout)
            
        self.addParameter(layout_param)
        
    def processAlgorithm(self, parameters, context, feedback):
        src_lyr = self.parameterAsSource(parameters, self.INPUT_LAYER, context)
        flds = self.parameterAsFields(parameters, self.INPUT_FIELDS, context)
        layout = self.parameterAsString(parameters, self.LAYOUT, context)
 
        return {self.INPUT_LAYER: src_lyr,
                self.INPUT_FIELDS: flds,
                self.LAYOUT: layout}