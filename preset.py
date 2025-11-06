import maya.cmds as cmds
import maya.mel as mel

# PRESET CLASS #
#######################################################################################
class Preset:
    def __init__(self, name, description, bounce, friction, 
                 stretchResistance, compressionResistance, bendResistance, 
                 bendAngleDropoff, restitutionAngle, rigidity, deformResistance,
                 restLengthScale, pointMass, tangentialDrag, damp, stretchDamp,
                 scalingRelation, pressureMethod, startPressure, airTightness, incompressibility,
                 maxIterations, pushOutRadius):
        
        #Initialising all simulation attributes 
        self.name = name
        self.description = description
        
        self.bounce = bounce
        self.friction = friction
        self.stretchResistance = stretchResistance
        self.compressionResistance = compressionResistance
        self.bendResistance = bendResistance
        self.bendAngleDropoff = bendAngleDropoff
        self.restitutionAngle = restitutionAngle
        self.rigidity = rigidity
        self.deformResistance = deformResistance
        self.restLengthScale = restLengthScale
        self.pointMass = pointMass
        self.tangentialDrag = tangentialDrag
        self.damp = damp
        self.stretchDamp = stretchDamp
        self.scalingRelation = scalingRelation
        self.pressureMethod = pressureMethod
        self.startPressure = startPressure
        self.airTightness = airTightness
        self.incompressibility = incompressibility
        self.maxIterations = maxIterations
        self.pushOutRadius = pushOutRadius


#######################################################################################
# CONVERT PRESET DATA TO AND FROM DICTIONARIES #
#######################################################################################

    #Converts preset object attributes to a dictionary
    def to_dict(self):
        return self.__dict__
    
    #Create a preset object from a dictionary of attributes
    @classmethod
    def from_dict(cls, data):
        return cls(**data)
    
#######################################################################################
# APPLY PRESET #
#######################################################################################

    # Apply selected presets modified nCloth attributes to the selected mesh 
    def apply_preset(self):
        #Get currently selected objects in the scene
        selection = cmds.ls(selection=True)

        #If nothing is selected the user gets warned in the command line and a dialog box tells them they must select a mesh 
        if not selection: 
                cmds.warning("Please select a mesh to continue")
                cmds.confirmDialog(title="Confirm Action", message=f"Error: Please select a mesh to continue.", button=['OK'], dismissString='No')
                return

        #Dialog box confirms the user wants to apply the preset to the selection
        selection_str = ", ".join(selection)
        confirmation = cmds.confirmDialog(title="Confirm Action", message=f"Are you sure you'd like to apply Preset '{self.name}' to {selection_str}?", button=['Yes','No'], defaultButton='Yes', cancelButton='No', dismissString='No')
        if confirmation == 'Yes': 
            for obj in selection:
                cmds.select(obj, replace=True) 

                #Use MEL command to apply nCloth to the selected mesh/es for nCloth simulation (if mesh isn't already nCloth)
                mel.eval("createNCloth 0")

                #Get all shape nodes of the object
                shapes = cmds.listRelatives(obj, shapes=True) or []
                for shape in shapes:

                    #Find any connected nCloth nodes
                    connections = cmds.listConnections(shape, type="nCloth") or []

                    #Apply all preset attributes to the nCloth node
                    for ncloth_node in connections: 
                        cmds.setAttr(ncloth_node + ".bounce", self.bounce)
                        cmds.setAttr(ncloth_node + ".friction", self.friction)
                        cmds.setAttr(ncloth_node + ".stretchResistance", self.stretchResistance)
                        cmds.setAttr(ncloth_node + ".compressionResistance", self.compressionResistance)
                        cmds.setAttr(ncloth_node + ".bendResistance", self.bendResistance)
                        cmds.setAttr(ncloth_node + ".bendAngleDropoff", self.bendAngleDropoff)
                        cmds.setAttr(ncloth_node + ".restitutionAngle", self.restitutionAngle)
                        cmds.setAttr(ncloth_node + ".rigidity", self.rigidity)
                        cmds.setAttr(ncloth_node + ".deformResistance", self.deformResistance)
                        cmds.setAttr(ncloth_node + ".restLengthScale", self.restLengthScale)
                        cmds.setAttr(ncloth_node + ".pointMass", self.pointMass) 
                        cmds.setAttr(ncloth_node + ".tangentialDrag", self.tangentialDrag)
                        cmds.setAttr(ncloth_node + ".damp", self.damp)
                        cmds.setAttr(ncloth_node + ".stretchDamp", self.stretchDamp)
                        cmds.setAttr(ncloth_node + ".scalingRelation", self.scalingRelation)
                        cmds.setAttr(ncloth_node + ".pressureMethod", self.pressureMethod)
                        cmds.setAttr(ncloth_node + ".startPressure", self.startPressure)
                        cmds.setAttr(ncloth_node + ".airTightness", self.airTightness)
                        cmds.setAttr(ncloth_node + ".incompressibility", self.incompressibility)
                        cmds.setAttr(ncloth_node + ".maxIterations", self.maxIterations)
                        cmds.setAttr(ncloth_node + ".pushOutRadius", self.pushOutRadius)

        #User has cancelled the action
        else: 
            return

#######################################################################################
# SAVE PRESET #
#######################################################################################
    # Saves a new preset based on current UI settings and adds it to the presets dictionary
    #Class method used so the class can be called directly since we do not have a class instance 

    @staticmethod
    def save_preset(settings_dict, json_manager, ncloth_controls, update_dropdown_func, presets):

        #Ensures new name of custom preset has no leading or trailing spaces
        new_name = settings_dict.get("name", "").strip()

        #Saving prevented if preset name is empty or already exists
        if not new_name:
            cmds.warning("Preset name cannot be empty")
            return
        
        #Saving prevented if preset name is Custom -
        if new_name == "Custom -":
            cmds.warning("You cannot save a preset with name 'Custom -'. Please choose another name.")
            return

        #Saving prevented if custom name is already in use by another preset
        if new_name in presets:
            cmds.warning(f"Preset '{new_name}' already exists! Please choose another name.")
            return
        
        confirmation = cmds.confirmDialog(title="Confirm Save", message=f"Are you sure you want to save: '{new_name}'?", button=["Yes", "No"], dismissString="No")

        if confirmation == "Yes":

            #Create and save the new preset
            preset = Preset(**settings_dict)

            presets[new_name] = preset

            json_manager.add_preset(new_name, preset)

            #Loading presets after adding otherwise it breaks
            presets = json_manager.load_presets()

            update_dropdown_func(presets, ncloth_controls)
        else:
            return

#######################################################################################
#DELETE PRESET#
#######################################################################################

    @classmethod
    def delete_preset(cls, preset_name, loaded_presets, json_manager, ncloth_controls, update_dropdown_func):

        #Ensures preset name has no leading or trailing spaces
        preset_name = preset_name.strip()

        #Prevent deleting pre-defined presets
        protected_presets = ["Custom", "Custom -", "T-Shirt Cotton", "Silk", "Chiffon", "Heavy Denim", "Thick Leather", 
                           "Jelly", "Solid Rubber", "Concrete", "Lava", "Default"]

        if preset_name in protected_presets:
            cmds.warning(f"Preset '{preset_name}' is a built-in preset and cannot be deleted!")
            return

        if preset_name not in loaded_presets:
            cmds.warning(f"Preset '{preset_name}' not found!")


        confirmation = cmds.confirmDialog(title="Confirm Delete", message=f"Are you sure you want to delete preset '{preset_name}'?", button=["Yes", "No"], dismissString="No")

        if confirmation == "Yes":

            #Remove preset from dictionary
            loaded_presets.pop(preset_name)
            json_manager.save_presets(loaded_presets)

            #Update dropdown menu of presets
            update_dropdown_func(loaded_presets, ncloth_controls)
            
            #Reset UI fields
            if ncloth_controls.get('fieldpresetName'):
                cmds.textField(ncloth_controls['fieldpresetName'], edit=True, text="")

            if ncloth_controls.get('fieldpresetDesc'):
                cmds.scrollField(ncloth_controls['fieldpresetDesc'], edit=True, text="")

            #Set dropdown to display default
            dropdown = ncloth_controls.get('presetDropdown')
            if dropdown and "Custom" in loaded_presets:
                try:
                    cmds.optionMenu(dropdown, edit=True, value="Custom")
                except RuntimeError:
                    pass
    
        else:
            return

#######################################################################################  