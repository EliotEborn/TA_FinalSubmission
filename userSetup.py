import maya.cmds as cmds 
import maya.mel as mel
import os
import sys
import maya.utils
file_path = mel.eval("getenv MAYA_APP_DIR ")

print(file_path)

new_file_path = os.path.join(file_path, "scripts\PAM")

sys.path.append(new_file_path)

from main_class import main

def CreateToolMenu():

    tool_menu_name = "MyMayaToolMenu"

    if cmds.menu(tool_menu_name, exists=True):
        cmds.deleteUI(tool_menu_name, menu=True)

    custom_tool_menu = cmds.menu(tool_menu_name, label="P.A.M.", parent="MayaWindow", tearOff = True)

    # Menu Item to Create a Cube
    cmds.menuItem(label="Physical Attribute Modifier", parent=custom_tool_menu, command=lambda val: main(), image="toolSettings.png")
    

maya.utils.executeDeferred(CreateToolMenu)

