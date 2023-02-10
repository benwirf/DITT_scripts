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

import os
                       
class LoadRasters(QgsProcessingAlgorithm):
    '''
    Working example of post-processing multiple layers.
    Here we will apply a style to the output rasters.
    '''
    INPUT_FOLDER = 'INPUT_FOLDER'
    OUTPUT_LAYERS = 'OUTPUT_LAYERS'

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
            file_name = file.name.split('.')[0]
            file_path = os.path.join(source_folder, file.name)
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
                
        post_processor = RasterPostProcessor.create(QColor(0, 0, 255), QColor(255, 0, 0))
        context.layerToLoadOnCompletionDetails(lid).setPostProcessor(post_processor)
        post_processsor = None

        return {self.OUTPUT_LAYERS: output_layers}
        

class RasterPostProcessor(QgsProcessingLayerPostProcessorInterface):
    
    instance = None
    color1 = None
    color2 = None

    def postProcessLayer(self, layer, context, feedback):  # pylint: disable=unused-argument
        print('Post processing...')
        project = context.project()
        lyrs = context.layersToLoadOnCompletion()
        for lyr_id, details in lyrs.items():
            lyr = project.mapLayers()[lyr_id]
            if lyr.isValid():
                prov = lyr.dataProvider()
                stats = prov.bandStatistics(1, QgsRasterBandStats.All, lyr.extent(), 0)
                min = stats.minimumValue
                max = stats.maximumValue
                renderer = QgsSingleBandPseudoColorRenderer(prov, 1)
                renderer.setClassificationMin(min)
                renderer.setClassificationMax(max)
                color_ramp = QgsGradientColorRamp(self.color1, self.color2)
                renderer.createShader(color_ramp)
                lyr.setRenderer(renderer)
                lyr.triggerRepaint()
                                
    # Hack to work around sip bug!
    @staticmethod
    def create(color1, color2) -> 'RasterPostProcessor':
        RasterPostProcessor.instance = RasterPostProcessor()
        RasterPostProcessor.color1 = color1
        RasterPostProcessor.color2 = color2
        return RasterPostProcessor.instance