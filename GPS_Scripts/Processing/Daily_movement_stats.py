from qgis.PyQt.QtCore import QCoreApplication, QVariant
from qgis.core import (QgsField, QgsFeature, QgsFeatureSink, QgsFeatureRequest,
                        QgsProcessing, QgsProcessingAlgorithm,
                        QgsProcessingParameterFeatureSource,
                        QgsProcessingParameterField,
                        QgsProcessingParameterFeatureSink,
                        QgsProcessingParameterFileDestination)
                       
class DailyMovementStats(QgsProcessingAlgorithm):
    INPUT = 'INPUT'
    DATETIME_FIELD = 'DATETIME_FIELD'
    OUTPUT = 'OUTPUT'
    OUTPUT_XL = 'OUTPUT_XL'
 
    def __init__(self):
        super().__init__()
 
    def name(self):
        return "dailymovementstats"
         
    def displayName(self):
        return "Daily movement stats"
 
    def group(self):
        return "GPS Collars"
 
    def groupId(self):
        return "gps_collars"
 
    def shortHelpString(self):
        return "Calculate daily distance walked statistics and write results to\
        a line layer and excel spreadsheet"
 
    def helpUrl(self):
        return "https://qgis.org"
         
    def createInstance(self):
        return type(self)()
   
    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterFeatureSource(
            self.INPUT,
            "Input GPS point layer",
            [QgsProcessing.TypeVectorAnyGeometry]))
            
        self.addParameter(QgsProcessingParameterField(
            self.DATETIME_FIELD,
            'Field containing datetime attribute',
            parentLayerParameterName=self.INPUT,
            type=QgsProcessingParameterField.DateTime))
        
        self.addParameter(QgsProcessingParameterFeatureSink(
            self.OUTPUT,
            "Daily tracks",
            QgsProcessing.TypeVectorLine))
            
        self.addParameter(QgsProcessingParameterFileDestination(
            self.OUTPUT_XL,
            'Output District Spreadsheet',
            'Microsoft Excel (*.xlsx);;Open Document Spreadsheet (*.ods)'))
 
    def processAlgorithm(self, parameters, context, feedback):
        results = {}
        
        source = self.parameterAsSource(parameters, self.INPUT, context)
        
        datetime_fields = self.parameterAsFields(parameters, self.DATETIME_FIELD, context)
        if not datetime_fields:
            return {}
        datetime_field = datetime_fields[0]
        
        (sink, dest_id) = self.parameterAsSink(parameters, self.OUTPUT, context,
                                               source.fields(), source.wkbType(), source.sourceCrs())
        #############################################################
        '''
        features = source.getFeatures(QgsFeatureRequest())
        for feat in features:
            out_feat = QgsFeature()
            out_feat.setGeometry(feat.geometry())
            out_feat.setAttributes(feat.attributes())
            sink.addFeature(out_feat, QgsFeatureSink.FastInsert)
        '''
        ##############################################################
        results[self.OUTPUT] = dest_id
        results[self.OUTPUT_XL] = parameters[self.OUTPUT_XL]# Path to output spreadsheet
        #return results
        return {'DateTime Field': datetime_field}
        