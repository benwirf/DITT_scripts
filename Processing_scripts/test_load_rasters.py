from qgis.PyQt.QtCore import QCoreApplication, QVariant
from qgis.core import (QgsProcessing, QgsProcessingAlgorithm,
                        QgsProcessingParameterFile,
                        QgsRasterLayer)

import os
                       
class LoadRasters(QgsProcessingAlgorithm):
    INPUT_FOLDER = 'INPUT_FOLDER'
    OUTPUT_LAYERS = 'OUTPUT_LAYERS'
    outputLayers = []

    def __init__(self):
        super().__init__()
 
    def name(self):
        return "load_rasters"
     
    def tr(self, text):
        return QCoreApplication.translate("load_rasters", text)
         
    def displayName(self):
        return self.tr("Load rasters")
 
    def group(self):
        return self.tr("Examples")
 
    def groupId(self):
        return "examples"
 
    def shortHelpString(self):
        return self.tr("Load multiple raster layers")
 
    def helpUrl(self):
        return "https://qgis.org"
         
    def createInstance(self):
        return type(self)()
        
#    def flags(self):
#        return super().flags() | QgsProcessingAlgorithm.FlagNoThreading
   
    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterFile(
            self.INPUT_FOLDER,
            self.tr("Source directory"),
            behavior=QgsProcessingParameterFile.Folder))
 
    def processAlgorithm(self, parameters, context, feedback):
        source_folder = self.parameterAsString(parameters, self.INPUT_FOLDER, context)

        for file in os.scandir(source_folder):
            file_name = file.name.split('.')[0]
            file_path = os.path.join(source_folder, file.name)
            rl = QgsRasterLayer(file_path, file_name, 'gdal')
            if rl.isValid():
                self.outputLayers.append(rl)
        
        return {self.OUTPUT_LAYERS: self.outputLayers}
        
    def postProcessAlgorithm(self, context, feedback):
        if self.outputLayers:
            project = context.project()
            root = project.layerTreeRoot()
            group = root.insertGroup(0, 'Group1')
            for l in self.outputLayers:
                group.addLayer(l)
            self.outputLayers.clear()
        
        return {}