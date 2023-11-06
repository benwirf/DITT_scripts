from qgis.PyQt.QtCore import QCoreApplication, QVariant
from qgis.core import (NULL, QgsField, QgsFields, QgsFeature, QgsFeatureSink,
                        QgsFeatureRequest, QgsProcessing, QgsProcessingAlgorithm,
                        QgsProcessingParameterFeatureSource,
                        QgsProcessingParameterField,
                        QgsProcessingParameterFileDestination,
                        QgsProcessingParameterFeatureSink,
                        QgsGeometry, QgsSpatialIndex,
                        QgsCoordinateTransform)
import processing

                       
class CarryingCapacitySummary(QgsProcessingAlgorithm):
    LAND_TYPES = 'LAND_TYPES'
    OUTPUT_FIELDS = 'OUTPUT_FIELDS'
    LAND_TYPE_FIELD = 'LAND_TYPE_FIELD'
    PADDOCKS = 'PADDOCKS'
    PDK_NAME_FIELD = 'PDK_NAME_FIELD'
    WATERPOINTS = 'WATERPOINTS'
    OUTPUT = 'OUTPUT'
    XL_SUMMARY = 'XL_SUMMARY'
 
    def __init__(self):
        super().__init__()
 
    def name(self):
        return "carryingcapacitysummary"
         
    def displayName(self):
        return "Carrying capacity summary"
 
    def group(self):
        return "Analysis"
 
    def groupId(self):
        return "analysis"
 
    def shortHelpString(self):
        return "Generate spreadsheet summary of watered land type\
                areas and percentage for each paddock polygon\
                in an input paddock layer."
 
    def helpUrl(self):
        return "https://qgis.org"
         
    def createInstance(self):
        return type(self)()
   
    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterFeatureSource(
            self.LAND_TYPES,
            "Land types layer",
            [QgsProcessing.TypeVectorPolygon]))
            
        self.addParameter(QgsProcessingParameterField(
            self.OUTPUT_FIELDS,
            "Fields to copy to output layers",
            parentLayerParameterName=self.LAND_TYPES,
            allowMultiple=True))
            
        self.addParameter(QgsProcessingParameterField(
            self.LAND_TYPE_FIELD,
            "Field containing unique land type name",
            parentLayerParameterName=self.LAND_TYPES,
            type=QgsProcessingParameterField.String))
        
        self.addParameter(QgsProcessingParameterFeatureSource(
            self.PADDOCKS,
            "Paddock polygon layer",
            [QgsProcessing.TypeVectorPolygon]))
            
        self.addParameter(QgsProcessingParameterField(
            self.PDK_NAME_FIELD,
            "Paddock name field",
            parentLayerParameterName=self.PADDOCKS,
            type=QgsProcessingParameterField.String))
            
        self.addParameter(QgsProcessingParameterFeatureSource(
            self.WATERPOINTS,
            "Water points layer",
            [QgsProcessing.TypeVectorPoint]))
                        
        self.addParameter(QgsProcessingParameterFeatureSink(
            self.OUTPUT,
            "Output layer",
            QgsProcessing.TypeVectorPolygon))
            
        self.addParameter(QgsProcessingParameterFileDestination(
            self.XL_SUMMARY,
            'Carrying capacity summary spreadsheet',
            'Microsoft Excel (*.xlsx);;Open Document Spreadsheet (*.ods)'))
 
    def processAlgorithm(self, parameters, context, feedback):
        results = {}
        
        lt_lyr = self.parameterAsSource(parameters, self.LAND_TYPES, context)
        lt_field_names = self.parameterAsFields(parameters, self.OUTPUT_FIELDS, context)
        lt_name_fld = self.parameterAsFields(parameters, self.LAND_TYPE_FIELD, context)[0]
        pdk_lyr = self.parameterAsSource(parameters, self.PADDOCKS, context)
        pdk_name_fld = self.parameterAsFields(parameters, self.PDK_NAME_FIELD, context)[0]
        wpt_lyr = self.parameterAsSource(parameters, self.WATERPOINTS, context)

        dest_spreadsheet = parameters[self.XL_SUMMARY]
        
        # Fields with these names will be added to output layer and their values calculated
        STANDARD_ADDITIONAL_FIELD_NAMES = ['ID', 'Paddock', 'Land_Type', 'Pdk_LT_area_km2', '3km_WA_LT_area_km2', '5km_WA_LT_area_km2', 'Watered_LT_area', 'Pcnt_LT_watered',]
        
        # Remove any of the fields selected to be copied if they have the same name as any of our standard fields
        lt_fields = [fld_name for fld_name in lt_field_names if (fld_name not in STANDARD_ADDITIONAL_FIELD_NAMES and fld_name != lt_name_fld)]
        
        # Construct list of field indexes from output field names
        lt_field_indexes = [lt_lyr.fields().lookupField(fld) for fld in lt_fields]
        
        # Create a QgsSpatialIndex from land type layer
        land_types_index = QgsSpatialIndex(lt_lyr.getFeatures())
        
        # Create a single geometry object comprising all property paddocks
        all_pdks = QgsGeometry.unaryUnion([f.geometry() for f in pdk_lyr.getFeatures()])
        
        req = land_types_index.intersects(self.transformedRect(all_pdks.boundingBox(), pdk_lyr.sourceCrs(), lt_lyr.sourceCrs(), context.project()))
        
        if not pdk_lyr.sourceCrs().isGeographic():
            if wpt_lyr.sourceCrs() != pdk_lyr.sourceCrs():
                wpt_lyr = wpt_lyr.materialize(QgsFeatureRequest().setDestinationCrs(pdk_lyr.sourceCrs(), context.transformContext()))
            if lt_lyr.sourceCrs() != pdk_lyr.sourceCrs():
                lt_lyr = lt_lyr.materialize(QgsFeatureRequest(req).setDestinationCrs(pdk_lyr.sourceCrs(), context.transformContext()))
        if not wpt_lyr.sourceCrs().isGeographic():
            if pdk_lyr.sourceCrs() != wpt_lyr.sourceCrs():
                pdk_lyr = pdk_lyr.materialize(QgsFeatureRequest().setDestinationCrs(wpt_lyr.sourceCrs(), context.transformContext()))
            if lt_lyr.sourceCrs() != wpt_lyr.sourceCrs():
                lt_lyr = lt_lyr.materialize(QgsFeatureRequest(req).setDestinationCrs(wpt_lyr.sourceCrs(), context.transformContext()))
        if not lt_lyr.sourceCrs().isGeographic():
            lt_lyr = lt_lyr.materialize(QgsFeatureRequest(req))
            if pdk_lyr.sourceCrs() != lt_lyr.sourceCrs():
                pdk_lyr = pdk_lyr.materialize(QgsFeatureRequest().setDestinationCrs(lt_lyr.sourceCrs(), context.transformContext()))
            if wpt_lyr.sourceCrs() != lt_lyr.sourceCrs():
                wpt_lyr = wpt_lyr.materialize(QgsFeatureRequest().setDestinationCrs(lt_lyr.sourceCrs(), context.transformContext()))
        
        if (pdk_lyr.sourceCrs().isGeographic()) and (wpt_lyr.sourceCrs().isGeographic()) and (lt_lyr.sourceCrs().isGeographic()):
            pdk_lyr = pdk_lyr.materialize(QgsFeatureRequest().setDestinationCrs(QgsCoordinateReferenceSystem('epsg:9473'), context.transformContext()))
            wpt_lyr = wpt_lyr.materialize(QgsFeatureRequest().setDestinationCrs(QgsCoordinateReferenceSystem('epsg:9473'), context.transformContext()))
            lt_lyr = lt_lyr.materialize(QgsFeatureRequest(req).setDestinationCrs(QgsCoordinateReferenceSystem('epsg:9473'), context.transformContext()))
        
        flds = QgsFields()
        
        flds_to_add = [QgsField('ID', QVariant.String),
                        QgsField('Paddock', QVariant.String),
                        QgsField('Land_Type', QVariant.String),
                        QgsField('Pdk_LT_area_km2', QVariant.Double, len=10, prec=5),
                        QgsField('3km_WA_LT_area_km2', QVariant.Double, len=10, prec=5),
                        QgsField('5km_WA_LT_area_km2', QVariant.Double, len=10, prec=5),
                        QgsField('Watered_LT_area', QVariant.Double, len=10, prec=5),
                        QgsField('Pcnt_LT_watered', QVariant.Double, len=10, prec=1)]
                
        for fld in flds_to_add:
            flds.append(fld)
        for fld in lt_lyr.fields():
            if fld.name() in lt_fields:
                flds.append(fld)
        
        (sink, dest_id) = self.parameterAsSink(parameters, self.OUTPUT, context,
                                               flds, pdk_lyr.wkbType(), pdk_lyr.sourceCrs())
                                               

        output_features = []

        ID = 1

        for pdk in pdk_lyr.getFeatures():
            PADDOCK_NAME = pdk[pdk_name_fld] if pdk[pdk_name_fld] != NULL else 'Un-named paddock'
            pdk_geom = pdk.geometry()
            pdk_wpts = [ft for ft in wpt_lyr.getFeatures() if ft.geometry().intersects(pdk_geom)]
            buffers_3km = [ft.geometry().buffer(3000, 25) for ft in pdk_wpts]
            dissolved_3km_buffers = QgsGeometry.unaryUnion(buffers_3km)
            pdk_3km_wa = dissolved_3km_buffers.intersection(pdk_geom)
            buffers_5km = [ft.geometry().buffer(5000, 25) for ft in pdk_wpts]
            dissolved_5km_buffers = QgsGeometry.unaryUnion(buffers_5km)
            pdk_5km_wa = dissolved_5km_buffers.intersection(pdk_geom)
            
            pdk_lt_names = [ft[lt_name_fld] for ft in lt_lyr.getFeatures() if ft.geometry().intersects(pdk_geom)]
            
            for LAND_TYPE_NAME in pdk_lt_names:
                land_type_features = [ft for ft in lt_lyr.getFeatures() if ft[lt_name_fld] == LAND_TYPE_NAME]
                if not land_type_features:
                    continue
                # Copy attribute in source feature for each field in fields selected to be copied
                land_type_atts = [land_type_features[0][fld_name] for fld_name in lt_fields]
                
                lt_multipart_geom = QgsGeometry.collectGeometry([ft.geometry() for ft in land_type_features])
                lt_in_pdk = lt_multipart_geom.intersection(pdk_geom)
                PDK_LT_AREA = lt_in_pdk.area()
                pdk_3km_wa_lt = lt_in_pdk.intersection(pdk_3km_wa)
                PDK_3KM_WA_LT_AREA = pdk_3km_wa_lt.area()
                pdk_5km_wa_lt = lt_in_pdk.intersection(pdk_5km_wa)
                PDK_5KM_WA_LT_AREA = pdk_5km_wa_lt.area()
                # We use 50% of the area between 3 and 5km from water so...
                # subtract 3km wa from 5km wa to get 3-5km wa as a band, divide it by 2 then add it back to the 3km wa
                WATERED_LT_AREA = ((PDK_5KM_WA_LT_AREA-PDK_3KM_WA_LT_AREA)/2)+PDK_3KM_WA_LT_AREA
                PCNT_LT_WATERED = (WATERED_LT_AREA/PDK_LT_AREA)*100
                
                output_attributes = [ID,
                                    PADDOCK_NAME,
                                    LAND_TYPE_NAME,
                                    round(PDK_LT_AREA/1000000, 5),
                                    round(PDK_3KM_WA_LT_AREA/1000000, 5),
                                    round(PDK_5KM_WA_LT_AREA/1000000, 5),
                                    round(WATERED_LT_AREA/1000000, 5),
                                    round(PCNT_LT_WATERED, 1)]
                
                for att in land_type_atts:
                    output_attributes.append(att)
                
                output_feat = QgsFeature(flds)
                output_feat.setGeometry(lt_in_pdk)
                output_feat.setAttributes(output_attributes)
                
                is_dup_geom = False
                for feat in output_features:
                    if feat.geometry().isGeosEqual(output_feat.geometry()):
                        is_dup_geom = True
                if not is_dup_geom:
                    output_features.append(output_feat)
                
                    ID+=1
        
        sink.addFeatures(output_features)
        
        results[self.OUTPUT] = dest_id
        
        save_2_xlsx_params = {'LAYERS':[dest_id],
            'USE_ALIAS':False,
            'FORMATTED_VALUES':False,
            'OUTPUT':dest_spreadsheet,
            'OVERWRITE':True}
            
        results['summary_spreadsheet'] = processing.run("native:exporttospreadsheet", save_2_xlsx_params, context=context, feedback=feedback, is_child_algorithm=True)['OUTPUT']
        
#        return results
        return {'Copied attributes': land_type_atts}
        
    def transformedRect(self, extent, src_crs, dest_crs, project):
        # Copy geometry
        bb = QgsGeometry().fromRect(extent).boundingBox()
        xform = QgsCoordinateTransform(src_crs, dest_crs, project)
        xform.transformBoundingBox(bb)
        return bb
        
        