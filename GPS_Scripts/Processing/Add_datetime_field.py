from processing.gui.wrappers import WidgetWrapper
from qgis.PyQt.QtWidgets import (QWidget, QComboBox, QLabel, QPushButton,
                                QTableWidget, QHBoxLayout, QTableWidgetItem,
                                QVBoxLayout)
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtCore import (QCoreApplication, Qt, QVariant, QDate, QDateTime)
from qgis.core import (QgsField, QgsFeature, QgsFeatureSink, QgsFeatureRequest,
                        QgsFields, QgsProcessing, QgsProcessingAlgorithm,
                        QgsProcessingParameterFeatureSource,
                        QgsProcessingParameterField,
                        QgsProcessingParameterString,
                        QgsProcessingParameterFeatureSink)
from datetime import datetime
                       
class AddDateTimeField(QgsProcessingAlgorithm):
    INPUT = 'INPUT'
    DATE_FIELD = 'DATE_FIELD'
    DATE_STRING_FORMAT = 'DATE_STRING_FORMAT'
    TIME_FIELD = 'TIME_FIELD'
    TIME_STRING_FORMAT = 'TIME_STRING_FORMAT'
    OUTPUT = 'OUTPUT'
 
    def __init__(self):
        super().__init__()
 
    def name(self):
        return "adddatetimefield"
         
    def displayName(self):
        return "Add date time field"
 
    def group(self):
        return "GPS Collars"
 
    def groupId(self):
        return "gps_collars"
 
    def shortHelpString(self):
        return "Add a QDateTime field from a string field containing date/time information"
 
    def helpUrl(self):
        return "https://qgis.org"
         
    def createInstance(self):
        return type(self)()
   
    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterFeatureSource(
            self.INPUT,
            "Input layer",
            [QgsProcessing.TypeVectorAnyGeometry]))
        
        ########DATE FIELD##############################################
        self.addParameter(QgsProcessingParameterField(
            self.DATE_FIELD,
            "Field containing date string",
            parentLayerParameterName=self.INPUT,
            type=QgsProcessingParameterField.String))
        
        format_param = QgsProcessingParameterString(self.DATE_STRING_FORMAT, 'Date String Format')
        format_param.setMetadata({'widget_wrapper': {'class': CustomParametersWidgetWrapper}})
        self.addParameter(format_param)
        #################################################################
        
        ########TIME FIELD##############################################
        self.addParameter(QgsProcessingParameterField(
            self.TIME_FIELD,
            "Field containing time string",
            parentLayerParameterName=self.INPUT,
            type=QgsProcessingParameterField.String))
        
        format_param = QgsProcessingParameterString(self.TIME_STRING_FORMAT, 'Time String Format')
        format_param.setMetadata({'widget_wrapper': {'class': CustomParametersWidgetWrapper}})
        self.addParameter(format_param)
        #################################################################
            
        self.addParameter(QgsProcessingParameterFeatureSink(
            self.OUTPUT,
            "Output layer",
            QgsProcessing.TypeVectorAnyGeometry))
 
    def processAlgorithm(self, parameters, context, feedback):
        source = self.parameterAsSource(parameters, self.INPUT, context)
        date_fields = self.parameterAsFields(parameters, self.DATE_FIELD, context)
        date_string_field = date_fields[0]# This is a string literal, not a QgsField object
        date_format = self.parameterAsString(parameters, self.DATE_STRING_FORMAT, context)
        ###
        time_fields = self.parameterAsFields(parameters, self.TIME_FIELD, context)
        time_string_field = time_fields[0]# This is a string literal, not a QgsField object
        time_format = self.parameterAsString(parameters, self.TIME_STRING_FORMAT, context)
        ###
        flds = [fld for fld in source.fields()]
        new_fld_idx = source.fields().lookupField(date_string_field)+1
        datetime_field = QgsField('q_datetime', QVariant.DateTime)
        flds.insert(new_fld_idx, datetime_field)
        output_flds = QgsFields()
        for fld in flds:
            output_flds.append(fld)
        (sink, dest_id) = self.parameterAsSink(parameters, self.OUTPUT, context,
                                               output_flds, source.wkbType(), source.sourceCrs())
        
        all_feats = []
        
        src_feat_count = source.featureCount()
        for i, ft in enumerate(source.getFeatures()):
            if feedback.isCanceled():
                break
            pcnt = ((i+1)/src_feat_count)*100
            feedback.setProgress(round(pcnt, 1))
            feat = QgsFeature(output_flds)
            feat.setGeometry(ft.geometry())
            atts = [att for att in ft.attributes()]
            #Parse DateTime###########################################
            if date_string_field == time_string_field:
                # Date and Time are both in a single field e.g. '2023-05-10 05:57:34Z'
                # So we can parse a datetime object from either input
                dt = datetime.strptime(ft[date_string_field], date_format)                
            elif date_string_field != time_string_field:
                # Date and time info is in separate fields
                # So we need to parse separately then combine
                dd = datetime.strptime(ft[date_string_field], date_format)
                tt = datetime.strptime(ft[time_string_field], time_format)
                dt = datetime.combine(dd.date(), tt.time())
            qdtd = QDateTime(dt)
            #########################################################
            atts.insert(new_fld_idx, qdtd)
            feat.setAttributes(atts)
            all_feats.append(feat)
        
        sink.addFeatures(all_feats)
        
        return {self.OUTPUT: dest_id}
                
class CustomParametersWidgetWrapper(WidgetWrapper):
    def createWidget(self):
        self.cfw = CustomFormatWidget()
        return self.cfw
        
    def value(self):
        return self.cfw.getFormat()

class CustomFormatWidget(QWidget):
    def __init__(self):
        super(CustomFormatWidget, self).__init__()
        self.setGeometry(500, 300, 500, 200)
        #self.format_cb_lbl = QLabel('Date String Format', self)
        self.format_cb = QComboBox(self)
        self.format_cb.addItems(self.common_formats())
        self.format_cb.setEditable(True)
        self.help_btn = QPushButton(QIcon(":images/themes/default/propertyicons/metadata.svg"), '', self)
        self.help_btn.setToolTip('Get Help')
        self.layout = QHBoxLayout(self)
        #self.layout.addWidget(self.format_cb_lbl)
        self.layout.addWidget(self.format_cb, 1)
        self.layout.addWidget(self.help_btn)
        
        self.help_widget = HelpWidget(self)
        self.help_btn.clicked.connect(lambda: self.help_widget.show())
    
    def common_formats(self):
        return ['%Y-%m-%d %H:%M:%SZ',
                '%d/%m/%Y %H:%M:%S',
                '%d-%m-%Y',
                '%d/%m/%Y',
                '%Y-%m-%d',
                '%Y/%m/%d',
                '%H:%M:%S']
                
    def getFormat(self):
        return self.format_cb.currentText()
        
        
class HelpWidget(QWidget):
    def __init__(self, parent=None):
        super(HelpWidget, self).__init__()
        self.help_label = QLabel('See table below for common date/time strings \n\
        and corresponding datetime formats', self)
        self.rows = [['2022-05-18 20:35:20Z', '%Y-%m-%d %H:%M:%SZ'],
                    ['18/05/2022 00:06:02', '%d/%m/%Y %H:%M:%S'],
                    ['18-05-2022', '%d-%m-%Y'],
                    ['18/05/2022', '%d/%m/%Y'],
                    ['2022-05-18', '%Y-%m-%d'],
                    ['2022/05/18', '%Y/%m/%d'],
                    ['06:10:45', '%H:%M:%S']]
        self.tbl = QTableWidget()
        self.tbl.setColumnCount(2)
        self.tbl.setRowCount(7)
        self.tbl.setHorizontalHeaderLabels(['String Format', 'DateTime Format'])
        for row in range(self.tbl.rowCount()):
            for col in range(self.tbl.columnCount()):
                item = QTableWidgetItem(self.rows[row][col])
                self.tbl.setItem(row, col, item)
        self.tbl.resizeColumnsToContents()
        self.tbl.setStyleSheet('color: blue')
        self.setMinimumWidth(self.tbl.columnWidth(0)+self.tbl.columnWidth(1)+50)
        self.layout = QVBoxLayout(self)
        self.layout.addWidget(self.help_label, alignment=Qt.AlignCenter)
        self.layout.addWidget(self.tbl)