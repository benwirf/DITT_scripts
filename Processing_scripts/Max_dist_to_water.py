from qgis.PyQt.QtCore import QCoreApplication, QVariant
from qgis.core import (QgsFeatureRequest,
                        QgsProcessing, QgsProcessingAlgorithm,
                        QgsProcessingParameterFeatureSource,
                        QgsProcessingParameterField,
                        QgsProcessingParameterFolderDestination,
                        QgsProcessingMultiStepFeedback,
                        QgsVectorLayer,
                        QgsWkbTypes,
                        QgsProcessingParameterNumber,
                        QgsProcessingOutputMultipleLayers)

import os
import processing
                       
class ExAlgo(QgsProcessingAlgorithm):
    PADDOCKS = 'PADDOCKS'
    PADDOCK_NAME_FIELD = 'PADDOCK_NAME_FIELD'
    WATER_POINTS = 'WATER_POINTS'
    OUTPUT_RESOLUTION = 'OUTPUT_RESOLUTION'
    OUTPUT_FOLDER = 'OUTPUT_FOLDER'
    OUTPUT_LAYERS = 'OUTPUT_LAYERS'
 
    def __init__(self):
        super().__init__()
 
    def name(self):
        return "water_proximity"
     
         
    def displayName(self):
        return "Water proximity"
 
    def group(self):
        return "Examples"
 
    def groupId(self):
        return "examples"
 
    def shortHelpString(self):
        return "Calculates maximum distance to water per paddock"
 
    def helpUrl(self):
        return "https://qgis.org"
         
    def createInstance(self):
        return type(self)()
   
    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterFeatureSource(
            self.PADDOCKS,
            "Input paddocks layer",
            [QgsProcessing.TypeVectorPolygon]))
            
        self.addParameter(QgsProcessingParameterField(
            self.PADDOCK_NAME_FIELD,
            "Paddock name field",
            parentLayerParameterName=self.PADDOCKS,
            type=QgsProcessingParameterField.String))
            
        self.addParameter(QgsProcessingParameterFeatureSource(
            self.WATER_POINTS,
            "Input water points layer",
            [QgsProcessing.TypeVectorPoint]))
            
        self.addParameter(QgsProcessingParameterNumber(
            self.OUTPUT_RESOLUTION,
            "Pixel size (resolution) for output proximity rasters",
            defaultValue=25,
            minValue=5.0,
            maxValue=100.0))
            
        self.addParameter(QgsProcessingParameterFolderDestination(
            self.OUTPUT_FOLDER,
            "Folder for output files"))
            
        self.addOutput(QgsProcessingOutputMultipleLayers(
            self.OUTPUT_LAYERS,
            "Output layers"))
 
    def processAlgorithm(self, parameters, context, model_feedback):
        results = {}
        outputs = {}
        
        source_paddocks = self.parameterAsSource(parameters, self.PADDOCKS, context)
        # list of field names...
        paddock_name_field = self.parameterAsFields(parameters, self.PADDOCK_NAME_FIELD, context)[0]
        source_waterpoints = self.parameterAsSource(parameters, self.WATER_POINTS, context)
        output_folder = self.parameterAsString(parameters, self.OUTPUT_FOLDER, context)
        
        pdk_name_fld_idx = source_paddocks.fields().lookupField(paddock_name_field)
        
        #############Transform either or both input layer/s if geographic#############
        #I won't fully trust the logic in this block until I test it thoroughly...
        #hence, if something isn't working- start debugging here.
        # paddocks projected but waterpoints geographic
        if not source_paddocks.sourceCrs().isGeographic() and source_waterpoints.sourceCrs().isGeographic():
            crs = source_paddocks.sourceCrs()
            prepared_paddocks = source_paddocks.materialize(QgsFeatureRequest().setSubsetOfAttributes([pdk_name_fld_idx]))
            prepared_waterpoints = source_waterpoints.materialize(QgsFeatureRequest().setSubsetOfAttributes([]).setDestinationCrs(crs, context.transformContext()))
        # water points projected but paddocks geographic
        elif source_paddocks.sourceCrs().isGeographic() and not source_waterpoints.sourceCrs().isGeographic():
            crs = source_waterpoints.sourceCrs()
            prepared_paddocks = source_paddocks.materialize(QgsFeatureRequest().setSubsetOfAttributes([pdk_name_fld_idx]).setDestinationCrs(crs, context.transformContext()))
            prepared_waterpoints = source_waterpoints.materialize(QgsFeatureRequest().setSubsetOfAttributes([]))
        # both inputs geographic (we 'transform' to epsg:9473 GDA202 Australian Albers)
        elif source_paddocks.sourceCrs().isGeographic() and source_waterpoints.sourceCrs().isGeographic():
            crs = QgsCoordinateReferenceSystem('epsg:9473')
            prepared_paddocks = source_paddocks.materialize(QgsFeatureRequest().setSubsetOfAttributes([pdk_name_fld_idx]).setDestinationCrs(crs, context.transformContext()))
            prepared_waterpoints = source_waterpoints.materialize(QgsFeatureRequest().setSubsetOfAttributes([]).setDestinationCrs(crs, context.transformContext()))
        # both inputs are projected
        else:
            # projected input crs are different (we 'transform' waterpoints to paddocks crs)
            if source_paddocks.sourceCrs() != source_waterpoints.sourceCrs():
                crs = source_paddocks.sourceCrs()
                prepared_waterpoints = source_waterpoints.materialize(QgsFeatureRequest().setSubsetOfAttributes([]).setDestinationCrs(crs, context.transformContext()))
                prepared_paddocks = source_paddocks.materialize(QgsFeatureRequest().setSubsetOfAttributes([pdk_name_fld_idx]))
            # both projected input crs are the same
            else:
                crs = source_paddocks.sourceCrs()
                prepared_paddocks = source_paddocks.materialize(QgsFeatureRequest().setSubsetOfAttributes([pdk_name_fld_idx]))
                prepared_waterpoints = source_waterpoints.materialize(QgsFeatureRequest().setSubsetOfAttributes([]))
            
        ########################################################################
        
        ###Calculate number of paddocks containing at least one waterpoint######
        analyzed_paddocks = [ft for ft in prepared_paddocks.getFeatures() if [f for f in prepared_waterpoints.getFeatures() if f.geometry().intersects(ft.geometry())]]
#        model_feedback.pushInfo(repr(analyzed_paddocks))
        ########################################################################
        steps = len(analyzed_paddocks)*3
        feedback = QgsProcessingMultiStepFeedback(steps, model_feedback)
        step = 1
        
        outputLayers = []
        
        # Iterate over each paddock
        for paddock in prepared_paddocks.getFeatures():
            paddock_name = paddock[paddock_name_field]
            # Simple spatial query to retrieve water points within each paddock
            waterpoint_feats = [f for f in prepared_waterpoints.getFeatures() if f.geometry().intersects(paddock.geometry())]
            model_feedback.pushInfo(repr(waterpoint_feats))
            if not waterpoint_feats:
                continue
            model_feedback.pushInfo(repr(crs))
            # Create a temporary layer to hold waterpoint features which fall within each paddock
            tmp_lyr = QgsVectorLayer(f'Point?crs={crs.authid()}', '', 'memory')
            tmp_lyr.dataProvider().addFeatures(waterpoint_feats)
            
            ############################################################################
            # Rasterise temporary waterpoint layer to create a binary raster where pixel value
            # is 1 at water locations and 0 everywhere else
            raster_extent = paddock.geometry().boundingBox()
            xmin = raster_extent.xMinimum()
            xmax = raster_extent.xMaximum()
            ymin = raster_extent.yMinimum()
            ymax = raster_extent.yMaximum()
            
            extent_string = f'{xmin},{xmax},{ymin},{ymax} [{tmp_lyr.crs().authid()}]'
            #extent_string = '670539.640100000,674839.662800000,8101017.562800000,8103145.602500000 [EPSG:28352]'
            
            rasterize_params = {'INPUT':tmp_lyr,
                                'FIELD':'',
                                'BURN':1,
                                'USE_Z':False,
                                'UNITS':1,
                                'WIDTH':25,
                                'HEIGHT':25,
                                'EXTENT':extent_string,
                                'NODATA':-1,
                                'OPTIONS':'',
                                'DATA_TYPE':0,
                                'INIT':0,
                                'INVERT':False,
                                'EXTRA':'',
                                'OUTPUT':'TEMPORARY_OUTPUT'}
            
            feedback.setCurrentStep(step)
            step+=1
            outputs[f'rasterized_{paddock_name}'] = processing.run("gdal:rasterize", rasterize_params, context=context, feedback=feedback, is_child_algorithm=True)
            results[f'rasterized_{paddock_name}'] = outputs[f'rasterized_{paddock_name}']['OUTPUT']
            #####################################################################################
            # Calculate Proximity Raster for each waterpoint binary raster...
            proximity_params = {'INPUT':results[f'rasterized_{paddock_name}'],
                                'BAND':1,
                                'VALUES':'1',
                                'UNITS':0,
                                'MAX_DISTANCE':0,
                                'REPLACE':0,
                                'NODATA':0,
                                'OPTIONS':'',
                                'EXTRA':'',
                                'DATA_TYPE':5,
                                'OUTPUT':'TEMPORARY_OUTPUT'}
                                
            feedback.setCurrentStep(step)
            step+=1
            outputs[f'proximity_{paddock_name}'] = processing.run("gdal:proximity", proximity_params, context=context, feedback=feedback, is_child_algorithm=True)
            results[f'proximity_{paddock_name}'] = outputs[f'proximity_{paddock_name}']['OUTPUT']
            ############################################################################
            #*Use materialize()
            paddock_layer_subset = prepared_paddocks.materialize(QgsFeatureRequest(paddock.id()))

            clipped_path = os.path.join(output_folder, f'{paddock[paddock_name_field]}.tif')
            
            clip_params = {'INPUT':results[f'proximity_{paddock_name}'],
                            'MASK':paddock_layer_subset,
                            'SOURCE_CRS':None,
                            'TARGET_CRS':None,
                            'NODATA':-9999,
                            'ALPHA_BAND':False,
                            'CROP_TO_CUTLINE':True,
                            'KEEP_RESOLUTION':False,
                            'SET_RESOLUTION':False,
                            'X_RESOLUTION':None,
                            'Y_RESOLUTION':None,
                            'MULTITHREADING':False,
                            'OPTIONS':'',
                            'DATA_TYPE':0,
                            'EXTRA':'',
                            'OUTPUT':clipped_path}

            feedback.setCurrentStep(step)
            step+=1
            outputLayers.append(clipped_path)
            outputs[f'clipped_{paddock_name}'] = processing.run("gdal:cliprasterbymasklayer", clip_params, context=context, feedback=feedback, is_child_algorithm=True)
            results[f'clipped_{paddock_name}'] = outputs[f'clipped_{paddock_name}']['OUTPUT']
        results[self.OUTPUT_LAYERS] = outputLayers
        return results