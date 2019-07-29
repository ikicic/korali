import sys
import os
import json

#####################################################################

def getVariableName(v):
 cVarName = v["Name"].replace(" ", "")
 cVarName = '_' + cVarName[0].lower() + cVarName[1:]
 return cVarName
 
def getVariableDefault(v):
 return v.get('Default', '*none*')
 
def getVariableInfo(v, moduleName):
 varString = ''
 varString += '??? abstract "' + v["Name"] + '"\n\n'
 varString += '\t' + v["Description"] + '\n'
 varString += '\n'
 varString += '\t+ Default Value: ' + getVariableDefault(v) + '\n'
 varString += '\t+ Datatype: ' + v["Type"] + '\n'
 varString += '\t+ Syntax: \n\n' 
 varString += '\t```python\n\t\tkorali["Variables"][i]["' + moduleName + '"]["' + v["Name"] + '"] = *value*\n\t```\n\n'
 return varString

#####################################################################