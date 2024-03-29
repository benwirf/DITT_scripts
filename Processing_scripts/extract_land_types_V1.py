from qgis.PyQt.QtCore import QCoreApplication, QVariant, QDir
from qgis.core import (QgsVectorLayer,
                        QgsField,
                        QgsFeature,
                        QgsFeatureSink,
                        QgsFeatureRequest,
                        QgsProcessing,
                        QgsProcessingAlgorithm,
                        QgsProcessingParameterFeatureSource,
                        QgsProcessingParameterField,
                        QgsProcessingParameterFeatureSink,
                        QgsProcessingParameterBoolean,
                        QgsProcessingParameterEnum,
                        QgsProcessingParameterDefinition,
                        QgsProcessingParameterFolderDestination,
                        QgsProcessingOutputMultipleLayers,
                        QgsProcessingMultiStepFeedback,
                        QgsSpatialIndex,
                        QgsGeometry,
                        QgsProcessingException,
                        QgsCoordinateTransform,
                        QgsCoordinateReferenceSystem,
                        QgsDistanceArea,
                        QgsUnitTypes)

from pathlib import Path

import processing

import os
                       
class ExtractLandTypes(QgsProcessingAlgorithm):
    LAND_TYPES = 'LAND_TYPES'# Vector polygon
    UNIT_FIELD = 'UNIT_FIELD'# Field containing unique map unit/land unit
    PADDOCKS = 'PADDOCKS'# Vector polygon
    WATERPOINTS = 'WATERPOINTS'# Vector point
    DISSOLVE_PADDOCKS = 'DISSOLVE_PADDOCKS'# Boolean
    WATERED_AREAS = 'WATERED_AREAS'# Enum
    AREA_METHOD = 'AREA_METHOD'# Enum
    OUTPUT_FOLDER = 'OUTPUT_FOLDER'# destination folder
    LOAD_OUTPUTS = 'LOAD_OUTPUTS'# Boolean
    OUTPUT_LAYERS = 'OUTPUT_LAYERS'
    OUTPUT_FORMAT = 'OUTPUT_FORMAT'
    
    WA_DISTANCES = ['3km', '5km']
    AREA_METHODS = ['Ellipsoidal', 'Planar']
    FORMATS = ['gpkg', 'shp', 'json', 'kml', 'kmz']
    
    # Will be populated with output layer paths if user selects 'Load Outputs'
    layers_to_load = []
 
    def __init__(self):
        super().__init__()
 
    def name(self):
        return "extractlandtypes"
         
    def displayName(self):
        return "Extract Land Types"
 
    def group(self):
        return "Examples"
 
    def groupId(self):
        return "examples"
 
    def shortHelpString(self):
        return "Extract and calculate land type areas for property, paddock and watered areas"
 
    def helpUrl(self):
        return "https://qgis.org"
         
    def createInstance(self):
        return type(self)()
        
    def checkParameterValues(self, parameters, context):
        if (parameters[self.WATERPOINTS] and not parameters[self.WATERED_AREAS]) or (not parameters[self.WATERPOINTS] and parameters[self.WATERED_AREAS]):
            return (False, 'Water points and watered area inputs are incompatible. Specify both or neither.')
        return (True, '')
           
    def initAlgorithm(self, config=None):
        
        self.addParameter(QgsProcessingParameterFeatureSource(
            self.LAND_TYPES,
            "Land types layer (e.g. land systems/ units)",
            [QgsProcessing.TypeVectorPolygon],
            optional=False))
            
        self.addParameter(QgsProcessingParameterField(
            self.UNIT_FIELD,
            "Field containing unique map unit/ land unit name",
            parentLayerParameterName=self.LAND_TYPES,
            type=QgsProcessingParameterField.String))
            
        self.addParameter(QgsProcessingParameterFeatureSource(
            self.PADDOCKS,
            "Property paddocks layer",
            [QgsProcessing.TypeVectorPolygon],
            optional=False))

        self.addParameter(QgsProcessingParameterFeatureSource(
            self.WATERPOINTS,
            "Property waterpoints layer",
            [QgsProcessing.TypeVectorPoint],
            optional=True))
            
        self.addParameter(QgsProcessingParameterBoolean(
            self.DISSOLVE_PADDOCKS,
            "Include calculation for whole property (paddocks dissolved)?",
            defaultValue=False))
            
        self.addParameter(QgsProcessingParameterEnum(
            self.WATERED_AREAS,
            "Include watered areas?",
            self.WA_DISTANCES,
            allowMultiple=True,
            optional=True))
            
        self.parameterDefinition(self.WATERED_AREAS).setMetadata({
            'widget_wrapper': {
                'useCheckBoxes': True,
                'columns': 2}})
                
        self.addParameter(QgsProcessingParameterEnum(
            self.AREA_METHOD,
            "Area calculation method",
            self.AREA_METHODS,
            defaultValue=0))
            
        self.parameterDefinition(self.AREA_METHOD).setMetadata({
            'widget_wrapper': {
                'useCheckBoxes': True,
                'columns': 2}})

        self.parameterDefinition(self.AREA_METHOD).setFlags(QgsProcessingParameterDefinition.FlagAdvanced)
        
        self.addParameter(QgsProcessingParameterFolderDestination(
            self.OUTPUT_FOLDER,
            "Folder for output files"))
            
        '''
        Prime suspect (output param) in case of crash/freeze- remove this first
        '''
        self.addOutput(QgsProcessingOutputMultipleLayers(
            self.OUTPUT_LAYERS,
            "Output layers"))
            
        self.addParameter(QgsProcessingParameterBoolean(
            self.LOAD_OUTPUTS,
            "Load output layers on completion?",
            defaultValue=False))
            
        self.addParameter(QgsProcessingParameterEnum(
            self.OUTPUT_FORMAT,
            "Output file format",
            self.FORMATS,
            allowMultiple=False,
            defaultValue=self.FORMATS[0],
            optional=False))
        
    def processAlgorithm(self, parameters, context, model_feedback):
        results = {}
        outputs = {}
 
        source_land_types = self.parameterAsSource(parameters, self.LAND_TYPES, context)
        unit_fields = self.parameterAsFields(parameters, self.UNIT_FIELD, context)
        source_paddocks = self.parameterAsSource(parameters, self.PADDOCKS, context)
        source_waterpoints = self.parameterAsSource(parameters, self.WATERPOINTS, context)
        dissolve_paddocks = self.parameterAsBool(parameters, self.DISSOLVE_PADDOCKS, context)
        watered_areas = self.parameterAsEnums(parameters, self.WATERED_AREAS, context)
        area_method = self.parameterAsEnum(parameters, self.AREA_METHOD, context)
        output_folder = self.parameterAsString(parameters, self.OUTPUT_FOLDER, context)
        load_outputs = self.parameterAsBool(parameters, self.LOAD_OUTPUTS, context)
        output_format = self.parameterAsEnum(parameters, self.OUTPUT_FORMAT, context)
        
        # Used to calculate land type areas if user selects ellipsoidal method
        da = QgsDistanceArea()
        
        # creates output destination folder
        if not QDir().mkpath(output_folder):
            raise QgsProcessingException('Failed to create output directory')
            return {}
        
        # Check CRS of paddock layer and transform to epsg:9473 if geographic
        src_crs = source_paddocks.sourceCrs()
        if src_crs.isGeographic():
            dest_crs = QgsCoordinateReferenceSystem('epsg:9473')# Transform to GDA2020 Albers (projected)
        else:
            dest_crs = src_crs
        
        # Create a QgsSpatialIndex from land type layer
        land_types_index = QgsSpatialIndex(source_land_types.getFeatures())
        
        # Create a single geometry object comprising all property paddocks
        all_pdks = QgsGeometry.unaryUnion([f.geometry() for f in source_paddocks.getFeatures()])
#        model_feedback.pushInfo(repr(all_pdks))
        
        # Construct a feature request of land types intersecting the property extent
        req = land_types_index.intersects(self.transformedGeom(all_pdks, source_paddocks.sourceCrs(), source_land_types.sourceCrs(), context.transformContext()).boundingBox())
        
        # create temporary, transformed copy of land types with features intersecting property bounding box
        local_land_types_projected = source_land_types.materialize(QgsFeatureRequest(req).setDestinationCrs(dest_crs, context.transformContext()))
        
        # Dissolve land types by the land unit/ map unit field
        local_land_types_projected_dissolved = processing.run("native:dissolve",
                                                                {'INPUT':local_land_types_projected,
                                                                'FIELD':unit_fields,
                                                                'OUTPUT':'TEMPORARY_OUTPUT'},
                                                                context=context,
                                                                feedback=model_feedback,
                                                                is_child_algorithm=True)
        
        lltpd_temp_result = context.getMapLayer(local_land_types_projected_dissolved['OUTPUT'])
        

        # Check if user selected option to calculate for whole property...
        if dissolve_paddocks:
#            model_feedback.pushInfo(f'Source CRS: {src_crs.authid()}')
#            model_feedback.pushInfo(f'Target CRS: {dest_crs.authid()}')
            all_pdks_projected = self.transformedGeom(all_pdks, src_crs, dest_crs, context.transformContext()).makeValid()
            plt_path = os.path.join(output_folder, f'Property_land_types.{self.FORMATS[output_format]}')
            property_land_types_temp = QgsVectorLayer(f'Polygon?crs={dest_crs.authid()}', 'Property_land_types', 'memory')
            property_land_types_temp.dataProvider().addAttributes([fld for fld in source_land_types.fields()])
            property_land_types_temp.dataProvider().addAttributes([QgsField('Area_m2', QVariant.Double, prec=3),
                                                                    QgsField('Area_ha', QVariant.Double, prec=3),
                                                                    QgsField('Area_km2', QVariant.Double, prec=5),
                                                                    QgsField('Percent', QVariant.Double, prec=2)])
            property_land_types_temp.updateFields()
            for ft in lltpd_temp_result.getFeatures():
                if ft.geometry().intersects(all_pdks_projected):
                    model_feedback.pushInfo('Intersection found')
                    ix = ft.geometry().intersection(all_pdks_projected)
                    feat = QgsFeature(property_land_types_temp.fields())
                    feat.setGeometry(ix)
                    atts = ft.attributes()
                    if area_method == 1:# Planar
                        plt_area_m2 = round(ix.area(), 3)
                        plt_area_ha = round(ix.area()/10000, 3)
                        plt_area_km2 = round(ix.area()/1000000, 5)
                        plt_pcnt = (ix.area()/all_pdks_projected.area())*100
                    elif area_method == 0:# Ellipsoidal
                        da.setSourceCrs(property_land_types_temp.sourceCrs(), context.transformContext())
                        da.setEllipsoid(property_land_types_temp.sourceCrs().ellipsoidAcronym())
                        plt_area = da.measureArea(ix)
                        plt_area_m2 = round(plt_area, 3)
                        plt_area_ha = round(da.convertAreaMeasurement(plt_area, QgsUnitTypes.AreaHectares), 3)
                        plt_area_km2 = round(da.convertAreaMeasurement(plt_area, QgsUnitTypes.AreaSquareKilometers), 5)
                        plt_pcnt = (plt_area/da.measureArea(all_pdks_projected))*100
                        #*****************************************************
                    atts.append(plt_area_m2)
                    atts.append(plt_area_ha)
                    atts.append(plt_area_km2)
                    atts.append(plt_pcnt)
                    feat.setAttributes(atts)
                    property_land_types_temp.dataProvider().addFeatures([feat])
                else:
                    model_feedback.pushInfo('No intersection found!')
            if property_land_types_temp.isValid():
                    plt_result = processing.run("native:savefeatures",
                                                {'INPUT':property_land_types_temp,
                                                'OUTPUT':plt_path},
                                                context=context,
                                                feedback=model_feedback,
                                                is_child_algorithm=True)
                    if load_outputs:
                        self.layers_to_load.append(plt_path)
                        
        
        if source_waterpoints:
            waterpoints_projected = source_waterpoints.materialize(QgsFeatureRequest().setDestinationCrs(dest_crs, context.transformContext()))        
        
#        results[self.OUTPUT_LAYERS] = outputLayers
#        return results
        return {'All Inputs': [source_land_types,
                                source_paddocks,
                                source_waterpoints,
                                dissolve_paddocks,
                                watered_areas,
                                area_method,
                                output_folder,
                                load_outputs,
                                plt_path,
                                property_land_types_temp.isValid()]}
        
        
    def postProcessAlgorithm(self, context, feedback):
        for uri in self.layers_to_load:
            lyr_name = Path(uri).stem
            ml = QgsVectorLayer(uri, lyr_name, 'ogr')
            context.project().addMapLayers([ml])
        self.layers_to_load.clear()
        return {}
        
    def transformedGeom(self, g, orig_crs, target_crs, transform_context):
        geom_copy = QgsGeometry().fromWkt(g.asWkt())
        if orig_crs != target_crs:
            xform = QgsCoordinateTransform(orig_crs, target_crs, transform_context)
            geom_copy.transform(xform)
        return geom_copy
        