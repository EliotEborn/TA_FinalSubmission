import maya.mel as mel
import sys
import os

#Get the Maya directory using the MEL command
file_path = mel.eval("getenv MAYA_APP_DIR ")

#Add the scripts\PAM folder path to the Maya directory
new_file_path = os.path.join(file_path, "scripts\PAM")

#Add scripts\PAM to Python's module search path
sys.path.append(new_file_path)


#Import classes
from json_manager import JsonManager
from ui_manager import UiManager

#Defines and initialise PAM Tool
def main():

    #Initilise JSON and load saved presets
    json_manager = JsonManager()
    presets = json_manager.load_presets()

    #Initialise and display main UI
    ui_manager = UiManager()
    ui_manager.create_UI()

#Run main only if this script is executed directly
if __name__ == "__main__":
    main()