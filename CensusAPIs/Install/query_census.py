#!/usr/bin/env python

## for more information about ArcGIS Python Add-ins
## http://resources.arcgis.com/en/help/main/10.2/index.html#//014p00000025000000
## Python Add-in Tools:
## http://resources.arcgis.com/en/help/main/10.2/index.html#/Tool/014p00000027000000/

import arcpy, pythonaddins
import urllib2, json, os
import ConfigParser

config = ConfigParser.ConfigParser()
config.read(os.path.join(os.path.dirname(__file__), r'census_config.txt'))
censusAPIkey = config.get('api.census.gov', 'key')

class QueryCensus2010(object):
    def __init__(self):
        self.enabled = True
        self.checked = True
        self.shape = "NONE" # Can set to "Line", "Circle" or "Rectangle" for interactive shape drawing and to activate the onLine/Polygon/Circle event sinks.
        self.Census = {}
        self.Census['tables'] = {
            "H0030001": "Housing units",
            "H0030003": "Vacant housing units",
            "H0040001": "Occupied housing units",
            "H0040002": "Owned with a mortgage or a loan",
            "H0040003": "Owned free and clear",
            "H0040004": "Renter occupied",
            "P0010001": "Population"
        }
        self.Census['sortorder'] = ('P0010001', 'H0030001', 'H0030003', 'H0040001', 'H0040002', 'H0040003', 'H0040004')
            
    def onMouseDown(self, x, y, button, shift):
        pass
    def onMouseDownMap(self, x, y, button, shift):
        pass
    def onMouseUp(self, x, y, button, shift):
        pass
    def onMouseUpMap(self, x, y, button, shift):
        censuspath = ''
        censuslyr = ''
# Get spatial reference (sr) for the first Data Frame of the current map document. 
        mxd = arcpy.mapping.MapDocument("CURRENT") # current map document
        df = arcpy.mapping.ListDataFrames(mxd)[0]  # first data frame
        sr = df.spatialReference                   # spatial reference of the data frame
        lat, lng = 0, 0
        # Reproject coordinates to WGS84 (longitude, latitude) if different coordinate system
        if not (sr.PCSCode == 4326):
            pt = arcpy.PointGeometry(arcpy.Point(x,y), sr)
            ll = pt.projectAs(arcpy.SpatialReference(4326))
            lng, lat = ll.firstPoint.X, ll.firstPoint.Y
        else:
            lng, lat = x, y

        # determine if the Census Geometry layer already exists
        if(len( arcpy.mapping.ListLayers(df,"census_geometry") ) > 0):
            censuslyr = arcpy.mapping.ListLayers(df,"census_geometry")[0]
        else:
            censuslyr = None

        # determine if the Census Geometry layer is broken
        if(hasattr(censuslyr, "isBroken") and censuslyr.isBroken):
            if(arcpy.Exists(r"in_memory\census_geometry")):
                arcpy.Delete_management(r"in_memory\census_geometry")
            arcpy.mapping.RemoveLayer(df, censuslyr)
            censuslyr = None

        # create a new Census Geometry layer
        if(censuslyr == None):
            if(arcpy.Exists(r"in_memory\census_geometry")):
                arcpy.Delete_management(r"in_memory\census_geometry")
            censuspath = arcpy.CreateFeatureclass_management("in_memory", "census_geometry", "POLYGON", "", "DISABLED", "DISABLED", "GEOGCS['GCS_WGS_1984',DATUM['D_WGS_1984',SPHEROID['WGS_1984',6378137.0,298.257223563]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]];-400 -400 1000000000;-100000 10000;-100000 10000;8.98315284119522E-09;0.001;0.001;IsHighPrecision", "", "0", "0", "0")
            censuspath = censuspath.getOutput(0)
            arcpy.AddField_management(censuspath, "state",  "TEXT", "", "", "2", "", "NULLABLE", "NON_REQUIRED", "")
            arcpy.AddField_management(censuspath, "county", "TEXT", "", "", "3", "", "NULLABLE", "NON_REQUIRED", "")
            arcpy.AddField_management(censuspath, "tract",  "TEXT", "", "", "6", "", "NULLABLE", "NON_REQUIRED", "")
            arcpy.AddField_management(censuspath, "block",  "TEXT", "", "", "4", "", "NULLABLE", "NON_REQUIRED", "")
            ### TODO: dynamically add fields to store the API information (self.Census['tables'])
            ###       so that everything can be in an ArcGIS Feature Class element
            censuslyr = arcpy.mapping.ListLayers(df, "census_geometry")[0]
            symbollyr = arcpy.mapping.Layer( os.path.join(os.path.dirname(__file__), r'census_geometry.lyr') )
            arcpy.mapping.UpdateLayer(df, censuslyr, symbollyr, True)
        # if already exists, remove features from the Census Geometry layer
        else:
            censuslyr = arcpy.mapping.ListLayers(df, "census_geometry")[0]
            censuspath = censuslyr.dataSource
            arcpy.DeleteFeatures_management(censuslyr)

        if not((lat == 0) or (lng == 0)):
            if(shift == 1):
                # hold shift to search tracts
                geourl = "http://tigerweb.geo.census.gov/arcgis/rest/services/Tracts_Blocks/MapServer/0/query?where=&text=&objectIds=&geometry=x%3A{0}%2C+y%3A{1}&geometryType=esriGeometryPoint&inSR=4326&spatialRel=esriSpatialRelIntersects&relationParam=&outFields=STATE,COUNTY,TRACT&returnGeometry=true&outSR=4326&returnIdsOnly=false&returnZ=false&returnM=false&returnDistinctValues=false&f=pjson".format(lng,lat)
                tblurl = "http://api.census.gov/data/2010/sf1?key={k}&get={tbl}&for=tract:{t}&in=state:{s}+county:{c}"
            else:
                geourl = "http://tigerweb.geo.census.gov/arcgis/rest/services/Tracts_Blocks/MapServer/12/query?where=&text=&objectIds=&geometry=x%3A{0}%2C+y%3A{1}&geometryType=esriGeometryPoint&inSR=4326&spatialRel=esriSpatialRelIntersects&relationParam=&outFields=STATE,COUNTY,TRACT,BLOCK&returnGeometry=true&outSR=4326&returnIdsOnly=false&returnZ=false&returnM=false&returnDistinctValues=false&f=pjson".format(lng,lat)
                tblurl = "http://api.census.gov/data/2010/sf1?key={k}&get={tbl}&for=block:{b}&in=state:{s}+county:{c}+tract:{t}"
            # retrieve the Census Geometry from the TigerWeb ArcGIS Server
            response = urllib2.urlopen(geourl)
            geod = json.loads(response.read())
            # if no features returned, provide a warning and stop
            if(len(geod['features']) == 0):
                pythonaddins.MessageBox("No Census Geometries located. Are you clicking within the United States?", "No Geometries", 0)
                return False

            # read the geometries into an arcpy Polygon object
            polygon = arcpy.Polygon(arcpy.Array(map(lambda x: arcpy.Point(x[0], x[1]), geod['features'][0]['geometry']['rings'][0])), arcpy.SpatialReference(4326))
            geoattr = geod['features'][0]['attributes']
            if("BLOCK" not in geoattr):
                geoattr["BLOCK"] = None
                
            # use an insert cursor to update the "census_geometry" data with the returned results
            cursor = arcpy.da.InsertCursor(censuspath, ("SHAPE@", "state", "county", "tract", "block") )
            cursor.insertRow( (polygon, geoattr["STATE"], geoattr["COUNTY"], geoattr["TRACT"], geoattr["BLOCK"] ) )
            del cursor

            # build the URL to request data from api.census.gov
            global censusAPIkey
            if(shift == 1):
                tblurl = tblurl.format(tbl=",".join(self.Census['sortorder']),s=geoattr["STATE"],c=geoattr["COUNTY"],t=geoattr["TRACT"],k=censusAPIkey)
            else:
                tblurl = tblurl.format(tbl=",".join(self.Census['sortorder']),s=geoattr["STATE"],c=geoattr["COUNTY"],t=geoattr["TRACT"],b=geoattr["BLOCK"],k=censusAPIkey)
            # request the data from the Census API
            response = urllib2.urlopen(tblurl)
            apid = json.loads(response.read())
            # change the 2D array to a dictionary
            apid = dict(zip(apid[0], apid[1]))

            # put the API data into a dialog box
            result = ""
            for k in self.Census['sortorder']:
                result += "{description}: {value}\n".format(description=self.Census['tables'][k], value=apid[k])
            pythonaddins.MessageBox(result, "Census 2010 Information", 0)
        else:
            pythonaddins.MessageBox("Unable to produce valid coordinates. Please check your data frame coordinate system.", "Invalid Coordinates", 0)
    def onMouseMove(self, x, y, button, shift):
        pass
    def onMouseMoveMap(self, x, y, button, shift):
        pass
    def onDblClick(self):
        pass
    def onKeyDown(self, keycode, shift):
        pass
    def onKeyUp(self, keycode, shift):
        pass
    def deactivate(self):
        self.enabled = True
        self.checked = False
    def onCircle(self, circle_geometry):
        pass
    def onLine(self, line_geometry):
        pass
    def onRectangle(self, rectangle_geometry):
        pass
