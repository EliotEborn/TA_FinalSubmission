from preset import Preset
from json_manager import JSON_Manager
import os

#PRESET OBJECTS#
#######################################################################################
Default_Custom = Preset(name="", description="", bounce=0.0, friction=0.00,
                 stretchResistance=0.0, compressionResistance=0.0, bendResistance=0.0, 
                 bendAngleDropoff=0.0, restitutionAngle=0.0, rigidity=0.0, deformResistance=0.0,
                 restLengthScale=0.0, pointMass=0.00, tangentialDrag=0.00, damp=0.00, stretchDamp=0.0,
                 scalingRelation=0, pressureMethod=0, startPressure=0.0, airTightness=0.0, incompressibility=0.0,
                 maxIterations=0, pushOutRadius=0.0)
TShirt_Cotton = Preset(name="T-Shirt Cotton", description="Cotton",  bounce=0.0, friction=0.30, 
                 stretchResistance=35.0, compressionResistance=10.0, bendResistance=0.10, 
                 bendAngleDropoff=0.4, restitutionAngle=0.0, rigidity=0.0, deformResistance=0.0,
                 restLengthScale=1.0, pointMass=0.60, tangentialDrag=0.10, damp=0.80, stretchDamp=0.0,
                 scalingRelation=1, pressureMethod=0, startPressure=0.0, airTightness=0.0, incompressibility=0.0,
                 maxIterations=1000, pushOutRadius=10.0)

Silk = Preset(name="Silk", description="Silk",  bounce=0.0, friction=0.05,
                 stretchResistance=60.0, compressionResistance=10.0, bendResistance=0.05, 
                 bendAngleDropoff=0.3, restitutionAngle=0.0, rigidity=0.0, deformResistance=0.0,
                 restLengthScale=1.0, pointMass=0.05, tangentialDrag=0.05, damp=0.20, stretchDamp=0.0,
                 scalingRelation=1, pressureMethod=0, startPressure=0.0, airTightness=0.0, incompressibility=0.0,
                 maxIterations=1000, pushOutRadius=0.108)

Chiffon = Preset(name="Chiffon", description="Chiffon",  bounce=0.0, friction=0.90,
                 stretchResistance=40.0, compressionResistance=20.0, bendResistance=0.2, 
                 bendAngleDropoff=0.6, restitutionAngle=0.0, rigidity=0.0, deformResistance=0.0,
                 restLengthScale=1.0, pointMass=0.15, tangentialDrag=0.40, damp=2.0, stretchDamp=0.0,
                 scalingRelation=1, pressureMethod=0, startPressure=0.0, airTightness=0.0, incompressibility=0.0,
                 maxIterations=1000, pushOutRadius=0.108)

Heavy_Denim = Preset(name="Heavy Denim", description="Heavy Denim",  bounce=0.0, friction=0.80,
                 stretchResistance=50.0, compressionResistance=20.0, bendResistance=0.4, 
                 bendAngleDropoff=0.603, restitutionAngle=0.0, rigidity=0.0, deformResistance=0.0,
                 restLengthScale=1.0, pointMass=2.0, tangentialDrag=0.10, damp=0.80, stretchDamp=0.0,
                 scalingRelation=1, pressureMethod=0, startPressure=0.0, airTightness=0.0, incompressibility=0.0,
                 maxIterations=1000, pushOutRadius=0.108)

Thick_Leather = Preset(name="Thick Leather", description="Thick Leather",  bounce=0.0, friction=0.60,
                 stretchResistance=40.0, compressionResistance=40.0, bendResistance=10.0, 
                 bendAngleDropoff=0.727, restitutionAngle=0.0, rigidity=0.0, deformResistance=0.0,
                 restLengthScale=1.0, pointMass=3.0, tangentialDrag=0.20, damp=8.00, stretchDamp=0.0,
                 scalingRelation=1, pressureMethod=0, startPressure=0.0, airTightness=0.0, incompressibility=0.0,
                 maxIterations=1000, pushOutRadius=10.0)

Jelly = Preset(name="Jelly", description="Jelly",  bounce=0.5, friction=0.05,
                 stretchResistance=20.0, compressionResistance=2.0, bendResistance=0.01, 
                 bendAngleDropoff=0.1, restitutionAngle=0.0, rigidity=0.0, deformResistance=0.1,
                 restLengthScale=1.0, pointMass=0.30, tangentialDrag=0.05, damp=0.05, stretchDamp=0.0,
                 scalingRelation=1, pressureMethod=0, startPressure=0.2, airTightness=0.8, incompressibility=5.0,
                 maxIterations=1000, pushOutRadius=0.1)

Solid_Rubber = Preset(name="Solid Rubber", description="Solid Rubber",  bounce=0.0, friction=2.0,
                 stretchResistance=20.0, compressionResistance=20.0, bendResistance=20.0, 
                 bendAngleDropoff=0.0, restitutionAngle=360, rigidity=0.3, deformResistance=0.0,
                 restLengthScale=1.0, pointMass=2.0, tangentialDrag=0.00, damp=0.80, stretchDamp=0.0,
                 scalingRelation=1, pressureMethod=1, startPressure=0.0, airTightness=1.0, incompressibility=20.0,
                 maxIterations=500, pushOutRadius=0.0)

Concrete = Preset(name="Concrete", description="Concrete",  bounce=0.0, friction=1.00,
                 stretchResistance=20.0, compressionResistance=20.0, bendResistance=0.00, 
                 bendAngleDropoff=0.0, restitutionAngle=360, rigidity=4.0, deformResistance=6.0,
                 restLengthScale=1.0, pointMass=20.0, tangentialDrag=0.00, damp=1.00, stretchDamp=0.0,
                 scalingRelation=1, pressureMethod=0, startPressure=0.0, airTightness=0.0, incompressibility=0.0,
                 maxIterations=500, pushOutRadius=0.0)

Lava = Preset(name="Lava", description="Lava",  bounce=0.0, friction=0.603,
                 stretchResistance=0.01, compressionResistance=0.01, bendResistance=0.70, 
                 bendAngleDropoff=0.851, restitutionAngle=720, rigidity=0.0, deformResistance=0.0,
                 restLengthScale=1.0, pointMass=10.0, tangentialDrag=0.0, damp=1.5, stretchDamp=0.10,
                 scalingRelation=1, pressureMethod=1, startPressure=0.0, airTightness=1.0, incompressibility=5.0,
                 maxIterations=500, pushOutRadius=10.0)

Default = Preset(name="Default", description="",  bounce=0.0, friction=0.00,
                 stretchResistance=0.0, compressionResistance=0.0, bendResistance=0.0, 
                 bendAngleDropoff=0.0, restitutionAngle=0.0, rigidity=0.0, deformResistance=0.0,
                 restLengthScale=0.0, pointMass=0.00, tangentialDrag=0.00, damp=0.00, stretchDamp=0.0,
                 scalingRelation=0, pressureMethod=0, startPressure=0.0, airTightness=0.0, incompressibility=0.0,
                 maxIterations=0, pushOutRadius=0.0)
#######################################################################################

#PRESET DICTIONARY#
#######################################################################################
presets = {
    "Custom" : Default_Custom,
    "T-Shirt Cotton" : TShirt_Cotton,
    "Silk" : Silk,
    "Chiffon" : Chiffon,
    "Heavy Denim" : Heavy_Denim,
    "Thick Leather" : Thick_Leather,
    "Jelly" : Jelly,
    "Solid Rubber" : Solid_Rubber,
    "Concrete" : Concrete,
    "Lava" : Lava,
    "Default" : Default
}
#######################################################################################


