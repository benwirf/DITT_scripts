from qgis.PyQt.QtCore import QCoreApplication, QVariant
from qgis.core import (QgsProcessingAlgorithm,
                        QgsProcessing,
                        QgsProcessingParameterFeatureSource,
                        QgsProcessingParameterRasterDestination)
                        
import processing
                       
class ExAlgo(QgsProcessingAlgorithm):
    INPUT = 'INPUT'
    OUTPUT = 'OUTPUT'
 
    def __init__(self):
        super().__init__()
 
    def name(self):
        return "exalgo"
     
    def tr(self, text):
        return QCoreApplication.translate("exalgo", text)
         
    def displayName(self):
        return self.tr("Use tin interp")
 
    def group(self):
        return self.tr("Examples")
 
    def groupId(self):
        return "examples"
 
    def shortHelpString(self):
        return self.tr("Example script without logic")
 
    def helpUrl(self):
        return "https://qgis.org"
         
    def createInstance(self):
        return type(self)()
   
    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterFeatureSource(
            self.INPUT,
            self.tr("Input layer"),
            [QgsProcessing.TypeVectorPolygon]))

        self.addParameter(QgsProcessingParameterRasterDestination(
            self.OUTPUT,
            self.tr("Output raster")))

    def processAlgorithm(self, parameters, context, feedback):
        out_ras = self.parameterAsOutputLayer(parameters, self.OUTPUT, context)
        
        params1 = {'INPUT':parameters[self.INPUT],
                    'STRATEGY':0,
                    'VALUE':100,
                    'MIN_DISTANCE':0.1,
                    'OUTPUT':'TEMPORARY_OUTPUT'}
        rand_pts = processing.run("qgis:randompointsinsidepolygons", params1, context=context, feedback=feedback, is_child_algorithm=True)['OUTPUT']

        params2 = {'INPUT':rand_pts,
                    'FIELD_NAME':'INTERP',
                    'FIELD_TYPE':1,
                    'FIELD_LENGTH':3,
                    'FIELD_PRECISION':0,
                    'FORMULA':'rand(1, 100)',
                    'OUTPUT':'TEMPORARY_OUTPUT'}
                    
        fld_calc = processing.run("native:fieldcalculator", params2, context=context, feedback=feedback, is_child_algorithm=True)['OUTPUT']
        #fld_calc_lyr = context.getMapLayer(fld_calc)

        params3 = {'INTERPOLATION_DATA':f'{fld_calc}::~::0::~::1::~::0',
                    'METHOD':0,
                    'EXTENT':'131.881193298,132.997064303,-13.996373726,-12.094533450 [EPSG:4326]',
                    'PIXEL_SIZE':0.1,
                    'OUTPUT':out_ras}
        processing.run("qgis:tininterpolation", params3, context=context, feedback=feedback, is_child_algorithm=True)

        return {'Temp_Layer': fld_calc}