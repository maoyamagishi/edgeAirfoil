import adsk.core, adsk.fusion, adsk.cam, traceback
ui = None
app = adsk.core.Application.get()
if app:
    ui  = app.userInterface

product = app.activeProduct
design = adsk.fusion.Design.cast(product)
class Airfoil:

    def AirfoilNameReader(name):
        # Reading first line with airfoil name
        object_name = name
        if(len(object_name)==0): 
            object_name = "No_name"
        object_name = object_name.replace(" ", "_")
        return  object_name
    
    def DatFileChecker(Firstrow):
        # Reading second line for distinguishing file format
        Lednicer_top = 0
        Lednicer_bottom = 0
        second_line = Firstrow
        line = second_line.strip(' \t')
        line = line.replace('\t', ' ')
        line = line.replace(',', ' ')
        p1 = line.find(".")
        p2 = line.find(" ")
        p3 = line.rfind(".")
        try:
            x = int(line[0:p1])
        except ValueError:
            ui.messageBox('Wrong file format. Cannot convert first string to number.', 'Error')
            return
        try:
            y = int(line[p2+1:p3])
        except ValueError:
            ui.messageBox('Wrong file format. Cannot convert second string to number.', 'Error')
            return
        
        if x > 1:
            # Lednicer DAT format
            DATformat = 2
            Lednicer_top = x
            Lednicer_bottom = y
        elif x == 1:
            # Selig DAT format
            DATformat = 1
        else:
            msg = ''
            msg += '\nUnknown DAT format'
            ui.messageBox(msg, 'Error')
            return
        
        return DATformat ,Lednicer_top,Lednicer_bottom

    
    def DAT2List2(datfile,filesize,starposition):
        coordX = []
        coordY = []
        for ii in range(filesize ):
            line = datfile[ii +1 + starposition]
            line = line.strip(' \t')
            line = line.replace('\t', ' ')
            line = line.replace(',', ' ')
            p1 = line.find(" ")
            p2 = line.rfind(" ")
            try:
                x = float(line[0:p1])
            except ValueError:
                ui.messageBox('Wrong file format. Cannot convert X coordinate.', 'Error')
                break
            try:
                y = float(line[p2+1:])
            except ValueError:
                ui.messageBox('Wrong file format. Cannot convert Y coordinate.', 'Error')
                break
            coordX.append(x)
            coordY.append(y)
            # Reading next line with coordinates
        return coordX,coordY

    def DatHandler(datfile,DATformat,Lednicer_top,Lednicer_bottom):
        # Reading file into array
        if DATformat == 1: # Selig
            filesize = len(datfile) -1
            coXY = Airfoil.DAT2List2(datfile,filesize,0)
            coordX = coXY[0]
            coordY = coXY[1]

        # Reading file into array with following processing
        elif DATformat == 2: # Lednicer

            coXY1 = Airfoil.DAT2List2(datfile,Lednicer_top -1,0)
            coordX1 = coXY1[0]
            coordY1 = coXY1[1]

            coXY2 = Airfoil.DAT2List2(datfile,Lednicer_bottom -1,Lednicer_top)
            coordX2 = coXY2[0]
            coordY2 = coXY2[1]

            # Need to join two arrays in correct way
            for i in reversed(range(len(coordX1))):
                coordX.append(coordX1[i])
                coordY.append(coordY1[i])
            for i in range(1, len(coordX2)):
                coordX.append(coordX2[i])
                coordY.append(coordY2[i])
        
        return coordX ,coordY

    def Execute(self, Plane, Point1, Point2):
        coordX = [] # result array for spline
        coordY = [] # result array for spline
        coordX1 = [] # temporary array for Lednicer DAT format
        coordY1 = [] # temporary array for Lednicer DAT format
        coordX2 = [] # temporary array for Lednicer DAT format
        coordY2 = [] # temporary array for Lednicer DAT format
        DATformat = 0 # 1 - Selig, 2 - Lednicer, 0 - undefined
        Lednicer_top = 0
        Lednicer_bottom = 0
        msg = ''
        consPoint1 = adsk.core.Point3D.create(Point1.geometry.x,Point1.geometry.y,Point1.geometry.z)
        consPoint2 = adsk.core.Point3D.create(Point2.geometry.x,Point2.geometry.y,Point2.geometry.z)        
        measureResult = app.measureManager.measureMinimumDistance(consPoint1, consPoint2)
        Chord = measureResult.value
        rootComp = design.rootComponent


        point1coordinatex = consPoint1.x
        point1coordinatey = consPoint1.y
        point1coordinatez = consPoint1.z
        point2coordinatex = consPoint2.x
        point2coordinatey = consPoint2.y
        point2coordinatez = consPoint2.z

        foildirection = [consPoint1.x -point2coordinatex, point1coordinatey-point2coordinatey, point1coordinatez-point2coordinatez]

        dlg = ui.createFileDialog()
        dlg.title = 'Open DAT File'
        dlg.filter = 'Airfoil DAT files (*.dat);;All Files (*.*)'
        if dlg.showOpen() != adsk.core.DialogResults.DialogOK :
            return
        
        filename = dlg.filename
        f = open(filename, 'r')

        root = design.rootComponent
        try:
            sketch = root.sketches.add(Plane)
        except RuntimeError:
            ui.messageBox('You should select origin plane or construction plane.', 'Error')
            return

        normal = sketch.xDirection.crossProduct(sketch.yDirection)
        normal.transformBy(sketch.transform)
        origin = sketch.origin
        origin.transformBy(sketch.transform)
        Xvector = adsk.core.Vector3D.create(1.0, 0.0, 0.0)   # X axis
        Yvector = adsk.core.Vector3D.create(0.0, 1.0, 0.0)   # Y axis
        Zvector = adsk.core.Vector3D.create(0.0, 0.0, 1.0)   # Z axis
        foilvector = adsk.core.Vector3D.create(foildirection[0] ,foildirection[1] ,foildirection[2])

            
#        translationMatrix = adsk.core.Matrix3D.create()
#        translationMatrix.translation = adsk.core.Vector3D.create(OffsetX, OffsetY, 0.0)

        points = adsk.core.ObjectCollection.create()
        datfile = f.readlines()

        filename = Airfoil.AirfoilNameReader(datfile[0])
        object_name = filename
        
        while True:
            try:
                Plane.name = object_name
                break
            except RuntimeError:
                print("Renaming of this type of planes is not supported on this platform...")
        
        formatAndDatas = Airfoil.DatFileChecker(datfile[1])
        DATformat = formatAndDatas[0]
        Lednicer_top = formatAndDatas[1]
        Lednicer_bottom = formatAndDatas[2]
 
        COORDs = Airfoil.DatHandler(datfile,DATformat,Lednicer_top,Lednicer_bottom)   
        coordX = COORDs[0]
        coordY = COORDs[1]    
        
        xlist = coordX.copy()
        ylist = coordX.copy()
        zlist = coordX.copy()

        
        if sketch.xDirection.isParallelTo(Xvector):
            if sketch.yDirection.isParallelTo(Yvector):
                # XY plane, normal Y  
                if foilvector.isParallelTo(Xvector):    #parallel to y axis
                    if foildirection[0] < 0:   #finished
                        for i in range(len(coordX)) :
                           xlist[i] = coordX[i] * Chord  + point1coordinatex                  
                           ylist[i] = coordY[i] * Chord  + point1coordinatey
                           zlist[i] = 0.0
                    else:
                        for i in range(len(coordX)) :    #finished
                           xlist[i] = (1 - coordX[i]) * Chord  + point2coordinatex                  
                           ylist[i] = coordY[i] * Chord + point2coordinatey
                           zlist[i] = 0.0
                else:                        #parallel to x axis
                    if foildirection[1] < 0:
                        for i in range(len(coordX)) :
                           ylist[i] = coordX[i] * Chord + point1coordinatey                   
                           xlist[i] = coordY[i] * Chord + point1coordinatex
                           zlist[i] = 0.0
                    else:
                        for i in range(len(coordX)) :
                           ylist[i] = (1 - coordX[i]) * Chord + point2coordinatey                   
                           xlist[i] = coordY[i] * Chord + point2coordinatex
                           zlist[i] = 0.0

        if sketch.xDirection.isParallelTo(Zvector):
            if sketch.yDirection.isParallelTo(Yvector):
                # YZ plane, normal Y
                if foildirection[1] == 0:      #parallel to y axis  
                    if foildirection[0] > 0:   #finished 
                       for i in range(len(coordX)) :
                           xlist[i] = coordY[i] * Chord - point1coordinatey                 
                           ylist[i] =  -1* coordX[i] * Chord + point1coordinatex
                           zlist[i] = 0.0
                           
                    else:                     
                        for i in range(len(coordX)) :   #finished
                           xlist[i] = coordY[i] * Chord - point1coordinatey                 
                           ylist[i] = coordX[i] * Chord + point1coordinatex
                           zlist[i] = 0.0
                           
                else:                           #parallel to z axis
                    if foildirection[1] > 0:  #finished
                        for i in range(len(coordX)):
                           xlist[i] = coordY[i] * Chord - point1coordinatex              
                           ylist[i] = -1*coordX[i] * Chord - point1coordinatey   
                           zlist[i] = 0.0
                           
                    else:                       
                        for i in range(len(coordX)) :     #finished
                           xlist[i] =    coordY[i] * Chord - point1coordinatex          
                           ylist[i] = coordX[i] * Chord + point1coordinatey
                           zlist[i] = 0.0
                           

        if sketch.xDirection.isParallelTo(Xvector):
            if sketch.yDirection.isParallelTo(Zvector):
                # XZ plane, mirrored Y
                if foildirection[1] == 0:      #parallel to y axis  
                    if foildirection[0] > 0:   #finished
                       for i in range(len(coordX)) :
                           xlist[i] = -1 * coordX[i] * Chord - point1coordinatey                 
                           ylist[i] = coordY[i] * Chord - point1coordinatex
                           zlist[i] = 0.0
                           
                    else:              
                        for i in range(len(coordX)) :   
                           xlist[i] = coordX[i] * Chord + point1coordinatex                 
                           ylist[i] = coordY[i] * Chord + point1coordinatey
                           zlist[i] = 0.0
                           
                else:                           #parallel to z axis
                    if foildirection[1] > 0:  
                        ui.messageBox(format(sketch.xDirection.isParallelTo(Xvector)))
                        for i in range(len(coordX)):
                           xlist[i] = coordY[i] * Chord + point1coordinatex                 
                           ylist[i] = -1 * coordX[i] * Chord + point1coordinatey
                           zlist[i] = 0.0
                    else:                       
                        for i in range(len(coordX)) :     
                           xlist[i] = -1* coordY[i] * Chord - point1coordinatey             
                           ylist[i] = coordX[i] * Chord - point1coordinatex
                           zlist[i] = 0.0

        for i in range(len(coordX)):
            point = adsk.core.Point3D.create(xlist[i] , ylist[i]  , zlist[i] )       
            points.add(point)
        
        sketch.sketchCurves.sketchFittedSplines.add(points)
              
        sketch.name=object_name


