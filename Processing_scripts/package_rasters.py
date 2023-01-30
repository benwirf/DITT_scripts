from qgis.PyQt.QtCore import QCoreApplication, QVariant
from qgis.core import (QgsProcessing, QgsProcessingAlgorithm,
                        QgsProcessingParameterMultipleLayers,
                        QgsProcessingParameterFile,
                        QgsProcessingMultiStepFeedback)
                        
import processing
import math
                       
class PackageRasters(QgsProcessingAlgorithm):
    INPUT_RASTERS = 'INPUT_RASTERS'
    OUTPUT_GPKG = 'OUTPUT_GPKG'
 
    def __init__(self):
        super().__init__()
 
    def name(self):
        return "Package_rasters"
         
    def displayName(self):
        return "Package rasters"
 
    def group(self):
        return "Raster Tools"
 
    def groupId(self):
        return "Raster_tools"
 
    def shortHelpString(self):
        return "Packages multiple raster layers as sub-dataset raster tables\
                in an existing Geopackage."
 
    def helpUrl(self):
        return "https://qgis.org"
         
    def createInstance(self):
        return type(self)()
   
    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterMultipleLayers(self.INPUT_RASTERS, 'Input raster layers', QgsProcessing.TypeRaster)),
        self.addParameter(QgsProcessingParameterFile(self.OUTPUT_GPKG, 'Geopackage', extension='gpkg'))
 
    def processAlgorithm(self, parameters, context, model_feedback):
        input_rasters = self.parameterAsLayerList(parameters, self.INPUT_RASTERS, context)
        output_geopackage = self.parameterAsFileOutput(parameters, self.OUTPUT_GPKG, context)
        steps = len(input_rasters)
        feedback = QgsProcessingMultiStepFeedback(steps, model_feedback)
        step = 1
        
        results = {}
        outputs = {}
        
        for raster in input_rasters:
            no_data_value = raster.dataProvider().sourceNoDataValue(1)
            if math.isnan(raster.dataProvider().sourceNoDataValue(1)):
                no_data_value = None
            data_type = 6
            bnd_count = raster.bandCount()
            if bnd_count > 1:
                data_type = 1
                no_data_value = 0

            
            params = {'INPUT':raster,
                        'TARGET_CRS':None,
                        'NODATA':no_data_value,
                        'COPY_SUBDATASETS':False,
                        'OPTIONS':'',
                        'EXTRA':'-co APPEND_SUBDATASET=YES -co RASTER_TABLE={}'.format(raster.name()),
                        'DATA_TYPE':data_type,
                        'OUTPUT':output_geopackage}
            
            feedback.setCurrentStep(step)
            outputs[f'packaged_raster_{raster.name()}'] = processing.run("gdal:translate", params, context=context, feedback=feedback, is_child_algorithm=True)
            results[f'packaged_raster_{raster.name()}'] = outputs[f'packaged_raster_{raster.name()}']['OUTPUT']
            step += 1
            
        return results