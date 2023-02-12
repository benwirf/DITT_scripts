
from PyQt5.QtCore import QCoreApplication, QVariant
from PyQt5.QtGui import QColor
from qgis.core import (QgsProcessing,
                        QgsProcessingAlgorithm,
                        QgsProcessingParameterFile,
                        QgsRasterLayer,
                        QgsProcessingContext,
                        QgsProcessingOutputMultipleLayers,
                        QgsProcessingLayerPostProcessorInterface,
                        QgsRasterBandStats,
                        QgsSingleBandPseudoColorRenderer,
                        QgsGradientColorRamp,
                        QgsColorRampShader,
                        QgsStyle,
                        QgsRasterShader)

from pathlib import Path
import os
import time
                       
class StyleRasters(QgsProcessingAlgorithm):
    '''
    Working example of post-processing multiple layers.
    Here we will apply a style to the output rasters.
    '''
    INPUT_FOLDER = 'INPUT_FOLDER'
    OUTPUT_LAYERS = 'OUTPUT_LAYERS'

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
            lid = None
            if rl.isValid():
                context.temporaryLayerStore().addMapLayer(rl)
                context.addLayerToLoadOnCompletion(rl.id(), QgsProcessingContext.LayerDetails(rl.name(),
                                                                                        context.project(),
                                                                                        rl.name()))
                lid = rl.id()
                output_layers.append(rl)

        return {self.OUTPUT_LAYERS: output_layers}
        
    def postProcessAlgorithm(self, context, feedback):
        lyrs = context.layersToLoadOnCompletion()
        for lyr_id, details in lyrs.items():
            lyr = context.getMapLayer(lyr_id)
            if lyr.isValid():
                prov = lyr.dataProvider()
                stats = prov.bandStatistics(1, QgsRasterBandStats.All, lyr.extent(), 0)
                min = stats.minimumValue
                max = stats.maximumValue
                renderer = QgsSingleBandPseudoColorRenderer(prov, 1)
                renderer.setClassificationMin(min)
                renderer.setClassificationMax(max)
                color_ramp = QgsGradientColorRamp(QColor(0, 0, 255), QColor(255, 0, 0))
                renderer.createShader(color_ramp)
                lyr.setRenderer(renderer)
                lyr.triggerRepaint()
        
        return {}
