#Query Census APIs
Python-based Add-in for ArcGIS Desktop. Upon clicking a location within the United States, the tool with query TigerWeb and api.census.gov to retrieve the selected geometry and some basic demographic data. 

You do not need to download any Census GIS data for this tool to work. It will request the geometry and attribute data for you! Works with nearly any projection in ArcMap. 

##Install
Request a [Census API key](http://www.census.gov/developers/tos/key_request.html). Open the `query_census.py` file and paste your API key into the `CensusAPIkey` variable. 

Double-click `makeaddin.py` to create the `.esriaddin` file. Double-click the `.esriaddin` file to install the add-in in ArcMap. 

##Usage
A new "Query Census APIs" toolbar should appear in ArcMap. Click the "Query 2010 Census" button, then click the map to retrieve a Census Block along with demographic information. Hold `Shift` to request Census Tracts instead of Blocks. 
