#Author-
#Description-

import adsk.core, adsk.fusion, adsk.cam, traceback
import os
from . import Airfoil
from . import Handlers as hd

# global set of event handlers to keep them referenced for the duration of the command
handlers = []
ui = None
app = adsk.core.Application.get()
if app:
    ui  = app.userInterface

product = app.activeProduct
design = adsk.fusion.Design.cast(product)


class AirfoilCommandExecuteHandler(adsk.core.CommandEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        try:
            command = args.firingEvent.sender
            inputs = command.commandInputs

            input0 = inputs[0];     # construction plane
            sel0 = input0.selection(0)
            
            input1 = inputs[1];     # leading edge
            sel1 = input1.selection(0)
            
            input2 = inputs[2];     # tail edge
            sel2 = input2.selection(0)
           
            airfoil = Airfoil.Airfoil()
            airfoil.Execute(sel0.entity, sel1.entity, sel2.entity);
        except:
            if ui:
                ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

class AirfoilCommandCreatedHandler(adsk.core.CommandCreatedEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        try:
            cmd = args.command
            onExecute = AirfoilCommandExecuteHandler()
            cmd.execute.add(onExecute)
            onDestroy = hd.AirfoilCommandDestroyHandler()
            cmd.destroy.add(onDestroy)

            onValidateInput = hd.AirfoilValidateInputHandler()
            cmd.validateInputs.add(onValidateInput)
            # keep the handler referenced beyond this function
            handlers.append(onExecute)
            handlers.append(onDestroy)
            handlers.append(onValidateInput)
            #define the inputs
            inputs = cmd.commandInputs
            i1 = inputs.addSelectionInput('ConstPlane', 'Construction Plane', 'Please select a construction plane')
            i1.addSelectionFilter(adsk.core.SelectionCommandInput.ConstructionPlanes)
            i1.addSelectionFilter(adsk.core.SelectionCommandInput.RootComponents)


            i2 = inputs.addSelectionInput('SketchPoint', 'Sketch Point', 'Please select a Sketch point')
            i2.addSelectionFilter(adsk.core.SelectionCommandInput.SketchPoints)    

            i3 = inputs.addSelectionInput('SketchPoint', 'Sketch Point', 'Please select a Sketch point')
            i3.addSelectionFilter(adsk.core.SelectionCommandInput.SketchPoints)  

        except:
            if ui:
                ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

# Main function
def run(context):
    try:
        title = 'Select Construction Plane'

        if not design:
            ui.messageBox('No active Fusion design', title)
            return

        commandDefinitions = ui.commandDefinitions

        # check the command exists or not
        cmdDef = commandDefinitions.itemById('AirfoilCMDDef')
        if not cmdDef:
            resourceDir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'resources') # absolute resource file path is specified
            cmdDef = commandDefinitions.addButtonDefinition('AirfoilCMDDef',
                    'Airfoil Parameters',
                    'Creates airfoil spline on selected construction plane',
                    resourceDir)


        onCommandCreated = AirfoilCommandCreatedHandler()
        cmdDef.commandCreated.add(onCommandCreated)
        # keep the handler referenced beyond this function
        handlers.append(onCommandCreated)
        inputs = adsk.core.NamedValues.create()
        cmdDef.execute(inputs)

        # prevent this module from being terminate when the script returns, because we are waiting for event handlers to fire
        adsk.autoTerminate(False)

    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))