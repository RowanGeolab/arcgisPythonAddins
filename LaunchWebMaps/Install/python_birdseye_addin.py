#!/usr/bin/env python

## for more information about ArcGIS Python Add-ins
## http://resources.arcgis.com/en/help/main/10.2/index.html#//014p00000025000000
## Python Add-in Tools:
## http://resources.arcgis.com/en/help/main/10.2/index.html#/Tool/014p00000027000000/

import arcpy
import pythonaddins
import webbrowser

class LaunchCommonWebMaps(object):
    """Implementation for python_birdseye_addin.tool (Tool)"""
    def __init__(self):
        self.enabled = True
        self.checked = True
        self.newwindow = 2
        self.shape = "NONE" # Can set to "Line", "Circle" or "Rectangle" for interactive shape drawing and to activate the onLine/Polygon/Circle event sinks.
    def onMouseDown(self, x, y, button, shift):
        pass
    def onMouseDownMap(self, x, y, button, shift):
        pass
    def onMouseUp(self, x, y, button, shift):
        pass
    def onMouseUpMap(self, x, y, button, shift):
# Get spatial reference (sr) for the first Data Frame of the current map document. 
        mxd = arcpy.mapping.MapDocument("CURRENT")
        df = arcpy.mapping.ListDataFrames(mxd)[0]
        sr = df.spatialReference
        lat, lng = 0, 0
# Reproject coordinates to WGS84 (longitude, latitude) if different coordinate system.
        if not (sr.PCSCode == 4326):
            pt = arcpy.PointGeometry(arcpy.Point(x,y), sr)
            ll = pt.projectAs(arcpy.SpatialReference(4326))
            lng, lat = ll.firstPoint.X, ll.firstPoint.Y
        else:
            lng, lat = x, y
        if not((lat == 0) or (lng == 0)):
            if(shift == 2):
                    # hold control to launch Google Maps
                    url = "http://maps.google.com/maps?z=13&t=h&q=loc:{1}+{0}".format(lng,lat)
            else:
                    # no modifier keys for Bing Maps Oblique
                    url = "http://bing.com/maps/default.aspx?cp={1}~{0}&style=o&lvl=17".format(lng,lat)
            webbrowser.open(url, new=self.newwindow)
            self.newwindow = 0
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
