import os

from qgis.core import (QgsProcessing,
                        QgsProcessingAlgorithm,
                        QgsProcessingParameterRasterLayer,
                        QgsProcessingParameterVectorLayer,
                        QgsProcessingParameterField,
                        QgsProcessingParameterBoolean,
                        QgsProcessingParameterFolderDestination,
                        QgsProcessingMultiStepFeedback,
                        QgsProcessingContext,
                        QgsProject,
                        QgsRasterLayer,
                        QgsProcessingOutputMultipleLayers)

import processing


class Batch_raster(QgsProcessingAlgorithm):
    INPUT = 'INPUT'
    FIELDS = 'FIELDS'
    OUT_FOLDER = 'OUT_FOLDER'
    LOAD_OUTPUTS = 'LOAD_OUTPUTS'
    OUTPUT_LAYERS = 'OUTPUT_LAYERS'

    final_layers = {}

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterRasterLayer('likeraster', 'like raster', defaultValue=None))
        self.addParameter(QgsProcessingParameterVectorLayer(self.INPUT, 'vector', defaultValue=None))
        self.addParameter(QgsProcessingParameterField(self.FIELDS, 'fields to select', type=0, allowMultiple=True, defaultToAllFields=True, parentLayerParameterName=self.INPUT))
        self.addParameter(QgsProcessingParameterBoolean('VERBOSE_LOG', 'Verbose logging', optional=True, defaultValue=False))
        self.addParameter(QgsProcessingParameterFolderDestination(self.OUT_FOLDER, 'Output directory')),
        self.addParameter(QgsProcessingParameterBoolean(self.LOAD_OUTPUTS, 'Load output layers?', optional=True, defaultValue=True))
        self.addOutput(QgsProcessingOutputMultipleLayers(self.OUTPUT_LAYERS, 'Output layers'))

    def processAlgorithm(self, parameters, context, model_feedback):
        # Use a multi-step feedback, so that individual child algorithm progress reports are adjusted for the
        # overall progress through the model
        results = {}
        outputs = {}
        output_layers = []
        
        likeraster = self.parameterAsRasterLayer(parameters, 'likeraster', context)
        vector = self.parameterAsVectorLayer(parameters, self.INPUT, context)
        fields = self.parameterAsFields(parameters, self.FIELDS, context)
        out_dir = self.parameterAsString(parameters, self.OUT_FOLDER, context)
        load_outputs = self.parameterAsBool(parameters, 'LOAD_OUTPUTS', context)
        
        steps = len(fields)
        step = 1
        feedback = QgsProcessingMultiStepFeedback(steps, model_feedback)
        
        for index, field in enumerate(fields):
            if feedback.isCanceled():
                break
            feedback.pushInfo(str(field))
            if not 'OUT_FOLDER' in out_dir:
                out_path = os.path.join(out_dir, f'{field}_rasterized.tif')
            else:
                out_path = 'TEMPORARY_OUTPUT'
        
            # Rasterize (vector to raster)
            alg_params = {
                'BURN': 0,
                'DATA_TYPE': 5,
                'EXTENT': likeraster.extent(),
                'EXTRA': '',
                'FIELD': field,
                'INIT': None,
                'INPUT': parameters[self.INPUT],
                'INVERT': False,
                'NODATA': 0,
                'OPTIONS': '',
                'UNITS': 1,
                'OUTPUT': f'{field}',
                'HEIGHT':likeraster.rasterUnitsPerPixelY(),
                'WIDTH': likeraster.rasterUnitsPerPixelX(),
                'OUTPUT': out_path,
            }
            
            feedback.setCurrentStep(step)
            step+=1
            
            outputs[f'RasterizeVectorToRaster{field}'] = processing.run('gdal:rasterize',
                                                                        alg_params,
                                                                        is_child_algorithm=True,
                                                                        context=context,
                                                                        feedback=feedback)
                
            results[f'Raster_out{field}'] = outputs[f'RasterizeVectorToRaster{field}']['OUTPUT']

            if load_outputs:
                lyr = QgsRasterLayer(results[f'Raster_out{field}'], f'Raster_out{field}', 'gdal')
                feedback.pushInfo(repr(lyr.isValid()))
                if lyr.isValid():
                    context.temporaryLayerStore().addMapLayer(lyr)
                    details = QgsProcessingContext.LayerDetails(lyr.name(), context.project(), lyr.name())
#                    details.setOutputLayerName(lyr)
                    details.forceName = True
                    context.addLayerToLoadOnCompletion(lyr.id(), details)
                    output_layers.append(lyr)

        results[self.OUTPUT_LAYERS] = output_layers
        return results
    
    def name(self):
        return 'Batch_rasterize_fields'

    def displayName(self):
        return 'Batch_rasterize_fields'

    def group(self):
        return ''

    def groupId(self):
        return ''

    def createInstance(self):
        return Batch_raster()