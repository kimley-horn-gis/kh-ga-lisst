"""
Author: Colin T. Stiles, GISP
Version: 0.2
Last Edited Date: 2025-05-01
Description: This script is the only tool within the KH GA LISST toolbox.
GA LISST is the acronym for the Georgia Low Impact for Solar Siting Tool. More information for the LISST can be found here
(https://www.nature.org/en-us/about-us/where-we-work/united-states/georgia/stories-in-georgia/low-impact-solar-renewable-energy/?vu=georgiasolar).

This script is designed to retrieve the GA LISST data from the REST, convert the raster data into a polygon layer, clip the dataset to within a project's boundary, 
and calculate acreages for each of the LISST's ranks.

The ranks defined by the LISST are as follows:
    - "Most preferred for low impact"
    - "Less preferred for low impact"
    - "Not preferred for low impact"
    - "Avoidance recommended"

Args:
    in_boundary (GPFeatureLayer):
        Input feature layer or shapefile representing the project boundary.  Must be a polygon.
    output_folder (DEFolder, optional):
        Path to the folder where output files will be saved.
        If not provided, a folder named "ga_lisst_layers" will be created
        in the project's home folder.  Defaults to None.

Returns:
    GPFeatureLayer: The output polygon feature layer with acreage calculations for each LISST rank.
"""

# Import system modules
import arcpy
import os
import traceback

class Toolbox:
    """Retrieve and process the GA LISST dataset."""

    def __init__(self):
        """Define the tool's properties."""
        self.label = "GA LISST"
        self.alias = "GALISST"
        self.description = "Retrieves the Georgia Low Impact for Solar Siting Tool data for the input site boundary and calculates acreages for each rank."
        self.canRunInBackground = True
        self.category = "Process GA LISST"
        
        # List of tool classes associated with this toolbox
        self.tools = [ProcessLISST]

class ProcessLISST(object):
    """Retrieve and process the GA LISST dataset."""

    def __init__(self):
        """Define the tool's properties."""
        self.label = "GA LISST"
        self.alias = "GALISST"
        self.description = "Retrieves the Georgia Low Impact for Solar Siting Tool data for the input site boundary and calculates acreages for each rank."
        self.canRunInBackground = True
        self.category = "Process GA LISST"

    def getParameterInfo(self):
        """Define parameter definitions."""
        # Input Site Boundary
        param0 = arcpy.Parameter(
            displayName="Input Site Boundary",
            name="in_boundary",
            datatype="GPFeatureLayer",
            parameterType="Required",
            direction="Input",
        )
        param0.filter.list = ["Polygon"]  # Only allow polygons
        

        # Output folder (optional)
        param1 = arcpy.Parameter(
            displayName="Output Folder",
            name="output_folder",
            datatype="DEFolder",
            parameterType="Optional",
            direction="Input",
        )

        # Output LISST Polygon
        param2 = arcpy.Parameter(
            displayName="LISST Polygon",
            name="ga_lisst_polygon",
            datatype="GPFeatureLayer",
            parameterType="Derived",
            direction="Output",
        )
        param2.value = None  # Initialize
        param2.symbology = os.path.join(os.path.dirname(__file__), "symb", "GA_LISST.lyrx")

        params = [param0, param1, param2]
        return params

    def isLicensed(self):
        """Set whether the tool is licensed to execute."""
        # Check for Spatial Analyst extension
        if arcpy.CheckExtension("Spatial") == "Available":
            return True
        else:
            return False

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal validation is performed.
        This method is called whenever a parameter has been changed."""

        # If no output folder is specified, set the default output folder
        if not parameters[1].altered:
            # Use the project's home folder if available
            try:
                aprx = arcpy.mp.ArcGISProject("CURRENT")
                if aprx.filePath:
                    project_home_folder = os.path.dirname(aprx.filePath)
                    default_output_folder = os.path.join(project_home_folder, "ga_lisst_layers")
                    parameters[1].value = default_output_folder
                    # Create the default output directory if it does not exist
                    if not os.path.exists(default_output_folder):
                        try:
                            os.makedirs(default_output_folder)
                        except OSError as e:
                            arcpy.AddError(f"Failed to create output directory: {e}")
                            parameters[1].value = ""  # Reset the parameter value
                else:
                    arcpy.AddWarning("No project file found. Output files will be saved to a default location.")
            except Exception:
                pass  # Fallback to default behavior if "CURRENT" fails

        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool parameter.
        This method is called after internal validation."""

        # Input boundary checks
        if parameters[0].altered:
            if parameters[0].value:
                desc = arcpy.Describe(parameters[0].value)
                if desc.dataType not in ["FeatureClass", "Shapefile", "FeatureLayer"]:
                    parameters[0].setErrorMessage("Input must be a feature class, feature layer, or shapefile.")
                elif desc.shapeType != "Polygon":
                    parameters[0].setErrorMessage("Input must be a polygon.")
        return

    def execute(self, parameters, messages):
        """The source code of the tool."""

        in_boundary = parameters[0].valueAsText
        output_folder = parameters[1].valueAsText
        ga_lisst_polygon_param = parameters[2]  # Get the parameter *object*

        result = self.get_lisst(in_boundary, output_folder, ga_lisst_polygon_param)

        if result is None:
            arcpy.AddError("LISST Processing failed.")
            return  # Important: Exit if processing failed
        elif isinstance(result, dict) and "out_lisst_polygon" in result:
            # Correctly set the output parameter's value
            ga_lisst_polygon_param.value = result["out_lisst_polygon"]
        else:
            arcpy.AddError(f"Unexpected result type: {type(result)}. Check the get_lisst function.")
            return  # Important: Exit if the result is unexpected

    @staticmethod
    def get_project_home_folder():
        """Get the project's home folder."""
        try:
            aprx = arcpy.mp.ArcGISProject("CURRENT")
            if aprx.filePath:
                return os.path.dirname(aprx.filePath)
            else:
                return None
        except Exception:
            arcpy.AddError("Unable to access the current ArcGIS Pro project. Are you running this tool within ArcGIS Pro?")
            return None

    @staticmethod
    def get_lisst(in_boundary, output_folder, ga_lisst_polygon_param):
        """Retrieve GA LISST data and process to calculate acreages.

        Args:
            in_boundary (str): Path to the input boundary feature class.
            output_folder (str, optional): Path to the output folder. Defaults to None.
            ga_lisst_polygon_param (arcpy.Parameter): The output parameter object.
        Returns:
            dict: A dictionary containing the path to the output polygon, or None on failure.
        """
        # Determine the project's home folder
        project_home_folder = ProcessLISST.get_project_home_folder()
        if not project_home_folder:
            return None

        # Create a new folder for output layers if not provided
        if not output_folder:
            output_folder = os.path.join(project_home_folder, "ga_lisst_layers")
        try:
            os.makedirs(output_folder, exist_ok=True)
            arcpy.AddMessage(f"Workspace: {output_folder} created for storing output files.")
        except Exception as e:
            arcpy.AddError(f"Error creating output folder: {e}")
            return None

        arcpy.env.workspace = output_folder
        arcpy.env.overwriteOutput = True

        # Check out Spatial Analyst extension
        if arcpy.CheckExtension("Spatial") == "Available":
            arcpy.CheckOutExtension("Spatial")
        else:
            arcpy.AddError("Spatial Analyst extension is not available.")
            return None

        # Set the output coordinate system
        try:
            desc = arcpy.Describe(in_boundary)
            arcpy.env.outputCoordinateSystem = desc.spatialReference
            arcpy.AddMessage(f"Output spatial reference set to: {arcpy.env.outputCoordinateSystem.name}")
        except Exception as e:
            arcpy.AddError(f"Error getting input boundary spatial reference: {e}")
            return None  # Exit if we can't set the coordinate system.

        # Define output names *within* the output folder
        out_temp_raster_path = os.path.join(output_folder, "lisst_clip_temp.tif")
        out_temp_polygon_path = os.path.join(output_folder, "lisst_poly_temp.shp")
        out_clip_polygon_path = os.path.join(output_folder, "lisst_clip_poly.shp")
        out_lisst_polygon_path = os.path.join(output_folder, "lisst_polygon.shp")

        # Define REST endpoint
        ga_lisst_rest = "https://tiledimageservices.arcgis.com/F7DSX1DSNSiWmOqh/arcgis/rest/services/OverallPref_Nov2023_createhostedimagery/ImageServer"

        # Check if LISST REST is valid
        arcpy.AddMessage(f"Checking GA LISST REST service...")
        try:
            desc = arcpy.Describe(ga_lisst_rest)
            arcpy.AddMessage(f"GA LISST REST service appears valid and accessible.")
        except Exception as desc_err:
            arcpy.AddError(f"GA LISST REST service is not available or valid: {desc_err}")
            return None

        # --- GA LISST Processing --- #
        arcpy.AddMessage(f"Processing GA LISST data...")

        # Set processing extent and snap raster
        arcpy.AddMessage(f"Setting processing extent...")

        try:
            with arcpy.EnvManager(extent=in_boundary, snapRaster=ga_lisst_rest, cellSize=ga_lisst_rest):
                # Create a 100ft buffer around the input boundary
                arcpy.AddMessage(f"Buffering the input boundary by 100ft...")
                buffered_boundary = arcpy.analysis.Buffer(in_boundary, "memory\\buffered_boundary", "100 Feet")

                # Clip the raster to the buffer
                arcpy.AddMessage(f"Clipping the LISST raster to the buffer...")
                raster_clip = arcpy.sa.ExtractByMask(ga_lisst_rest, buffered_boundary)

                # Save the temporary clipped raster
                arcpy.AddMessage(f"Saving temporary clipped raster to: {out_temp_raster_path}")
                raster_clip.save(out_temp_raster_path)

                # Convert raster to polygon
                arcpy.AddMessage(f"Converting the LISST raster to a polygon feature layer...")
                arcpy.conversion.RasterToPolygon(out_temp_raster_path, out_temp_polygon_path, "NO_SIMPLIFY", "Rank")

                # Clip the polygon to the original boundary
                arcpy.AddMessage(f"Clipping the polygon to the original input boundary...")
                arcpy.analysis.Clip(out_temp_polygon_path, in_boundary, out_clip_polygon_path)

                # Dissolve based on Rank field
                arcpy.AddMessage(f"Dissolving the polygon based on Rank field...")
                arcpy.Dissolve_management(out_clip_polygon_path, out_lisst_polygon_path, "Rank")

                # Caculate new ACRES field
                arcpy.AddMessage(f"Calculating acreages for each rank...")
                # Add a field to store area in acres
                arcpy.AddField_management(out_lisst_polygon_path, "ACRES", "DOUBLE")
                arcpy.CalculateField_management(out_lisst_polygon_path, "ACRES", "!shape.area@ACRES!", "PYTHON3")

                # Delete the temp layers
                arcpy.AddMessage(f"Deleting the temporary layers...")
                arcpy.management.Delete(out_temp_polygon_path)
                arcpy.management.Delete(out_temp_raster_path)
                arcpy.management.Delete(out_clip_polygon_path)
                arcpy.management.Delete(buffered_boundary)

                arcpy.AddMessage(f"LISST data processed successfully. Output polygon: {out_lisst_polygon_path}")

        except IOError as e:
            arcpy.AddError(f"File/Service Access Error: {str(e)}")
            return None
        except ValueError as e:
            arcpy.AddError(f"Input Value Error: {str(e)}")
            return None
        except arcpy.ExecuteError:
            msgs = arcpy.GetMessages(2)
            arcpy.AddError("ArcPy Execution Error:")
            arcpy.AddError(msgs)
            arcpy.AddWarning(arcpy.GetMessages(1))
            arcpy.AddMessage(arcpy.GetMessages(0))
            return None
        except Exception as e:
            arcpy.AddError(f"An unexpected error occurred: {type(e).__name__} - {e}")
            arcpy.AddError(traceback.format_exc())  # Log the full traceback
            return None

        return {
            "out_lisst_polygon": out_lisst_polygon_path,
        }