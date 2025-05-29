# GA LISST Toolbox

[![The GA LISST Data](C:\Users\colin.stiles\OneDrive - KH\GitHub\kh-ga-lisst\pics\lisst_thumbnail.png)]

## Overview

The **GA LISST Toolbox** is an ArcGIS Pro toolbox designed to process the Georgia Low Impact for Solar Siting Tool (GA LISST) data. This tool retrieves the GA LISST raster data from a REST service, converts it into a polygon layer, clips the dataset to a user-defined project boundary, and calculates the acreage for each of the LISST's suitability ranks within that boundary.

More information about the GA LISST initiative can be found at [https://www.nature.org/en-us/about-us/where-we-work/united-states/georgia/stories-in-georgia/low-impact-solar-renewable-energy/?vu=georgiasolar](https://www.nature.org/en-us/about-us/where-we-work/united-states/georgia/stories-in-georgia/low-impact-solar-renewable-energy/?vu=georgiasolar).

**LISST Ranks:**

The GA LISST categorizes land suitability for low-impact solar development into the following ranks:

-   "Most preferred for low impact"
-   "Less preferred for low impact"
-   "Not preferred for low impact"
-   "Avoidance recommended"

## Installation

To use the GA LISST Toolbox:

1.  Save the provided folder (e.g., `kh-ga-lisst`) to a location on your computer.
2.  Open ArcGIS Pro.
3.  In the **Catalog** pane, right-click on **Folder** and select **Add Folder Connection** *(Ctrl+Shift+C)*.
4.  Navigate to the location where you saved the `kh-ga-lisst` folder and select it. The `kh-ga-lisst` folder will now be available in your project.
5.  In the **Catalog** pane, right-click on **Toolboxes** and select **Add Toolbox...**.
6.  Navigate to the location where you saved the `.pyt` file and select it. The "GA LISST" toolbox will now be available in your project.

## Tool: GA LISST

This tool performs the core processing of the GA LISST data.

### Parameters

**Input Site Boundary**
(Required)

-   **Data Type:** Feature Layer
-   **Description:** Input feature layer or shapefile representing the project boundary. **Must be a polygon feature class.**

**Output Folder**
(Optional)

-   **Data Type:** Folder
-   **Description:** Path to the folder where the output files will be saved.
-   **Default:** If no folder is provided, a new folder named `ga_lisst_layers` will be created in the home folder of the current ArcGIS Pro project. If no project is open, a default location will be used, with a warning message.

**LISST Polygon**
(Output)

-   **Data Type:** Feature Layer
-   **Description:** The resulting polygon feature layer clipped to the input boundary, with an added field named `ACRES` containing the calculated acreage for each LISST rank. The output layer will be symbolized according to the GA LISST ranks (symbology layer file `GA_LISST.lyrx` should be in the same directory as the toolbox script for automatic application).

### Requirements

-   **ArcGIS Pro:** This toolbox is designed for use within the ArcGIS Pro environment.
-   **Spatial Analyst Extension:** The ArcGIS Pro Spatial Analyst extension is required to run this tool. The tool will check for the availability of this extension and will not execute if it is not licensed.

### How to Use

1.  In ArcGIS Pro, navigate to the **GA LISST** toolbox in the **Catalog** pane.
2.  Double-click the **GA LISST** tool to open its geoprocessing pane.
3.  For the **Input Site Boundary** parameter, browse to and select the polygon feature layer representing your project area.
4.  (Optional) For the **Output Folder** parameter, specify the folder where you want the output files to be saved. If left blank, the default behavior will be used.
5.  Click **Run** to execute the tool.

Once the tool completes successfully, the **LISST Polygon** output feature layer will be added to your map. This layer will show the GA LISST ranks within your project boundary, and its attribute table will contain a field named `ACRES` indicating the area (in acres) for each rank.

### Error Handling and Messages

The tool provides informative messages during its execution:

-   **Warnings:** Indicate potential issues or deviations from the default behavior (e.g., when no ArcGIS Pro project is open and a default output location is used).
-   **Errors:** Indicate failures during the processing steps. Error messages will provide details about the issue encountered.
-   **Messages:** Provide updates on the progress of the tool, such as the creation of output folders, setting of the spatial reference, and the successful completion of processing steps.

If the Spatial Analyst extension is not available, the tool will display an error message and will not proceed. Ensure that you have the necessary license and that the extension is enabled in ArcGIS Pro.

## Version History

**Version:** 0.2
**Last Edited Date:** 2025-05-01
**Author:** Colin T. Stiles, GISP