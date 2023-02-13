
from PyQt5.QtCore import QCoreApplication, QVariant
from PyQt5.QtGui import QColor
from qgis.core import (QgsProcessing,
                        QgsProcessingAlgorithm,
                        QgsProcessingParameterFile,
                        QgsRasterLayer,
                        QgsProcessingContext,
                        QgsProcessingOutputMultipleLayers,
                        QgsProcessingLayerPostProcessorInterface)

from pathlib import Path
import os
import time
                       
class StyleRasters(QgsProcessingAlgorithm):
    '''
    HOLY SHIT- I think this works!!!
    '''
    INPUT_FOLDER = 'INPUT_FOLDER'
    OUTPUT_LAYERS = 'OUTPUT_LAYERS'
    post_processors = []

    def __init__(self):
        super().__init__()
 
    def name(self):
        return "styleoutputrasters"
     
    def tr(self, text):
        return QCoreApplication.translate("Processing", text)
         
    def displayName(self):
        return self.tr("Style output rasters")
 
    def group(self):
        return self.tr("Examples")
 
    def groupId(self):
        return "examples"
 
    def shortHelpString(self):
        return self.tr("Load and style multiple raster layers")
 
    def helpUrl(self):
        return "https://qgis.org"
         
    def createInstance(self):
        return type(self)()
   
    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterFile(
            self.INPUT_FOLDER,
            self.tr("Source directory"),
            behavior=QgsProcessingParameterFile.Folder))
            
        self.addOutput(QgsProcessingOutputMultipleLayers(
            self.OUTPUT_LAYERS,
            'Output layers'))
 
    def processAlgorithm(self, parameters, context, feedback):
        source_folder = self.parameterAsString(parameters, self.INPUT_FOLDER, context)
        output_layers = []
        for file in os.scandir(source_folder):
            file_path = os.path.join(source_folder, file.name)
            file_name = Path(file_path).stem
            rl = QgsRasterLayer(file_path, file_name, 'gdal')
            feedback.pushInfo(repr(rl.isValid()))
            if rl.isValid():
                context.temporaryLayerStore().addMapLayer(rl)
                context.addLayerToLoadOnCompletion(rl.id(), QgsProcessingContext.LayerDetails(rl.name(),
                                                                                        context.project(),
                                                                                        rl.name()))
                output_layers.append(rl)
                pp = self.classFactory(rl.id())
                if context.willLoadLayerOnCompletion(rl.id()):
                    context.layerToLoadOnCompletionDetails(rl.id()).setPostProcessor(pp)
            
        return {self.OUTPUT_LAYERS: output_layers}

    def classFactory(self, name):
        
        def postProcessLayer(i, layer, context, feedback):
            print(layer.name())
            
        def create(cls):
            cls.instance = cls()
            return cls.instance
            
        proc = type(f'{name}_processor', (QgsProcessingLayerPostProcessorInterface,), {'postProcessLayer': postProcessLayer,
                                                                                        'create': create})
        proci = proc.create(proc)
        return proci