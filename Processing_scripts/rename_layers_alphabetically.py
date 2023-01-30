from qgis.PyQt.QtCore import QCoreApplication
from qgis.core import (QgsProcessing, QgsProcessingAlgorithm,
                        QgsProcessingParameterMultipleLayers)

from string import ascii_lowercase
import itertools
                       
class ExAlgo(QgsProcessingAlgorithm):
    INPUT_LAYERS = 'INPUT_LAYERS'
    OUTPUT_NAMES = 'OUTPUT_NAMES'
 
    def __init__(self):
        super().__init__()
 
    def name(self):
        return "Rename_layers_alphabetically"
         
    def displayName(self):
        return "Rename layers alphabetically"
 
    def group(self):
        return "Layer Tools"
 
    def groupId(self):
        return "Layer_tools"
 
    def shortHelpString(self):
        return "Adds a unique alphabetical prefix to layer names in the\
        layer tree based on their current order.\
        Ensures that order will be maintained if layers are added to a geopackage."
 
    def helpUrl(self):
        return "https://qgis.org"
        
    def flags(self):
        return QgsProcessingAlgorithm.FlagNoThreading
         
    def createInstance(self):
        return type(self)()
   
    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterMultipleLayers(self.INPUT_LAYERS, 'Layers to rename', QgsProcessing.TypeMapLayer)),
 
    def processAlgorithm(self, parameters, context, feedback):
        input_layers = self.parameterAsLayerList(parameters, self.INPUT_LAYERS, context)
        root_group = context.project().layerTreeRoot()
        layers_in_toc_order = [l for l in root_group.layerOrder() if l in input_layers]

        prefix_lst = []

        count = 1

        for s in self.iter_all_strings():
            prefix_lst.append(s)
            if count == len(layers_in_toc_order):
                break
            count += 1

        new_names = [f'{sorted(prefix_lst)[i]}_{layers_in_toc_order[i].name()}' for i in range(len(layers_in_toc_order))]

        for i, layer in enumerate(layers_in_toc_order):
            layer.setName(new_names[i])
 
        return {self.OUTPUT_NAMES: new_names}
        
    def iter_all_strings(self):
        for size in itertools.count(1):
            for s in itertools.product(ascii_lowercase, repeat=size):
                yield "".join(s)