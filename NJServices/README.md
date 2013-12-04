#NJ Services
Python-based Add-in for ArcGIS Desktop. Adds the following tools to your ArcMap environment:
 
- Open NJ-GeoWeb
- Download 2012 Imagery

You do not need to download any shapefiles or geodatabases for these tools to work. Using Python and available web services, all the necessary data will be pulled in dynamically. 

##Install
Double-click `makeaddin.py` to create the `.esriaddin` file. Double-click the `.esriaddin` file to install the add-in in ArcMap. 

##Usage
A new "NJ Services" toolbar should appear in ArcMap. This toolbar will contain the following tools.

### Open NJ-GeoWeb
[NJ-GeoWeb](http://www.nj.gov/dep/gis/geowebsplash.htm) is the NJ DEP's primary web viewer. You can quickly jump from ArcGIS into NJ-GeoWeb by selecting this tool and drawing a bounding box around your area of interest. A new browser window will open with NJ-GeoWeb at the same extent you selected.

### Download 2012 Imagery
NJ OIT-OGIS has recent aerial imagery available as [a WMS](https://njgin.state.nj.us/NJ_NJGINExplorer/jviewer.jsp?pg=wms_instruct). If you need to quickly download the source .SID files, there's no need to visit [NJGIN](https://njgin.state.nj.us/NJ_NJGINExplorer/IW.jsp?DLayer=NJ%202012%20High%20Resolution%20Orthophotography). From within ArcMap, select this tool and draw a bounding box around your area of interest. The tool will allow you to choose an output directory. The image files will be automatically extracted from the .zip files and added to your current ArcMap document. Interrupted downloads are resumed, provided you specify the same directory as before. 

