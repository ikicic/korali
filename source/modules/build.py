import sys
import os
import json

####################################################################
# Helper Functions
####################################################################

def getVariableType(v):
 # Replacing bools with ints for Python compatibility
 return v['Type'].replace('bool', 'int')
 
def getCXXVariableName(v):
 cVarName = ''
 for name in v: cVarName += name 
 cVarName = cVarName.replace(" ", "")
 cVarName = cVarName.replace("(", "")
 cVarName = cVarName.replace(")", "")
 cVarName = cVarName.replace("+", "")
 cVarName = cVarName.replace("-", "")
 cVarName = cVarName.replace("[", "")
 cVarName = cVarName.replace("]", "")
 cVarName = '_' + cVarName[0].lower() + cVarName[1:]
 return cVarName

def getVariablePath(v):
 cVarPath = ''
 for name in v["Name"]: cVarPath += '["' + name + '"]' 
 return cVarPath
 
def getVariableDefault(v):
 return v.get('Default', '')
 
def getVariableEnabledDefault(v):
 if ( v.get('Default', '') ): return 'true'
 return 'false'
 
def getVariableDescriptor(v):
 if ('size_t' in v['Type']): return '%lu'
 if ('int' in v['Type']): return '%d'
 if ('bool' in v['Type']): return '%b'
 if ('double' in v['Type']): return '%e'
 if ('float' in v['Type']): return '%e'
 print('Error: Unrecognized type')
 exit(-1)
 
#####################################################################

def consumeValue(base, moduleName, path, varName, varType, varDefault):
 cString = '\n'
 
 if ('std::function' in varType):
  cString += ' ' + varName + ' = __korali_models[' + base + path + '.get<size_t>()];\n'
  cString += '   eraseValue(' + base + ', "' + path.replace('"', "'") + '");\n'
  return cString 
  
 if (varType == 'Korali::Distribution::Base*'):
  cString +=  ' ' + varName + ' = Korali::Distribution::Base::getDistribution(' + base + path + ');\n'
  cString += ' eraseValue(' + base + ', "' + path.replace('"', "'") + '");\n' 
  return cString
 
 if (varType == 'std::vector<Korali::Distribution::Base*>'):
  cString += ' for(size_t i = 0; i < ' + base + path + '.size(); i++) ' + varName + '.push_back(Korali::Distribution::Base::getDistribution(' + base + path + '[i]));\n'
  cString += ' eraseValue(' + base + ', "' + path.replace('"', "'") + '");\n\n' 
  return cString
  
 if ('Korali::' in varType):
  if (varDefault): cString = ' if (! isDefined(' + base + ', "' + path.replace('"', "'") + '[\'Type\']")) ' + base + path + '["Type"] = "' + varDefault + '"; \n'
  cString += ' ' + varName + ' = ' + varType + '::getModule(' + base + path + ');\n'
  cString += ' ' + varName + '->setConfiguration(' + base + path + ');\n'
  return cString  
  
 cString += ' if (isDefined(' + base + ', "' + path.replace('"', "'") + '"))  \n  { \n'
 cString += '   ' + varName + ' = ' + base + path + '.get<' + varType + '>();\n' 
 cString += '   eraseValue(' + base + ', "' + path.replace('"', "'") + '");\n'
 cString += '  }\n'
 
 if (varDefault == 'Korali Skip Default'):
  return cString
 
 cString += '  else '
 if (varDefault == ''):
  cString += '  Korali::logError("No value provided for mandatory setting: ' + path.replace('"', "'") + ' required by ' + moduleName + '.\\n"); \n'
 else:
  if ("std::string" in varType): varDefault = '"' + varDefault + '"'
  cString += varName + ' = ' + varDefault + ';'
   
 cString += '\n'
 return cString

#####################################################################

def saveValue(base, path, varName, varType):
 sString = '   ' + base + path + ' = ' + varName + ';\n'

 if (varType == 'Korali::Distribution::Base*'):
  sString =  ' ' + varName + '->getConfiguration(' + base + path + ');\n'
 
 if (varType == 'Korali::Solver::Base*'):
  sString =  ' ' + varName + '->getConfiguration(' + base + path + ');\n'
  
 if (varType == 'Korali::Problem::Base*'):
  sString =  ' ' + varName + '->getConfiguration(' + base + path + ');\n' 
 
 if (varType == 'Korali::Conduit::Base*'):
  sString =  ' ' + varName + '->getConfiguration(' + base + path + ');\n'  
  
 if (varType == 'std::vector<Korali::Distribution::Base*>'):
  sString  = ' for(size_t i = 0; i < ' + varName + '.size(); i++) ' + varName + '[i]->getConfiguration(' + base + path + '[i]);\n'
  
 if ('std::function' in varType):
  sString = ''
  
 return sString
 
####################################################################

def createSetConfiguration(module):
 codeString = 'void ' + module["C++ Class"] + '::setConfiguration(nlohmann::json& js) \n{\n'
  
 # Checking whether solver is accepted
 if 'Compatible Solvers' in module:
  codeString += ' bool __acceptedSolver = false;\n'
  for v in module["Compatible Solvers"]: 
   codeString += ' if (_k->_solver->getType() == "' + v + '") __acceptedSolver = true;\n'
  codeString += ' if (__acceptedSolver == false) Korali::logError("Selected solver %s not compatible with  type ' + module["Name"] + '", _k->_solver->getType().c_str()); \n\n' 
 
 # Consume Configuration Settings
 if 'Configuration Settings' in module:
  for v in module["Configuration Settings"]:
   codeString += consumeValue('js', module["Alias"], getVariablePath(v), getCXXVariableName(v["Name"]), getVariableType(v), getVariableDefault(v))
 
 if 'Internal Settings' in module: 
  for v in module["Internal Settings"]:
   codeString += consumeValue('js', module["Alias"], '["Internal"]' + getVariablePath(v),  getCXXVariableName(v["Name"]), getVariableType(v), 'Korali Skip Default')
  
 if 'Termination Criteria' in module:
  for v in module["Termination Criteria"]:
   codeString += consumeValue('js', module["Alias"], '["Termination Criteria"]' + getVariablePath(v), getCXXVariableName(v["Name"]), getVariableType(v), getVariableDefault(v))
 
 if 'Conditional Variables' in module:
  for v in module["Conditional Variables"]:
   codeString += ' ' + getCXXVariableName(v) + 'Conditional = "";\n'
   codeString += ' if(js' + getVariablePath(v) + '.is_number()) ' + getCXXVariableName(v) + ' = js' + getVariablePath(v) + ';\n'
   codeString += ' if(js' + getVariablePath(v) + '.is_string()) ' + getCXXVariableName(v) + 'Conditional = js' + getVariablePath(v) + ';\n'
   codeString += ' eraseValue(js, "' + getVariablePath(v).replace('"', "'") + '");\n\n'
 
 codeString += ' if(isEmpty(js) == false) Korali::logError("Unrecognized settings for ' + module["Name"] + ' (' + module["Alias"] + '): \\n%s\\n", js.dump(2).c_str());\n'
 codeString += '} \n\n'
  
 return codeString
  
####################################################################
  
def createGetConfiguration(module):  
 codeString = 'void ' + module["C++ Class"]  + '::getConfiguration(nlohmann::json& js) \n{\n\n'
 
 if 'Configuration Settings' in module:
  for v in module["Configuration Settings"]: 
   codeString += saveValue('js', getVariablePath(v), getCXXVariableName(v["Name"]), getVariableType(v))
 
 if 'Termination Criteria' in module:
  for v in module["Termination Criteria"]: 
   codeString += saveValue('js', getVariablePath(v), getCXXVariableName(v["Name"]), getVariableType(v))
   
 if 'Internal Settings' in module:   
  for v in module["Internal Settings"]: 
   codeString += saveValue('js', '["Internal"]' + getVariablePath(v), getCXXVariableName(v["Name"]), getVariableType(v))
   
 if 'Conditional Variables' in module: 
  for v in module["Conditional Variables"]:
   codeString += ' if(' + getCXXVariableName(v) + 'Conditional == "") js' + getVariablePath(v) + ' = ' + getCXXVariableName(v) + ';\n'
   codeString += ' if(' + getCXXVariableName(v) + 'Conditional != "") js' + getVariablePath(v) + ' = ' + getCXXVariableName(v) + 'Conditional;\n'
 
 codeString += '} \n\n'
 
 return codeString

####################################################################

def createCheckTermination(module):  
 codeString = 'bool ' + module["C++ Class"]  + '::checkTermination()\n'
 codeString += '{\n'
 codeString += ' bool hasFinished = false;\n\n'
 
 if 'Termination Criteria' in module:
  for v in module["Termination Criteria"]: 
   codeString += ' if (' + v["Criteria"] + ')\n'
   codeString += ' {\n'
   codeString += '  Korali::logInfo("Minimal", "' + module["Alias"] + ' Termination Criteria met: \\"' + getVariablePath(v).replace('"', "'") + '\\" (' + getVariableDescriptor(v) + ').\\n", ' + getCXXVariableName(v["Name"])  +');\n'
   codeString += '  hasFinished = true;\n'
   codeString += ' }\n\n'
  
 codeString += ' return hasFinished;\n'
 codeString += '}'
 
 return codeString
 
####################################################################

def createHeaderDeclarations(module):  
 headerString = ''
 
 if 'Configuration Settings' in module:
  for v in module["Configuration Settings"]:
   headerString += ' ' + getVariableType(v) + ' ' + getCXXVariableName(v["Name"]) + ';\n'
 
 if 'Internal Settings' in module:    
  for v in module["Internal Settings"]:
   headerString += ' ' + getVariableType(v) + ' ' + getCXXVariableName(v["Name"]) + ';\n'
 
 if 'Termination Criteria' in module:
  for v in module["Termination Criteria"]:
   headerString += ' ' + getVariableType(v) + ' ' + getCXXVariableName(v["Name"]) + ';\n'
 
 if 'Variables Configuration' in module:
  varStructName = '_' + getCXXVariableName(module["Name"]) + '_variableStruct'
  headerString += '\n struct ' + varStructName + ' {\n'
  for v in module["Variables Configuration"]:
   headerString += '  ' + getVariableType(v) + ' ' + getCXXVariableName(v["Name"]) + ';\n'
  headerString += ' };\n'
  headerString += ' std::vector<' + varStructName + '> _variables;\n'
 
 return headerString
 
####################################################################
# Main Parser Routine
####################################################################

currentDir = os.path.abspath(os.path.dirname(os.path.realpath(__file__)))
koraliDir = currentDir + '/../' 

# modules List
moduleDetectionList = ''
moduleIncludeList = ''

# Detecting modules' json file
for moduleDir, relDir, fileNames in os.walk(currentDir):
 for fileName in fileNames: 
  if '.json' in fileName:
   with open(moduleDir + '/' + fileName, 'r') as file: moduleConfig = json.load(file)
   moduleName = fileName.replace('.json', '')
   
   ####### Adding module to list
   relpath = os.path.relpath(moduleDir, koraliDir)
   filepath = os.path.join(relpath, moduleName + '.hpp')
   moduleIncludeList += '#include "' + filepath + '" \n'
   moduleDetectionList += '  if(moduleType == "' + moduleConfig["Alias"] + '") module = new ' + moduleConfig["C++ Class"] + '();\n'
   
   ###### Producing module code
   
   ## Adding getType()
   getTypeString = 'std::string ' + moduleConfig["C++ Class"] + '::getType() { return "' + moduleConfig["Alias"] + '"; }'
   
   moduleCodeString = createSetConfiguration(moduleConfig)
   moduleCodeString += createGetConfiguration(moduleConfig)
   moduleCodeString += createCheckTermination(moduleConfig)
   moduleCodeString += '\n\n' + getTypeString + '\n\n'
 
   ####### Producing header file
   
   # Loading template header .hpp file
   moduleTemplateHeaderFile = moduleDir + '/' + moduleName + '._hpp'
   with open(moduleTemplateHeaderFile, 'r') as file: moduleTemplateHeaderString = file.read()
   
   # Adding overridden function declarations
   functionOverrideString = ''
   functionOverrideString += ' std::string getType() override;\n'
   functionOverrideString += ' bool checkTermination() override;\n'
   functionOverrideString += ' void getConfiguration(nlohmann::json& js) override;\n'
   functionOverrideString += ' void setConfiguration(nlohmann::json& js) override;\n'
   newHeaderString = moduleTemplateHeaderString.replace('public:', 'public: \n' + functionOverrideString + '\n')
   
   # Adding declarations
   declarationsString = createHeaderDeclarations(moduleConfig)
   newHeaderString = newHeaderString.replace('public:', 'public: \n' + declarationsString + '\n')
   
   # Saving new header .hpp file
   moduleNewHeaderFile = moduleDir + '/' + moduleName + '.hpp'
   print('[Korali] Creating: ' + moduleNewHeaderFile + '...')
   with open(moduleNewHeaderFile, 'w') as file: file.write(newHeaderString)
   
   ###### Creating code file
   
   moduleBaseCodeFileName = moduleDir + '/' + moduleName + '._cpp'
   moduleNewCodeFile = moduleDir + '/' + moduleName + '.cpp'
   baseFileTime = os.path.getmtime(moduleBaseCodeFileName)
   newFileTime = baseFileTime
   if (os.path.exists(moduleNewCodeFile)): newFileTime = os.path.getmtime(moduleNewCodeFile)
   
   if (baseFileTime >= newFileTime):
    with open(moduleBaseCodeFileName, 'r') as file: moduleBaseCodeString = file.read()
    moduleBaseCodeString += '\n\n' + moduleCodeString
    print('[Korali] Creating: ' + moduleNewCodeFile + '...')
    with open(moduleNewCodeFile, 'w') as file: file.write(moduleBaseCodeString)

###### Updating module configuration file 

moduleBaseCodeFileName = currentDir + '/base._cpp' 
moduleNewCodeFile = currentDir + '/base.cpp'
baseFileTime = os.path.getmtime(moduleBaseCodeFileName)
newFileTime = baseFileTime
if (os.path.exists(moduleNewCodeFile)): newFileTime = os.path.getmtime(moduleNewCodeFile)

if (baseFileTime >= newFileTime):
  with open(moduleBaseCodeFileName, 'r') as file: moduleBaseCodeString = file.read()
  newBaseString = moduleBaseCodeString.replace('// Module Include List',  moduleIncludeList)
  newBaseString = newBaseString.replace(' // Module Selection List', moduleDetectionList)
  print('[Korali] Creating: ' + moduleNewCodeFile + '...')
  with open(moduleNewCodeFile, 'w') as file: file.write(newBaseString)

###### Creating base header file

moduleBaseHeaderFileName = currentDir + '/base._hpp'
moduleNewHeaderFile = currentDir + '/base.hpp'
with open(moduleBaseHeaderFileName, 'r') as file: moduleBaseHeaderString = file.read()
newBaseString = moduleBaseHeaderString
print('[Korali] Creating: ' + moduleNewHeaderFile + '...')
with open(moduleNewHeaderFile, 'w+') as file: file.write(newBaseString)