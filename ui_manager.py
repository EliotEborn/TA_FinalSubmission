import maya.cmds as cmds
import maya.mel as mel
import webbrowser
import os


from preset import Preset
from json_manager import JsonManager
from all_presets import presets

# UI MANAGER CLASS #
#######################################################################################
class UiManager: 
    
    def __init__(self):

        #Initialises JSON Manager which handles saving and loading presets
        self.jsonManager = JsonManager()

        #Checks if the JSON file exists or if it is empty (has no presets loaded into it)
        if not os.path.exists(self.jsonManager.file_path) or os.path.getsize(self.jsonManager.file_path) == 0:
            self.jsonManager.save_presets(presets)

        #Load all presets from the JSON file into a dictionary of Preset objects
        self.loaded_presets = self.jsonManager.load_presets()  

        #Checks if loading the JSON file returned nothing, if so load the default presets into the JSON
        if not self.loaded_presets:
            self.loaded_presets = presets
            self.jsonManager.save_presets(self.loaded_presets)

        #Checks if JSON file was just created, if so load the default presets into the JSON and marks file as not new anymore
        if self.jsonManager.is_new_file: 
            self.jsonManager.save_presets(presets)
            self.jsonManager.is_new_file = False

        #Initialise both current and original settings dictionaries and current preset
        self.current_settings = {}
        self.original_settings = {}
        self.current_preset = self.loaded_presets["Custom"]

        #Initilaise menu look-up dictionaries which map menu option names to integers
        self.scalingRel_menu = {'Link' : 0, 'Object Space' : 1, 'World Space' : 2}
        self.pressMeth_menu = {'Manual Pressure Setting' : 0, 'Volume Tracking Model' : 1}

        #Store nCloth controls dictionary, to be populated later
        self.ncloth_controls = {}

#######################################################################################
# BASIC FUNCTIONS #
#######################################################################################    

    #Open Autodesk Maya link on nCloth properties when INFO button pressed
    def open_webpage(self, url):
        webbrowser.open(url)

    #Check if any settings have changed compared to original preset values (excluding name) 
    def compare_settings(self, current_settings, original_settings):

        #If current_settings and original_settings dictionaries are empty, assume nothing has changed
        if not current_settings or not original_settings:
            return False

        #Iterate over each key in current_settings and compare values
        for key in current_settings:
            if key != "name":

                #Checks if current settings are different to original settings
                if current_settings[key] != original_settings.get(key, None):

            #Setting other than name has been changed
                    return True

        #No relevant settings have been changed
        return False


    #Update preset name if settings have changed (excluding name) 
    def update_preset_name(self, preset_name, current_settings, original_settings):
        if self.compare_settings(current_settings, original_settings):

            #Settings changed, name will be changed to Custom - "Preset Name"
            return f"Custom - {preset_name}"
        
        #If no change is found, keep original name
        return preset_name
    
#######################################################################################
# SETTINGS CHANGED HANDLER #
#######################################################################################


    #Callback to update the preset name in the UI when settings have changed
    def on_setting_changed(self, *args):

        #Get current settings from the UI
        self.current_settings = self.get_current_settings()

        #Compare current settings with original settings, if different update preset name
        new_name = self.update_preset_name(self.current_preset.name, self.current_settings, self.original_settings)

        cmds.textField(self.ncloth_controls['fieldpresetName'], edit=True, text=new_name)

#######################################################################################
# UI UPDATE AND PRESET SELECTION #
#######################################################################################

    #Update UI based on which preset button was pressed (which preset was selected from dropdown)
    def select_preset(self, preset_name, *args):

        #Gets selected preset from presets dictionary 
        preset = self.loaded_presets.get(preset_name)

        #If preset exists in the presets dictionary the UI is updated with the correct settings
        if preset:

            self.current_preset = preset

            self.update_UI(preset)

            #Store current settings as both current and original (needed for comparison later since base preset settings)
            self.original_settings = self.get_current_settings()
            self.current_settings = self.original_settings.copy()

            ##Update preset name if settings have changed
            updated_name = self.update_preset_name(preset_name, self.current_settings, self.original_settings)
            cmds.textField(self.ncloth_controls['fieldpresetName'], edit=True, text=updated_name)

            #Loops over all sliders and menus adding a callback so any change triggers a name change
            for slider_name in ['bounce', 'friction', 'stretchResistance', 'compressionResistance', 'bendResistance', 'bendAngleDropoff', 
                                'restitutionAngle', 'rigidity', 'deformResistance', 'restLengthScale', 'pointMass', 'tangentialDrag', 
                                'damp', 'stretchDamp', 'startPressure', 'airTightness', 'incompressibility', 'maxIterations', 'pushOutRadius']:

                slider = self.ncloth_controls[slider_name]
                if cmds.floatSliderGrp(slider, exists=True):
                    cmds.floatSliderGrp(slider, edit=True, changeCommand=lambda *_:self.on_setting_changed())
                elif cmds.intSliderGrp(slider, exists=True):
                    cmds.intSliderGrp(slider, edit=True, changeCommand=lambda *_:self.on_setting_changed())

            for menu_name in ['scalingRelation', 'pressureMethod']:
                menu = self.ncloth_controls[menu_name]
                cmds.optionMenu(menu, edit=True, changeCommand=lambda *_:self.on_setting_changed())
        else:
            cmds.warning(f"Preset '{preset_name}' not found!")


    #Update UI based on values of the current preset
    def update_UI(self, current_preset):

            #Update the preset name and description in their associated text fields
            cmds.textField(self.ncloth_controls['fieldpresetName'], edit = True, text=current_preset.name)
            cmds.scrollField(self.ncloth_controls['fieldpresetDesc'], edit = True, text=current_preset.description)

            #Update physical property sliders with current preset values
            cmds.floatSliderGrp(self.ncloth_controls['bounce'], edit = True, value=current_preset.bounce)
            cmds.floatSliderGrp(self.ncloth_controls['friction'], edit = True, value=current_preset.friction)
            cmds.floatSliderGrp(self.ncloth_controls['stretchResistance'], edit = True, value=current_preset.stretchResistance)
            cmds.floatSliderGrp(self.ncloth_controls['compressionResistance'], edit = True, value=current_preset.compressionResistance)
            cmds.floatSliderGrp(self.ncloth_controls['bendResistance'], edit = True, value=current_preset.bendResistance)
            cmds.floatSliderGrp(self.ncloth_controls['bendAngleDropoff'], edit = True, value=current_preset.bendAngleDropoff)
            cmds.floatSliderGrp(self.ncloth_controls['restitutionAngle'], edit=True, value=current_preset.restitutionAngle)
            cmds.floatSliderGrp(self.ncloth_controls['rigidity'], edit=True, value=current_preset.rigidity)
            cmds.floatSliderGrp(self.ncloth_controls['deformResistance'], edit=True, value=current_preset.deformResistance)
            cmds.floatSliderGrp(self.ncloth_controls['restLengthScale'], edit=True, value=current_preset.restLengthScale)
            cmds.floatSliderGrp(self.ncloth_controls['pointMass'], edit = True, value=current_preset.pointMass)
            cmds.floatSliderGrp(self.ncloth_controls['tangentialDrag'], edit = True, value=current_preset.tangentialDrag)
            cmds.floatSliderGrp(self.ncloth_controls['damp'], edit = True, value=current_preset.damp)
            cmds.floatSliderGrp(self.ncloth_controls['stretchDamp'], edit=True, value=current_preset.stretchDamp)

            #Update scaling relation option menu (Converting scaling relation menu option from int to corresponding string)
            scaling_relation_menu = ["Link", "Object Space", "World Space"]
            scaling_relation_str = scaling_relation_menu[current_preset.scalingRelation]
            cmds.optionMenu(self.ncloth_controls['scalingRelation'], edit = True, value=scaling_relation_str)

            #Update pressure method option menu (converting pressure method menu option from int to corresponding string)
            pressure_method_menu = ["Manual Pressure Setting", "Volume Tracking Model"]
            pressure_method_str = pressure_method_menu[current_preset.pressureMethod]
            cmds.optionMenu(self.ncloth_controls['pressureMethod'], edit = True, value=pressure_method_str)

            #Update related pressure method related sliders
            cmds.floatSliderGrp(self.ncloth_controls['startPressure'], edit=True, value=current_preset.startPressure)
            cmds.floatSliderGrp(self.ncloth_controls['airTightness'], edit=True, value=current_preset.airTightness)
            cmds.floatSliderGrp(self.ncloth_controls['incompressibility'], edit=True, value=current_preset.incompressibility)

            #Update additional simulation settings (these are not related to pressure method)
            cmds.intSliderGrp(self.ncloth_controls['maxIterations'], edit = True, value=current_preset.maxIterations)
            cmds.floatSliderGrp(self.ncloth_controls['pushOutRadius'], edit = True, value=current_preset.pushOutRadius)

    #Get current settings from all UI controls and return as a dictionary 
    def get_current_settings(self): 
        settings = {
        "name" : cmds.textField(self.ncloth_controls['fieldpresetName'], query=True, text = True, ),
        "description" : cmds.scrollField(self.ncloth_controls['fieldpresetDesc'], query=True, text = True),
        "bounce" : cmds.floatSliderGrp(self.ncloth_controls['bounce'], query=True, value = True),
        "friction": cmds.floatSliderGrp(self.ncloth_controls['friction'], query=True, value = True),
        "stretchResistance": cmds.floatSliderGrp(self.ncloth_controls['stretchResistance'], query=True, value = True),
        "compressionResistance": cmds.floatSliderGrp(self.ncloth_controls['compressionResistance'], query=True, value = True),
        "bendResistance": cmds.floatSliderGrp(self.ncloth_controls['bendResistance'], query=True, value = True),
        "bendAngleDropoff":cmds.floatSliderGrp(self.ncloth_controls['bendAngleDropoff'], query=True, value = True),
        "restitutionAngle":cmds.floatSliderGrp(self.ncloth_controls['restitutionAngle'], query=True, value = True),
        "rigidity":cmds.floatSliderGrp(self.ncloth_controls['rigidity'], query=True, value = True),
        "deformResistance":cmds.floatSliderGrp(self.ncloth_controls['deformResistance'], query=True, value = True),
        "restLengthScale":cmds.floatSliderGrp(self.ncloth_controls['restLengthScale'], query=True, value = True),
        "pointMass":cmds.floatSliderGrp(self.ncloth_controls['pointMass'], query=True, value = True),
        "tangentialDrag":cmds.floatSliderGrp(self.ncloth_controls['tangentialDrag'], query=True, value = True),
        "damp":cmds.floatSliderGrp(self.ncloth_controls['damp'], query=True, value = True),
        "stretchDamp":cmds.floatSliderGrp(self.ncloth_controls['stretchDamp'], query=True, value = True),
        "scalingRelation": self.scalingRel_menu.get(cmds.optionMenu(self.ncloth_controls['scalingRelation'], query=True, value = True), 0),
        "pressureMethod": self.pressMeth_menu.get(cmds.optionMenu(self.ncloth_controls['pressureMethod'], query=True, value = True), 0),
        "startPressure":cmds.floatSliderGrp(self.ncloth_controls['startPressure'], query=True, value = True),
        "airTightness":cmds.floatSliderGrp(self.ncloth_controls['airTightness'], query=True, value = True),
        "incompressibility":cmds.floatSliderGrp(self.ncloth_controls['incompressibility'], query=True, value = True),
        "maxIterations":cmds.intSliderGrp(self.ncloth_controls['maxIterations'], query=True, value=True),
        "pushOutRadius":cmds.floatSliderGrp(self.ncloth_controls['pushOutRadius'], query=True, value = True)
        }

        return settings

#######################################################################################
# COLLIDER AND TOOL ACTIONS #
#######################################################################################

    #Apply passive collider to selected mesh
    #NOTE: Passive collider must be added to meshes the user wants the simulated asset to interact with 
    def apply_collider(self):

        #Get current selected objects
        selection = cmds.ls(selection=True)

        #If nothing is selected warn the user and show message in dialog box
        if not selection: 
                cmds.warning("Please select a mesh to continue")
                cmds.confirmDialog(title="Confirm Action", message=f"Error: Please select a mesh to continue.", button=['OK'], dismissString='No')
                return

        #Checks with user if want to apply passive collider to selected objects (objects are listed in the string)
        selection_str = ", ".join(selection)
        confirmation = cmds.confirmDialog(title="Confirm Action", message=f"Are you sure you'd like to apply passive collider to: {selection_str}?", button=['Yes','No'], defaultButton='Yes', cancelButton='No', dismissString='No')

        #If user says yes, the passive collider is applied to the selected mesh
        if confirmation == 'Yes': 
            for obj in selection:
                cmds.select(obj, replace=True) 

                #Use MEL command to apply passive collider to the selected mesh/es for nCloth simulation
                mel.eval("makeCollideNCloth;")

    #Checks if the current UI settings match those of an existing preset, if so that preset is applied to the mesh, if no "Custom" is returned
    def does_preset_match(self, current_settings, preset):
        preset_name = preset.name
        match_found = True 

        #Compare each parameter in current UI to specified parameters in the selected preset
        for key in current_settings:
            preset_attr = getattr(preset, key, None)

            if current_settings[key] != preset_attr:
                match_found = False
        
        #If all settings match that exact preset will be returned, if they don't then "Custom" will be returned
        if match_found: 
            return preset_name
        return "Custom"

    #Identifies if current UI settings match the exisitng preset, then applies either the matched preset or custom settings
    def identify_and_apply_preset(self):
        current_settings = self.get_current_settings()
        preset_matches = self.does_preset_match(current_settings, self.current_preset)

        preset_name = getattr(self.current_preset, "name", None)
        if not preset_name:
            cmds.warning("No preset selected. Please select a preset to apply. ")
            return

        #If a preset matches, apply it
        if preset_matches != "Custom":
            self.loaded_presets[preset_matches].apply_preset()
        else:
            #Otherwise, apply custom preset
            custom_preset = Preset(**current_settings)
            custom_preset.apply_preset()

    #Resets tool to default values (This is defined in presets dictionary in all_presets)
    def reset_tool(self):
        #Get default custom preset
        custom_preset = self.loaded_presets["Custom"]
        self.current_preset = custom_preset

        #Update UI with values from custom preset
        self.update_UI(custom_preset)

        #Store current settings as orginal and make a copy for comparison in other functions
        self.original_settings = self.get_current_settings()
        self.current_settings = self.original_settings.copy()

        #Update preset dropdown to show "Custom"
        cmds.optionMenu(self.ncloth_controls['presetDropdown'], edit=True, value="Custom")

    #Creates buttons in the dropdown for each preset from the preset dictionary and adds them to the UI
    #Once all items are cleared the dropdown is then filled with all the preset names from the presets dicitonary (except "Default")
    def update_preset_dropdown(self, loaded_presets, ncloth_controls):
        dropdown = ncloth_controls.get('presetDropdown')

        if not dropdown:
            return

        #Clear existing menu items
        menu_items = cmds.optionMenu(dropdown, query=True, itemListLong=True) or []
        for item in menu_items:
            cmds.deleteUI(item)

        #Repopulate dropdown with all menu items except Default 
        for preset_name in loaded_presets.keys():

            if not preset_name or preset_name == "Default":

                continue

            cmds.menuItem(label=preset_name, parent=dropdown)

#######################################################################################
# UI CREATION #
#######################################################################################
    #Function to create the UI
    def create_UI(self):

        #Naming the UI window 
        dock_name = "win_maya_ui_dock"
  
        #Checks if the dockable window already exists and deletes it if it does
        if cmds.workspaceControl(dock_name, exists=True):
            cmds.deleteUI(dock_name, control=True)

        #Checks if the floating window already exists and deletes it if it does
        if cmds.window('win_maya_ui_dock', exists=True):
            cmds.deleteUI('win_maya_ui_dock', window=True)

        #Creating Main Window
        cmds.workspaceControl(dock_name, label="P.A.M.", retain=False, floating=True, width=800, height=900)

        #Main layout for UI window with tool title and top buttons
        cmds.columnLayout("mainColumnLayout", adj=True)
        cmds.separator(h=5, style='none')
        cmds.rowLayout(numberOfColumns=6)
        cmds.text(label="", width=10)
        cmds.text(label="Physical Attribute Modifier")
        cmds.text(label="", width=315)
        cmds.button(label = "RESET TOOL", align='right', command = lambda x: self.reset_tool())
        cmds.text(label="", width=3)
        cmds.button(label = "INFO", width=60, align='right', command=lambda x: self.open_webpage("https://help.autodesk.com/view/MAYAUL/2024/ENU/?guid=GUID-99C0FE0F-8A37-4EA5-99C2-E08A0EF437A5"))
        cmds.setParent("..")

        #CHANGED FROM SCROLL LAYOUT TO DROPDOWN BASED OFF OF USER TESTING SESSION
        cmds.separator(h=10, style='none')
        cmds.rowLayout(numberOfColumns=4)
        cmds.text(label="", width=113)
        cmds.text(label="Type:")
        self.presetDropdown = cmds.optionMenu("presetDropdown", width=200, 
                                              changeCommand = lambda x: self.select_preset(cmds.optionMenu("presetDropdown",query=True, value=True), self.ncloth_controls, self.scalingRel_menu, self.pressMeth_menu))
        for preset_name in self.loaded_presets.keys():
            if preset_name != "Default":
                cmds.menuItem(label=preset_name)
        cmds.button(label="Delete Preset", height=17,
                    command=lambda *_: Preset.delete_preset(cmds.optionMenu(self.presetDropdown, query=True, value=True),
                                                            self.loaded_presets, self.jsonManager, self.ncloth_controls, self.update_preset_dropdown))
        cmds.setParent("..")

        #Creation of simulation settings input fields and sliders
        cmds.rowLayout(numberOfColumns=2)
        cmds.separator(h=10, style='none')
        cmds.setParent("..")
        cmds.rowLayout(numberOfColumns=3)
        cmds.text(label="", width=76)
        cmds.text(label="Preset Name:")
        self.fieldpresetName = cmds.textField("fieldpresetName", pht="Name...", width=200)

        cmds.setParent("..")
        cmds.separator(h=10, style='none')
        cmds.rowLayout(numberOfColumns=3)
        cmds.text(label="", width=52)
        cmds.text(label="Preset Description:")
        self.fieldpresetDesc = cmds.scrollField("fieldpresetDesc", w=300, h=45, ww=True, nl=3, font="plainLabelFont")
        cmds.setParent("..")

        cmds.separator(h=10, style='none')
        cmds.rowLayout(numberOfColumns=4)
        cmds.text(label="", width=62)
        cmds.text(label="Simulation Type:")
        cmds.text(label="", width=20)
        sim_type = cmds.text(label="nCloth")
        cmds.setParent("..")

        cmds.separator(h=10, style='none')
        self.bounce = cmds.floatSliderGrp(l= "Bounce", min = 0.000, max = 1.000, field = True, step=0.01, precision=3)
        self.friction = cmds.floatSliderGrp(l = "Friction", min = 0.0, max = 2.0, field = True, step=0.01, precision=3)
        self.stretch_res = cmds.floatSliderGrp(l = "Stretch Resistance", min = 0, max = 200, field = True, step=0.01, precision=3)
        self.comp_res = cmds.floatSliderGrp(l = "Compression Resistance", min = 0, max = 200, field = True, step=0.01, precision=3)
        self.bend_res = cmds.floatSliderGrp(l = "Bend Resistance", min = 0, max = 5, field = True, step=0.01, precision=3)
        self.bend_ang_do = cmds.floatSliderGrp(l = "Bend Angle Dropoff", min = 0, max = 5, field = True, step=0.01, precision=3)
        self.restitution_ang = cmds.floatSliderGrp(l= "Restitution Angle", min = 0, max =720.0, field = True, step=0.01, precision=3)
        self.rigidity =  cmds.floatSliderGrp(l= "Rigidity", min = 0, max = 10, field = True, step=0.01, precision=3)
        self.deform_res = cmds.floatSliderGrp(l="Deform Resistance", min = 0, max = 10, field = True, step=0.01, precision=3)
        self.rest_len_scale = cmds.floatSliderGrp(l = "Rest Length Scale", min = 0, max = 2, field=True, step=0.01, precision=3)
        self.mass = cmds.floatSliderGrp(l = "Mass", min = 0, max = 5, field = True, step=0.01, precision=3)

        self.tang_drag = cmds.floatSliderGrp(l = "Tangential Drag", min = 0, max = 5, field = True, step=0.01, precision=3)
        self.damp = cmds.floatSliderGrp(l = "Damp", min = 0, max = 10, field = True, step=0.01, precision=3)
        self.stretch_damp = cmds.floatSliderGrp(l = "Stretch Damp", min = 0, max =10, field = True, step=0.01, precision=3)

        cmds.rowLayout(numberOfColumns=2)
        cmds.text(label="", width=61)
        self.scaling_rel = cmds.optionMenu(l="Scaling Relation", width=200)
        cmds.menuItem(l="Link")
        cmds.menuItem(l="Object Space")
        cmds.menuItem(l="World Space")  
        cmds.setParent("..")

        cmds.rowLayout(numberOfColumns=2)
        cmds.text(label="", width=55)
        self.press_meth = cmds.optionMenu(l="Pressure Method", width=250)
        cmds.menuItem(l="Manual Pressure Setting")
        cmds.menuItem(l="Volume Tracking Model")
        cmds.setParent("..")

        self.start_press = cmds.floatSliderGrp(l = "Start Pressure", min = -1, max =2, field = True, step=0.01, precision=3)
        self.air_tight = cmds.floatSliderGrp(l="Air Tightness", min = 0.000, max = 1.000, field = True, step=0.01, precision=3)
        self.incomp = cmds.floatSliderGrp(l="Incompressibility", min = 0.000, max = 200.000, field = True, step=0.01, precision=3)
        self.max_ite = cmds.intSliderGrp(l = "Max Iterations", min = 0, max = 1000, field = True)
        self.po_rad = cmds.floatSliderGrp(l = "Push Out Radius", min = 0, max = 10, field = True, step=0.01, precision=3)

        #nCloth controls stored in a dictionary for later use
        self.ncloth_controls = {
                       'fieldpresetName' : self.fieldpresetName,
                       'fieldpresetDesc' : self.fieldpresetDesc,
                       'bounce' : self.bounce,
                       'friction' : self.friction,
                       'stretchResistance' : self.stretch_res,
                       'compressionResistance' : self.comp_res,
                       'bendResistance' : self.bend_res,
                       'bendAngleDropoff' : self.bend_ang_do,
                       'restitutionAngle' : self.restitution_ang,
                       'rigidity' : self.rigidity,
                       'deformResistance' : self.deform_res,
                       'restLengthScale' : self.rest_len_scale,
                       'pointMass' : self.mass,
                       'tangentialDrag' : self.tang_drag,
                       'damp' : self.damp,
                       'stretchDamp' : self.stretch_damp,
                       'scalingRelation' : self.scaling_rel,
                       'pressureMethod' : self.press_meth,
                       'startPressure' : self.start_press,
                       'airTightness' : self.air_tight,
                       'incompressibility' : self.incomp,
                       'maxIterations' : self.max_ite,
                       'pushOutRadius' : self.po_rad}  

        #Used to replace placeholder from init in creation of dropdown menu
        #Defined AFTER ncloth_controls and stored as a variable so dropdown can be updated dynamically
        self.ncloth_controls['presetDropdown'] = self.presetDropdown

        #Buttons for saving custom, applying collider and applying preset
        cmds.columnLayout("mainColumnLayout", adj=True)
        cmds.separator(h=5, style='none')  
        cmds.rowLayout(nc=3,columnWidth=[(1, 200), (2,200), (3,200)], columnAttach=[(1, 'both', 1), (2, 'both', 1), (3, 'both', 1)])
        cmds.button(label = "Save Custom", width =150, command = lambda *args: Preset.save_preset(
            self.get_current_settings(),
            self.jsonManager,
            self.ncloth_controls,
            self.update_preset_dropdown, self.loaded_presets))
        cmds.button(label = "Apply Collider", width =150, command = lambda x: self.apply_collider())
        cmds.button(label = "Apply", width =150, command = lambda x: self.identify_and_apply_preset())
        cmds.setParent("..")

        #Update the dropdown menu for presets with new/custom presets added by the user 
        self.update_preset_dropdown(self.loaded_presets, self.ncloth_controls)

        #Show UI window
        cmds.workspaceControl(dock_name, edit=True, width=800, height=900)
