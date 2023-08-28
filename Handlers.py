import adsk.core, adsk.fusion, adsk.cam, traceback
ui = None
app = adsk.core.Application.get()
if app:
    ui  = app.userInterface

product = app.activeProduct
design = adsk.fusion.Design.cast(product)



class AirfoilCommandDestroyHandler(adsk.core.CommandEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        try:
            # when the command is done, terminate the script
            # this will release all globals which will remove all event handlers
            adsk.terminate()
        except:
            if ui:
                ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

class AirfoilValidateInputHandler(adsk.core.ValidateInputsEventHandler):
    def __init__(self):
        super().__init__()
       
    def notify(self, args):
        try:
            sels = ui.activeSelections
            if len(sels) == 3:
                args.areInputsValid = True
            else:
                args.areInputsValid = False
        except:
            if ui:
                ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))