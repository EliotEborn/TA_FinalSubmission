import maya.cmds as cmds
import maya.mel as mel
import sys
import os
import json
import webbrowser


from preset import Preset
from json_manager import JSON_Manager
from all_presets import presets

#UI MANAGER CLASS#
#######################################################################################
class UIManager: 
    
    def __init__(self):

        #Initialises JSON Manager and loads presets
        self.jsonManager = JSON_Manager()

        if self.jsonManager.is_new_file: 
            self.jsonManager.save_presets(presets)
            self.jsonManager.is_new_file = False

        self.loaded_presets = self.jsonManager.load_presets()  
        print("\nLoaded presets from JSON:")

        #INITIALISE BOTH CURRENT AND ORIGINAL SETTINGS DICTIONARIES AND CURRENT PRESET#
        self.current_settings = {}
        self.original_settings = {}
        self.current_preset = self.loaded_presets["Default"]

        #INITIALISE MENU LOOK-UP DICTIONARIES#
        self.scalingRel_menu = {'Link' : 0, 'Object Space' : 1, 'World Space' : 2}
        self.pressMeth_menu = {'Manual Pressure Setting' : 0, 'Volume Tracking Model' : 1}

        #STORING NCLOTH_CONTROLS DICTIONARY TO BE POPULATED LATER#
        self.ncloth_controls = {}

#######################################################################################
#BASIC FUNCTIONS#
#######################################################################################    

    #Open Autodesk Maya link on nCloth properties when INFO button pressed
    def open_webpage(self, url):
        webbrowser.open(url)

    #CHECK IF ANY SETTINGS HAS CHANGED FROM THE NAMED PRESET VALUES (EXCLUDING NAME)#
    def compare_settings(self, current_settings, original_settings):
        print("Settings inside setting_changed (before comparison):", current_settings)
        print("Original Settings:", original_settings)

        if not current_settings or not original_settings:
            return False

        #Iterate over each key and compare values 
        for key in current_settings:
            if key != "name":

                #Checks if current settings are different 
                if current_settings[key] != original_settings.get(key, None):
                    print(f"Setting changed: {key}")
            #SETTING OTHER THAN NAME HAS BEEN CHANGED
                    return True

        #NO RELEVANT SETTINGS HAVE CHANGED
        return False


    #UPDATE PRESET NAME IF SETTINGS HAVE CHANGED (EXCLUDING NAME)#
    #Move update preset name to on setting changed makes more sense
    def update_preset_name(self, preset_name, current_settings, original_settings):
        if self.compare_settings(current_settings, original_settings):

            #SET NEW NAME TO CUSTOM - (name of preset that was edited)
            updated_name = f"Custom - {preset_name}"
            print(f"Updated name: {updated_name}")
            return updated_name
        #Else, keep original name
        return preset_name
    
#######################################################################################
#SETTINGS CHANGED HANDLER#
#######################################################################################

    #CALLBACK TO UPDATE NAME WHEN SETTINGS CHANGED
    #CALL BACK WHEN ANY SETTING HAS BEEN CHANGED
    def on_setting_changed(self, *args):

        self.current_settings = self.get_current_settings()

        if self.compare_settings(self.current_settings, self.original_settings):
            new_name = f"Custom - {self.current_preset.name}"
        else:
            new_name = self.current_preset.name

        #look into using lambda here
        #when this get changed set boolean variable to true, therefore dont add custom - anymore
        #dont remmeber to set vriable back to false next time I change the preset from the dropdown
        #make sure when call update preset name it doesn't trigger the lambda 

        cmds.textField(self.ncloth_controls['fieldpresetName'], edit=True, text=new_name)

    #SETTING UI TO DISPLAY DEFAULT VALUES ON START UP#
    #REMOVE THIS COMMENTED OUT CODE#
    #current_preset = loaded_presets["Default"]

#######################################################################################
#UI UPDATE AND PRESET SELECTION#
#######################################################################################

    #UPDATE UI BASED OFF OF WHICH PRESET BUTTON WAS PRESSED#
    def select_preset(self, preset_name, *args):

        print(f"Preset Selected: {preset_name}")

        #Gets selected preset from presets dictionary 
        preset = self.loaded_presets.get(preset_name)

        #If preset exists in the presets dictionary the UI is updated with the correct settings
        if preset:

            self.current_preset = preset
            print(f"selected preset: {preset.name}")

            self.update_UI(preset)
            print(f"Update UI called with preset: {preset.name}")

            #GET CURRENT SETTINGS AND COMPARE WITH ORIGINAL SETTINGS
            self.original_settings = self.get_current_settings()
            self.current_settings = self.original_settings.copy()

            ##UPDATE PRESET NAME IF SETTINGS HAVE CHANGED
            updated_name = self.update_preset_name(preset_name, self.current_settings, self.original_settings)
            cmds.textField(self.ncloth_controls['fieldpresetName'], edit=True, text=updated_name)

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
            print(f"Preset '{preset_name}' not found!")


    #UPDATE UI BASED ON THE VALUES OF THE CURRENT PRESET#
    def update_UI(self, current_preset):

            #Update the preset name and description in their associated text fields
            cmds.textField(self.ncloth_controls['fieldpresetName'], edit = True, text=current_preset.name)
            cmds.scrollField(self.ncloth_controls['fieldpresetDesc'], edit = True, text=current_preset.description)

            #Update physical property sliders with current preset values
            cmds.floatSliderGrp(self.ncloth_controls['bounce'], edit = True, value=current_preset.bounce)
            cmds.floatSliderGrp(self.ncloth_controls['friction'], edit = True, value=current_preset.friction)
            cmds.intSliderGrp(self.ncloth_controls['stretchResistance'], edit = True, value=current_preset.stretchResistance)
            cmds.intSliderGrp(self.ncloth_controls['compressionResistance'], edit = True, value=current_preset.compressionResistance)
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

    #GATHER CURRENT SETTINGS PRESENT ON UI CONTROLS AND RETURN THEM AS A DICTIONARY#
    def get_current_settings(self): 
        settings = {
        "name" : cmds.textField(self.ncloth_controls['fieldpresetName'], query=True, text = True, ),
        "description" : cmds.scrollField(self.ncloth_controls['fieldpresetDesc'], query=True, text = True),
        "bounce" : cmds.floatSliderGrp(self.ncloth_controls['bounce'], query=True, value = True),
        "friction": cmds.floatSliderGrp(self.ncloth_controls['friction'], query=True, value = True),
        "stretchResistance": cmds.intSliderGrp(self.ncloth_controls['stretchResistance'], query=True, value = True),
        "compressionResistance": cmds.intSliderGrp(self.ncloth_controls['compressionResistance'], query=True, value = True),
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

        print("2nd Current settings:", settings)

        return settings

#######################################################################################
#COLLIDER AND TOOL ACTIONS#
#######################################################################################

    #APPLY PASSIVE COLLIDER TO SELECTED MESH#
    #NOTE: Passive collider must be added to meshes the user wants the simulated asset to interact with 
    def apply_collider(self):
        selection = cmds.ls(selection=True)
        if not selection: 
                cmds.warning("Please select a mesh to continue")
                cmds.confirmDialog(title="Confirm Action", message=f"Error: Please select a mesh to continue.", button=['OK'], dismissString='No')
                return

        selection_str = ", ".join(selection)
        confirmation = cmds.confirmDialog(title="Confirm Action", message=f"Are you sure you'd like to apply passive collider to: {selection_str}?", button=['Yes','No'], defaultButton='Yes', cancelButton='No', dismissString='No')

        if confirmation == 'Yes': 
            for obj in selection:
                cmds.select(obj, replace=True) 

                #Use MEL command to apply passive collider to the selected mesh/es for nCloth simulation
                mel.eval("makeCollideNCloth;")

    #CHECKS IF THE CURRENT UI SETTINGS MATCH THOSE OF AN EXISTING PRESET, IF SO THAT PRESET IS APPLIED TO THE SELECTED MESH, IF NOT "Custom" IS RETURNED#
    def does_preset_match(self, current_settings, preset):
        preset_name = preset.name
        print(f"\nComparing against: {preset_name}")
        match_found = True 

        for key in current_settings:
            preset_attr = getattr(preset, key, None)

            if current_settings[key] != preset_attr:
                print(f"Mismatch on '{key}': UI={current_settings[key]}, Preset={preset_attr}")
                match_found = False
        if match_found: 
            return preset_name
        return "Custom"

    #IDENTIFIES IF CURRENT UI SETTINGS MATCH EXISTING PRESET, THEN APPLIED EITHER THE MATCHED PRESET OR CUSTOM SETTINGS#
    #UI CLASS
    def identify_and_apply_preset(self):
        current_settings = self.get_current_settings()
        preset_matches = self.does_preset_match(current_settings, self.current_preset)
        print("Matched Preset:", preset_matches)

        #Apply matched
        if preset_matches != "Custom":
            self.loaded_presets[preset_matches].applypreset()
        else:
            custom_preset = Preset(**current_settings)
            custom_preset.apply_preset()

    #RESETS TOOL TO DEFAULT VALUES (this is defined in the Presets dictionary)#
    #NEED TO CHANGE IT SO  OPTION MENU ALSO RESETS TO CUSTOM (DEFAULT)
    def reset_tool(self):
        #Default_Custom = presets["Custom"]
        custom_preset = self.loaded_presets["Custom"]
        self.current_preset = custom_preset
        self.update_UI(custom_preset)
        self.original_settings = self.get_current_settings()
        self.current_settings = self.original_settings.copy()
        cmds.optionMenu(self.ncloth_controls['presetDropdown'], edit=True, value="Custom")

    #CREATES BUTTONS FOR EACH PRESET IN THE PRESET DICTIONARY AND ADDS THEM TO THE UI#
    #UI CLASS
    #Since changing to drop down instead of side scroller and individual buttons, need to clear existing menu ITEMS rather than deleting children of the layout 
    #Once all items are cleared the dropdown is then filled with all the preset names from the presets dicitonary (except "Default")
    #NEED TO ADD A CUSTOM PRESET WHICH IS ALL BLANK 
    def update_preset_dropdown(self, loaded_presets, ncloth_controls):
        dropdown = ncloth_controls.get('presetDropdown')

        if not dropdown:
            print("Dropdown not found!")
            return

        menu_items = cmds.optionMenu(dropdown, query=True, itemListLong=True) or []
        for item in menu_items:
            cmds.deleteUI(item)

        for preset_name in loaded_presets.keys():

            if not preset_name or preset_name == "Default":

                continue

            cmds.menuItem(label=preset_name, parent=dropdown)

#######################################################################################
#UI CREATION#
#######################################################################################
    #FUNCTION TO CREATE THE UI#
    def create_UI(self):

        #Checks if the window already exists and deletes it if it does
        if cmds.window('win_maya_ui', ex=True):
            cmds.deleteUI('win_maya_ui', window=True)

        #Creating Main Window
        cmds.window('win_maya_ui', title='Tool Settings', widthHeight=(500,600))

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
        self.stretch_res = cmds.intSliderGrp(l = "Stretch Resistance", min = 0, max = 200, field = True)
        self.comp_res = cmds.intSliderGrp(l = "Compression Resistance", min = 0, max = 200, field = True)
        self.bend_res = cmds.floatSliderGrp(l = "Bend Resistance", min = 0, max = 5, field = True, step=0.01, precision=3)
        self.bend_ang_do = cmds.floatSliderGrp(l = "Bend Angle Dropoff", min = 0, max = 5, field = True, step=0.01, precision=3)
        self.restitution_ang = cmds.floatSliderGrp(l= "Resitution Angle", min = 0, max =720.0, field = True, step=0.01, precision=3)
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

        #USED TO REPLACE PLACEHOLDER IN CREATION OF DROPDOWN MENU
        #Defined AFTER ncloth_controls and stored as a variable so dropdown can be updated dynamically
        self.ncloth_controls['presetDropdown'] = self.presetDropdown


        #Buttons for saving custom, applying collider and applying preset
        #ADD JSONMANAGER TO SAVE PRESET WHEN CLASS IS ADDED
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
        cmds.showWindow('win_maya_ui')
