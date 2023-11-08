# -*- coding: utf-8 -*-

import arcpy
from patterns.tools import PatternsTool



class Toolbox(object):
    def __init__(self):
        self.label = "Green Spatial Tools"
        self.alias = "greenspatial_tools"

        # List of tool classes associated with this toolbox
        self.tools = [DetectPatternsTool]


class DetectPatternsTool(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Detect and Quantify patterns"
        self.description = "Detecting and quantifying spatial patterns"
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define parameter definitions"""
        workspace_param = arcpy.Parameter(
            name="workspace_dir",
            datatype="DEFolder",
            displayName="Output folder",
            direction="Input",
            parameterType="Required"
        )
        workspace_param.value = "/arcgis/home/traffic"

        analysis_result_param = arcpy.Parameter(
            name="analysis_result",
            datatype="GPFeatureLayer",
            displayName="Emerging HotSpot Analysis Result",
            direction="Derived",
            parameterType="Output"
        )
        analysis_result_param.value = "SpaceTimeCube_EmergingHotSpotAnalysis"
        return [workspace_param, analysis_result_param]

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""
        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""
        return

    def execute(self, parameters, messages):
        """The source code of the tool."""
        feature_class = "traffic_data"
        workspace_dir = parameters[0].valueAsText
        messages.AddMessage(f"Detecting and quantifying spatial patterns of {feature_class} from {workspace_dir}...")
        
        patterns_tool = PatternsTool()
        patterns_tool.run(feature_class, workspace_dir)

        messages.AddMessage("Detection succeeded.")

    def postExecute(self, parameters):
        """This method takes place after outputs are processed and
        added to the display."""
        return
