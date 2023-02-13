
from PyQt5.QtCore import QCoreApplication, QVariant

from qgis.core import (QgsProcessing,
                        QgsProcessingAlgorithm,
                        QgsProcessingParameterFile,
                        QgsRasterLayer,
                        QgsProcessingContext,
                        QgsProcessingOutputMultipleLayers,
                        QgsProcessingLayerPostProcessorInterface)

from pathlib import Path
import os
                       
class AddRastersToGroup(QgsProcessingAlgorithm):
    '''
    Working example of setting post processor to multiple output layers
    '''
    INPUT_FOLDER = 'INPUT_FOLDER'
    OUTPUT_LAYERS = 'OUTPUT_LAYERS'

    def __init__(self):
        super().__init__()
 
    def name(self):
        return "addoutputrasterstogroup"
     
    def tr(self, text):
        return QCoreApplication.translate("Processing", text)
         
    def displayName(self):
        return self.tr("Add output rasters")
 
    def group(self):
        return self.tr("Examples")
 
    def groupId(self):
        return "examples"
 
    def shortHelpString(self):
        return self.tr("Load multiple raster layers added to a created group")
 
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
                pp = self.postProcessorClassFactory(rl.id())
                if context.willLoadLayerOnCompletion(rl.id()):
                    context.layerToLoadOnCompletionDetails(rl.id()).setPostProcessor(pp)
            
        return {self.OUTPUT_LAYERS: output_layers}

    def postProcessorClassFactory(self, name):
        
        def postProcessLayer(cls_inst, layer, context, feedback):
            group_name = 'group1'
            project = context.project()
            root_group = project.layerTreeRoot()
            if not root_group.findGroup(group_name):
                root_group.insertGroup(0, group_name)
            group1 = root_group.findGroup(group_name)
            if group1:
                lyr_node = root_group.findLayer(layer.id())
                if lyr_node:
                    node_clone = lyr_node.clone()
                    group1.addChildNode(node_clone)
                    lyr_node.parent().removeChildNode(lyr_node)
            feedback.pushInfo(f'{layer.name()} post processed')
            
        def create(cls):
            cls.instance = cls()
            return cls.instance
            
        proc = type(f'{name}_processor', (QgsProcessingLayerPostProcessorInterface,), {'postProcessLayer': postProcessLayer,
                                                                                        'create': create})
        proc_inst = proc.create(proc)
        return proc_inst
        