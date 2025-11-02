import json
import os
import maya.mel as mel

#Import classes
from preset import Preset 

# JSON MANAGER CLASS #
# Handles loading, saving and managing presets in JSON file #
#######################################################################################
class JsonManager:
    
    #Initialise the JsonManager class
    def __init__(self, file_path=None):

        self.is_new_file = False

        #Use provided file path or if none then use default Maya directory 
        if file_path is None: 
             self.file_path = mel.eval("getenv MAYA_APP_DIR ")

        else:
            self.file_path = file_path

        #Combine the existing directory path with file named "presets.json" to get full path to Json File
        self.file_path = os.path.join(self.file_path, "presets.json")

        print(self.file_path)

         
        #Create a new JSON file at that location if it doesn't already exist
        if not os.path.exists(self.file_path):
             
            self.is_new_file = True
            with open(self.file_path, 'w') as file:
                json.dump({}, file, indent=4)
        
    
    #Load all presets from the JSON file and return as a dictionary of Preset objects 
    def load_presets(self):
            
        with open(self.file_path, 'r') as file:
            presets_data = json.load(file)
            presets= {}
            for name, values in presets_data.items():
                try:
                    presets[name] = Preset.from_dict(values)
                except TypeError as e:
                    print(f"Error loading preset {name}: {e}")
            return presets

    #Save a dictionary of Preset objects to the JSON File        
    def save_presets(self, presets):
        presets_data = {name: preset.to_dict() for name, preset in presets.items()}

        with open(self.file_path, 'w') as file:
            json.dump(presets_data, file, indent=4)
   
    def add_preset(self, name, preset):

        presets = self.load_presets() or {}
        print('add_preset')
        print(presets)

        presets[name] = preset
        self.save_presets(presets)
        

#######################################################################################