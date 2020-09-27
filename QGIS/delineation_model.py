"""
Model exported as python.
Name : WBT
Group : 
With QGIS : 31416
"""

from qgis.core import QgsProcessing
from qgis.core import QgsProcessingAlgorithm
from qgis.core import QgsProcessingMultiStepFeedback
from qgis.core import QgsProcessingParameterRasterLayer
from qgis.core import QgsProcessingParameterNumber
from qgis.core import QgsProcessingParameterMapLayer
from qgis.core import QgsProcessingParameterVectorDestination
from qgis.core import QgsProcessingParameterRasterDestination
from qgis.core import QgsCoordinateReferenceSystem
import processing


class Wbt(QgsProcessingAlgorithm):

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterRasterLayer('DEM', 'DEM', defaultValue=None))
        self.addParameter(QgsProcessingParameterNumber('Streamtreshold', 'Stream_treshold', type=QgsProcessingParameterNumber.Integer, minValue=-3, maxValue=10, defaultValue=1))
        self.addParameter(QgsProcessingParameterMapLayer('pour', 'pour', defaultValue=None, types=[QgsProcessing.TypeVectorPoint]))
        self.addParameter(QgsProcessingParameterVectorDestination('Watershed', 'Watershed', type=QgsProcessing.TypeVectorPolygon, createByDefault=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterRasterDestination('Streams', 'Streams', createByDefault=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterVectorDestination('Snapped', 'snapped', type=QgsProcessing.TypeVectorPoint, createByDefault=True, defaultValue=None))

    def processAlgorithm(self, parameters, context, model_feedback):
        # Use a multi-step feedback, so that individual child algorithm progress reports are adjusted for the
        # overall progress through the model
        feedback = QgsProcessingMultiStepFeedback(11, model_feedback)
        results = {}
        outputs = {}

        # Rectangles, ovals, diamonds
        alg_params = {
            'HEIGHT': 2,
            'INPUT': parameters['pour'],
            'ROTATION': 0,
            'SEGMENTS': 5,
            'SHAPE': 0,
            'WIDTH': 2,
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['RectanglesOvalsDiamonds'] = processing.run('native:rectanglesovalsdiamonds', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(1)
        if feedback.isCanceled():
            return {}

        # ClipRasterToPolygon
        alg_params = {
            'input': parameters['DEM'],
            'maintain_dimensions': False,
            'polygons': outputs['RectanglesOvalsDiamonds']['OUTPUT'],
            'output': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['Cliprastertopolygon'] = processing.run('wbt:ClipRasterToPolygon', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(2)
        if feedback.isCanceled():
            return {}

        # Assign projection
        alg_params = {
            'CRS': QgsCoordinateReferenceSystem('EPSG:4326'),
            'INPUT': outputs['Cliprastertopolygon']['output']
        }
        outputs['AssignProjection'] = processing.run('gdal:assignprojection', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(3)
        if feedback.isCanceled():
            return {}

        # Assign projection
        alg_params = {
            'CRS': QgsCoordinateReferenceSystem('EPSG:4326'),
            'INPUT': outputs['RectanglesOvalsDiamonds']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['AssignProjection'] = processing.run('native:assignprojection', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(4)
        if feedback.isCanceled():
            return {}

        # BreachDepressions
        alg_params = {
            'dem': outputs['Cliprastertopolygon']['output'],
            'fill_pits': False,
            'flat_increment': None,
            'max_depth': None,
            'max_length': None,
            'output': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['Breachdepressions'] = processing.run('wbt:BreachDepressions', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(5)
        if feedback.isCanceled():
            return {}

        # FillDepressions
        alg_params = {
            'dem': outputs['Breachdepressions']['output'],
            'fix_flats': True,
            'flat_increment': None,
            'max_depth': None,
            'output': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['Filldepressions'] = processing.run('wbt:FillDepressions', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(6)
        if feedback.isCanceled():
            return {}

        # FlowAccumulationFullWorkflow
        alg_params = {
            'clip': False,
            'dem': outputs['Filldepressions']['output'],
            'esri_pntr': False,
            'log': False,
            'out_type': 1,
            'out_accum': QgsProcessing.TEMPORARY_OUTPUT,
            'out_dem': QgsProcessing.TEMPORARY_OUTPUT,
            'out_pntr': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['Flowaccumulationfullworkflow'] = processing.run('wbt:FlowAccumulationFullWorkflow', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(7)
        if feedback.isCanceled():
            return {}

        # ExtractStreams
        alg_params = {
            'flow_accum': outputs['Flowaccumulationfullworkflow']['out_accum'],
            'threshold': parameters['Streamtreshold'],
            'zero_background': False,
            'output': parameters['Streams']
        }
        outputs['Extractstreams'] = processing.run('wbt:ExtractStreams', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['Streams'] = outputs['Extractstreams']['output']

        feedback.setCurrentStep(8)
        if feedback.isCanceled():
            return {}

        # SnapPourPoints
        alg_params = {
            'flow_accum': outputs['Flowaccumulationfullworkflow']['out_accum'],
            'pour_pts': parameters['pour'],
            'snap_dist': 0.01,
            'output': parameters['Snapped']
        }
        outputs['Snappourpoints'] = processing.run('wbt:SnapPourPoints', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['Snapped'] = outputs['Snappourpoints']['output']

        feedback.setCurrentStep(9)
        if feedback.isCanceled():
            return {}

        # Watershed
        alg_params = {
            'd8_pntr': outputs['Flowaccumulationfullworkflow']['out_pntr'],
            'esri_pntr': False,
            'pour_pts': outputs['Snappourpoints']['output'],
            'output': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['Watershed'] = processing.run('wbt:Watershed', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(10)
        if feedback.isCanceled():
            return {}

        # Polygonize (raster to vector)
        alg_params = {
            'BAND': 1,
            'EIGHT_CONNECTEDNESS': False,
            'EXTRA': '',
            'FIELD': 'DN',
            'INPUT': outputs['Watershed']['output'],
            'OUTPUT': parameters['Watershed']
        }
        outputs['PolygonizeRasterToVector'] = processing.run('gdal:polygonize', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['Watershed'] = outputs['PolygonizeRasterToVector']['OUTPUT']
        return results

    def name(self):
        return 'WBT'

    def displayName(self):
        return 'WBT'

    def group(self):
        return ''

    def groupId(self):
        return ''

    def createInstance(self):
        return Wbt()
