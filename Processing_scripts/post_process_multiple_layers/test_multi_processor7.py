
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
                       
class StyleRasters(QgsProcessingAlgorithm):
    '''
    Working example of setting post processor to multiple output layers
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
        return self.tr("Apply a style to multiple raster layers")
 
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
                pp = self.postProcessorClassFactory(rl.id(), QColor(0, 0, 255), QColor(255, 0, 0))
                if context.willLoadLayerOnCompletion(rl.id()):
                    context.layerToLoadOnCompletionDetails(rl.id()).setPostProcessor(pp)
            
        return {self.OUTPUT_LAYERS: output_layers}

    def postProcessorClassFactory(self, name, col1, col2):
        
        def postProcessLayer(cls_inst, layer, context, feedback):
            if layer.isValid():
                prov = layer.dataProvider()
                stats = prov.bandStatistics(1, QgsRasterBandStats.All, layer.extent(), 0)
                min = stats.minimumValue
                max = stats.maximumValue
                renderer = QgsSingleBandPseudoColorRenderer(prov, 1)
                renderer.setClassificationMin(min)
                renderer.setClassificationMax(max)
                color_ramp = QgsGradientColorRamp(col1, col2)
                renderer.createShader(color_ramp)
                layer.setRenderer(renderer)
                layer.triggerRepaint()
            feedback.pushInfo(f'{layer.name()} post processed')
            
        def create(cls):
            cls.instance = cls()
            return cls.instance
            
        proc = type(f'{name}_processor', (QgsProcessingLayerPostProcessorInterface,), {'postProcessLayer': postProcessLayer,
                                                                                        'create': create})
        proc_inst = proc.create(proc)
        return proc_inst
