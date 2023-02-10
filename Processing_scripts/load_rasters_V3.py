from qgis.PyQt.QtCore import QCoreApplication, QVariant
from qgis.core import (QgsProcessing,
                        QgsProcessingAlgorithm,
                        QgsProcessingParameterFile,
                        QgsRasterLayer,
                        QgsProcessingContext,
                        QgsProcessingUtils,
                        QgsProcessingOutputMultipleLayers,
                        QgsProcessingLayerPostProcessorInterface)

import os
                       
class LoadRasters(QgsProcessingAlgorithm):
    '''
    Working example of post-processing multiple layer
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
                
        post_processor = LoadRasterPostProcessor.create()
        context.layerToLoadOnCompletionDetails(lid).setPostProcessor(post_processor)
        post_processsor = None

        return {self.OUTPUT_LAYERS: output_layers}
        

class LoadRasterPostProcessor(QgsProcessingLayerPostProcessorInterface):

    instance = None

    def postProcessLayer(self, layer, context, feedback):  # pylint: disable=unused-argument
        project = context.project()
        root_group = project.layerTreeRoot()
        if not root_group.findGroup('Group1'):
            root_group.insertGroup(0, 'Group1')
        group1 = root_group.findGroup('Group1')
        lyrs = context.layersToLoadOnCompletion()
        for lyr_id, details in lyrs.items():
            lyr_node = root_group.findLayer(lyr_id)
            node_clone = lyr_node.clone()
            group1.addChildNode(node_clone)
            lyr_node.parent().removeChildNode(lyr_node)
            
    # Hack to work around sip bug!
    @staticmethod
    def create() -> 'LoadRasterPostProcessor':
        LoadRasterPostProcessor.instance = LoadRasterPostProcessor()
        return LoadRasterPostProcessor.instance