import sys
import os
import json
from buildAux import *

def buildConduits(koraliDir):
 # Processing Conduits
 curdir = koraliDir + '/conduits' 
 
 # Detecting Conduits
 conduitPaths  = [x[0] for x in os.walk(curdir)][1:]
 for conduitPath in conduitPaths:
  conduitName = conduitPath.replace(curdir + '/', '')
  
  # Loading JSON Configuration
  conduitJsonFile = conduitPath + '/' + conduitName + '.json'
  if (not os.path.isfile(conduitJsonFile)): continue 
  with open(conduitJsonFile, 'r') as file: conduitJsonString = file.read()
  conduitConfig = json.loads(conduitJsonString)
  
  ####### Producing conduit.hpp
  
  # Producing private variable declarations
  conduitHeaderString = ''
  
  for v in conduitConfig["Conduit Configuration"]:
   conduitHeaderString += getVariableType(v) + ' ' + getCXXVariableName(v) + ';\n'
     
  # Loading template header .hpp file
  conduitTemplateHeaderFile = conduitPath + '/' + conduitName + '._hpp'
  with open(conduitTemplateHeaderFile, 'r') as file: conduitTemplateHeaderString = file.read()
  newHeaderString = conduitTemplateHeaderString.replace('private:', 'private: \n' + conduitHeaderString + '\n')
  
  # Saving new header .hpp file
  conduitNewHeaderFile = conduitPath + '/' + conduitName + '.hpp'
  print('[Korali] Creating: ' + conduitNewHeaderFile + '...')
  with open(conduitNewHeaderFile, 'w') as file: file.write(newHeaderString)
  
  ###### Producing conduit.cpp
  
  conduitCodeString = 'void Korali::Conduit::' + conduitConfig["Class"] + '::setConfiguration(nlohmann::json& js) \n{\n'
 
  # Consume Conduit Settings
  for v in conduitConfig["Conduit Configuration"]:
    conduitCodeString += consumeValue('js', conduitConfig["Alias"], getVariablePath(v), getCXXVariableName(v), getVariableType(v), getVariableDefault(v))
  
  conduitCodeString += '} \n\n'
  
  ###### Creating Conduit Get Configuration routine
  
  conduitCodeString += 'void Korali::Conduit::' + conduitConfig["Class"]  + '::getConfiguration(nlohmann::json& js) \n{\n\n'
  conduitCodeString += ' js["Type"] = "' + conduitConfig["Alias"] + '";\n'
 
  for v in conduitConfig["Conduit Configuration"]: 
    conduitCodeString += saveValue('js', getVariablePath(v), getCXXVariableName(v), getVariableType(v))
    
  conduitCodeString += '} \n\n'
  
  ###### Creating code file
  
  conduitBaseFileName = conduitPath + '/' + conduitName + '._cpp'
  conduitNewCodeFile = conduitPath + '/' + conduitName + '.cpp'
  baseFileTime = os.path.getmtime(conduitBaseFileName)
  newFileTime = baseFileTime
  if (os.path.exists(conduitNewCodeFile)): newFileTime = os.path.getmtime(conduitNewCodeFile)
  
  if (baseFileTime >= newFileTime):
    with open(conduitBaseFileName, 'r') as file: conduitBaseCodeString = file.read()
    conduitBaseCodeString += '\n\n' + conduitCodeString
    print('[Korali] Creating: ' + conduitNewCodeFile + '...')
    with open(conduitNewCodeFile, 'w') as file: file.write(conduitBaseCodeString)