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
    Now works and doesn't crash/ freeze QGIS
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
        
#    def flags(self):
#        return super().flags() | QgsProcessingAlgorithm.FlagNoThreading
   
    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterFile(
            self.INPUT_FOLDER,
            self.tr("Source directory"),
            behavior=QgsProcessingParameterFile.Folder))
            
        self.addOutput(QgsProcessingOutputMultipleLayers(
            self.OUTPUT_LAYERS,
            'Output layers'))
 
    def processAlgorithm(self, parameters, context, feedback):
        lyrs_to_add = {}
        source_folder = self.parameterAsString(parameters, self.INPUT_FOLDER, context)
        
        for file in os.scandir(source_folder):
            file_name = file.name.split('.')[0]
            file_path = os.path.join(source_folder, file.name)
            rl = QgsRasterLayer(file_path, file_name, 'gdal')
            feedback.pushInfo(repr(rl.isValid()))
            if rl.isValid():
                context.temporaryLayerStore().addMapLayer(rl)

#        return {}
        return {'OUTPUT': self.OUTPUT_LAYERS}

    def postProcessAlgorithm(self, context, feedback):
        '''
        Probably should just do this in processAlgorithm method
        '''
        lyrs = context.temporaryLayerStore().mapLayers()
        for lyr_id, lyr in lyrs.items():
            print('temp layer', lyr)
            context.addLayerToLoadOnCompletion(lyr_id, QgsProcessingContext.LayerDetails(lyr.name(),
                                                                                        context.project(),
                                                                                        lyr.name()))
            post_processor = LoadRasterPostProcessor.create()
            print(post_processor)
            '''
            Still only gets applied to the last layer!
            '''
            context.layerToLoadOnCompletionDetails(lyr_id).setPostProcessor(post_processor)
            post_processsor = None
        return {}
        

class LoadRasterPostProcessor(QgsProcessingLayerPostProcessorInterface):

    instance = None

    def postProcessLayer(self, layer, context, feedback):  # pylint: disable=unused-argument
        print(layer)
        if not isinstance(layer, QgsRasterLayer):
            print('Will return nothing', layer)
            return
                
        project = context.project()
        root_group = project.layerTreeRoot()
        node_layer = root_group.findLayer(layer.id())
        node_layer_clone = node_layer.clone()
        if not root_group.findGroup('Group1'):
            root_group.insertGroup(0, 'Group1')
        group1 = root_group.findGroup('Group1')
        group1.addChildNode(node_layer_clone)
        parent = node_layer.parent()
        parent.removeChildNode(node_layer)
        
    # Hack to work around sip bug!
    @staticmethod
    def create() -> 'LoadRasterPostProcessor':
        LoadRasterPostProcessor.instance = LoadRasterPostProcessor()
        return LoadRasterPostProcessor.instance
