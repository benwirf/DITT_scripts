from qgis.PyQt.QtCore import QCoreApplication, QVariant, QObject
from qgis.core import (QgsProcessing,
                        QgsProcessingAlgorithm,
                        QgsProcessingParameterFile,
                        QgsRasterLayer,
                        QgsProcessingContext,
                        QgsProcessingOutputMultipleLayers,
                        QgsProcessingLayerPostProcessorInterface)

from pathlib import Path
import os
                       
class LoadRasters(QgsProcessingAlgorithm):
    '''
    Working example of post-processing multiple layers,
    here we create a layer tree group and add the output rasters
    to it
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
        return self.tr("Load multiple raster layers to project,\
        create and add resulting layers to a layer tree group in post\
        processing.")
 
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
                
        post_processor = LoadRasterPostProcessor.create()
        context.layerToLoadOnCompletionDetails(lid).setPostProcessor(post_processor)
        post_processsor = None

        return {self.OUTPUT_LAYERS: output_layers}
        

class LoadRasterPostProcessor(QgsProcessingLayerPostProcessorInterface):
    
    instance = None
    group_name = 'group1'

    def postProcessLayer(self, layer, context, feedback):  # pylint: disable=unused-argument
        project = context.project()
        root_group = project.layerTreeRoot()
        if not root_group.findGroup(self.group_name):
            root_group.insertGroup(0, self.group_name)
        group1 = root_group.findGroup(self.group_name)
        lyrs = context.layersToLoadOnCompletion()
        for lyr_id, details in lyrs.items():
            lyr_node = root_group.findLayer(lyr_id)
            if lyr_node:
                node_clone = lyr_node.clone()
                group1.addChildNode(node_clone)
                lyr_node.parent().removeChildNode(lyr_node)

    # Hack to work around sip bug!
    @staticmethod
    def create() -> 'LoadRasterPostProcessor':
        LoadRasterPostProcessor.instance = LoadRasterPostProcessor()
        return LoadRasterPostProcessor.instance
