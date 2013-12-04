import arcpy, pythonaddins
import os, urllib2, json, zipfile

class dl2012(object):
    """Implementation for dl2012.tool (Tool)"""
    def __init__(self):
        self.enabled = True
        self.cursor = 3
        self.shape = "Rectangle"
    def onMouseDown(self, x, y, button, shift):
        pass
    def onMouseDownMap(self, x, y, button, shift):
        pass
    def onMouseUp(self, x, y, button, shift):
        pass
    def onMouseUpMap(self, x, y, button, shift):
        pass
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
        pass
    def onCircle(self, circle_geometry):
        pass
    def onLine(self, line_geometry):
        pass
    def onRectangle(self, rectangle_geometry):
        # perform some sanity checks
        if not (rectangle_geometry.spatialReference.PCSCode == 3424):
            rectangle_geometry = rectangle_geometry.projectAs(arcpy.SpatialReference(3424))
        if(not isinstance(rectangle_geometry.XMin, float)):
            pythonaddins.MessageBox("Click and drag to select an area.", "Incorrect Extent Specified", 1)
            return False       
        if(rectangle_geometry.XMin < 0 or rectangle_geometry.YMin < 0 or rectangle_geometry.XMax > 1000000 or rectangle_geometry.YMax > 1000000):
            pythonaddins.MessageBox("Select an area within New Jersey.", "Out of bounds", 1)
            return False
        # build the URL to request features from the NJGIN service
        wfsurl = "http://njgin.state.nj.us/NJ_GeoServer/wfs?service=wfs&version=2.0.0&request=GetFeature&typeName=NJOGIS:Ortho07Grid_poly&srsName=EPSG:3424&bbox={minx},{miny},{maxx},{maxy}&outputFormat=json" \
            .format(minx=rectangle_geometry.XMin,miny=rectangle_geometry.YMin,maxx=rectangle_geometry.XMax,maxy=rectangle_geometry.YMax)
        try:
            response = urllib2.urlopen(wfsurl)
            wfsd = json.loads(response.read())['features']
        except:
            pythonaddins.MessageBox("Unable to connect to the NJGIN web service. Please try again.", "Unable to connect", 0)
            return False
        
        # warn people about the potentially large download
        download = pythonaddins.MessageBox("You have selected {0} tiles, approximately {1}MB in size. Do you want to continue downloading?".format(len(wfsd), 10.1*len(wfsd)), "Continue Download?", 4)
        if(download == "No"):
            return False

        # specify output directory
        dldir = pythonaddins.SaveDialog("Choose download directory location...", "NewDownloadDirectory", r"C:\temp")
        if(dldir == None or dldir == 'None'):
            return False
        if(not os.path.exists(dldir)):
            os.makedirs(dldir)

        # one more notice
        finalnotice = """Please note, the download may take a while. Open the Python Console (in the "Geoprocessing" menu) for progress updates. You will be notified when the download is complete."""
        if("Cancel" == pythonaddins.MessageBox(finalnotice, "Beginning download...", 1)):
            return False
        
        #iterate over features in the JSON returned by the WFS service
        for f in wfsd:
            url = "https://njgin.state.nj.us/ortho2012/nj2012ortho_sid_{0}.zip".format(f["properties"]["TILE_NO"])
            response = urllib2.urlopen(url)
            # output the requested zip to disk
            ozf = os.path.join(dldir, os.path.basename(url))
            if(not os.path.exists(ozf)):
                with open(ozf, "wb") as zipf:
                    zipf.write(response.read())
                print f["properties"]["TILE_NO"] + ".zip downloaded...", 
            else:
                print f["properties"]["TILE_NO"] + ".zip already downloaded..."
            # open the zip and extract the juicy raster goodness
            if(not os.path.exists(os.path.join(dldir,f["properties"]["TILE_NO"]+".sid"))):
                with zipfile.ZipFile(ozf, 'r') as sidzip:
                    sidzip.extract(f["properties"]["TILE_NO"]+".sid",dldir)
                    sidzip.extract(f["properties"]["TILE_NO"]+".sdw",dldir)
                print "extracted."
            else:
                print f["properties"]["TILE_NO"] + ".sid already extracted..." 
            # add each raster to the current map frame
            mxd = arcpy.mapping.MapDocument("CURRENT")
            df = arcpy.mapping.ListDataFrames(mxd)[0]
            result = arcpy.MakeRasterLayer_management(os.path.join(dldir, f["properties"]["TILE_NO"]+".sid"), f["properties"]["TILE_NO"]+".sid")
        pythonaddins.MessageBox("Download complete.", "Done!", 0)
        arcpy.RefreshActiveView()

class openGeoweb(object):
    """Implementation for openGeoweb.tool (Tool)"""
    def __init__(self):
        self.enabled = True
        self.cursor = 3
        import webbrowser
        self.wb = webbrowser
        self.shape = "Rectangle"
    def onMouseDown(self, x, y, button, shift):
        pass
    def onMouseDownMap(self, x, y, button, shift):
        pass
    def onMouseUp(self, x, y, button, shift):
        pass
    def onMouseUpMap(self, x, y, button, shift):
        pass
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
        pass
    def onCircle(self, circle_geometry):
        pass
    def onLine(self, line_geometry):
        pass
    def onRectangle(self, rectangle_geometry):
        # if not in NJ State Plane feet, reproject it
        if not (rectangle_geometry.spatialReference.PCSCode == 3424):
            rectangle_geometry = rectangle_geometry.projectAs(arcpy.SpatialReference(3424))
        # catch single-clicks
        if(not isinstance(rectangle_geometry.XMin, float)):
            pythonaddins.MessageBox("Click and drag to select an area. NJ-Geoweb will then open at the same extent.", "Incorrect Extent Specified", 1)
            return False       
        # catch bounding boxes drawn far outside of New Jersey
        if(rectangle_geometry.XMin < 0 or rectangle_geometry.YMin < 0 or rectangle_geometry.XMax > 1000000 or rectangle_geometry.YMax > 1000000):
            pythonaddins.MessageBox("Select an area within New Jersey.", "Out of bounds", 1)
            return False
        # build the URL and open a browser
        geoweb = "http://njwebmap.state.nj.us/NJGeoWeb//UrlHandler.ashx?MAPTABID=2&MINX={minx}&MINY={miny}&MAXX={maxx}&MAXY={maxy}&SIZE=800,600&LABEL=%7c431434.194025001%7c482873.283329998%7c102711%7c0%2c0%2c0%7c12%7cCIRCLE%7c0%2c128%2c255%7c10%7c%7c&THEME=&LANGUAGE=en-US" \
            .format(minx=rectangle_geometry.XMin,miny=rectangle_geometry.YMin,maxx=rectangle_geometry.XMax,maxy=rectangle_geometry.YMax)
        self.wb.open(geoweb)
        # cross your fingers and hope that GeoWeb loads