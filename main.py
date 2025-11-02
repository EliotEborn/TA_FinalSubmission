import maya.cmds as cmds
import maya.mel as mel
import sys
import os

file_path = mel.eval("getenv MAYA_APP_DIR ")

print(file_path)

new_file_path = os.path.join(file_path, "scripts\PAM")
  
sys.path.append(new_file_path)

print(new_file_path)

from preset import Preset as Preset
from json_manager import JSON_Manager
from ui_manager import UIManager
from all_presets import presets as presets

print("this is a test")
def main():

    json_manager = JSON_Manager()
    presets = json_manager.load_presets()

    ui_manager = UIManager()
    ui_manager.create_UI()

if __name__ == "__main__":
    main()