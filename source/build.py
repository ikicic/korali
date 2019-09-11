import sys
import os
import json

####################################################################
# Helper Functions
####################################################################

def getVariableType(v):
 # Replacing bools with ints for Python compatibility
 return v['Type'].replace('bool', 'int').replace('std::function<void(Korali::Sample&)>', 'size_t')
 
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
  cString += ' ' + varName + ' = ' + base + path + '.get<size_t>();\n'
  cString += '   Korali::JsonInterface::eraseValue(' + base + ', "' + path.replace('"', "'") + '");\n'
  return cString 

 if ('Korali::Sample' in varType):
  cString = ''
  return cString

 if ('std::vector<Korali::Variable' in varType):
  baseType = varType.replace('std::vector<', '').replace('>','')
  cString += ' ' + varName + '.clear();\n'
  cString += ' for(size_t i = 0; i < ' + base + path + '.size(); i++) ' + varName + '.push_back(new Korali::Variable);\n'
  return cString
  
 if ('std::vector<Korali::Variable*>' in varType):
  baseType = varType.replace('std::vector<', '').replace('>','')
  cString += ' for(size_t i = 0; i < ' + base + path + '.size(); i++) ' + varName + '.push_back(new Korali::Variable());\n'
  cString += ' Korali::JsonInterface::eraseValue(' + base + ', "' + path.replace('"', "'") + '");\n\n' 
  return cString
  
 if ('std::vector<Korali::' in varType):
  baseType = varType.replace('std::vector<', '').replace('>','')
  cString += ' for(size_t i = 0; i < ' + base + path + '.size(); i++) ' + varName + '.push_back((' + baseType + ')Korali::Module::getModule(' + base + path + '[i]));\n'
  cString += ' Korali::JsonInterface::eraseValue(' + base + ', "' + path.replace('"', "'") + '");\n\n' 
  return cString
  
 if ('Korali::' in varType):
  if (varDefault): cString = ' if (! Korali::JsonInterface::isDefined(' + base + ', "' + path.replace('"', "'") + '[\'Type\']")) ' + base + path + '["Type"] = "' + varDefault + '"; \n'
  cString += ' ' + varName + ' = dynamic_cast<' + varType + '>(Korali::Module::getModule(' + base + path + '));\n'
  return cString  
  
 cString += ' if (Korali::JsonInterface::isDefined(' + base + ', "' + path.replace('"', "'") + '"))  \n  { \n'
 cString += '   ' + varName + ' = ' + base + path + '.get<' + varType + '>();\n' 
 cString += '   Korali::JsonInterface::eraseValue(' + base + ', "' + path.replace('"', "'") + '");\n'
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

 if ('Korali::Sample' in varType):
  sString = ''
  return sString
  
 if ('Korali::Variable' in varType):
  sString = ''
  return sString
  
 if ('std::vector<Korali::' in varType):
  sString = ' for(size_t i = 0; i < ' + varName + '.size(); i++) ' + varName + '[i]->getConfiguration(' + base + path + '[i]);\n'
  return sString
    
 if ('Korali::' in varType):
  sString =  ' ' + varName + '->getConfiguration(' + base + path + ');\n'  
  return sString
    
 sString = '   ' + base + path + ' = ' + varName + ';\n'  
 return sString

####################################################################
 
def getParentClass(module):
  className = module["C++ Class"]
  parentName = className.rsplit('::', 1)[0]
  if ('::Base' in className): parentName = className.rsplit('::', 2)[0]
  parentName += '::Base'
  if (parentName == 'Korali::Base'): parentName = 'Korali::Module'
  return parentName
 
####################################################################

def createSetConfiguration(module):
 codeString = 'void ' + module["C++ Class"] + '::setConfiguration(nlohmann::json& js) \n{\n'
  
 # Consume Configuration Settings
 if 'Configuration Settings' in module:
  for v in module["Configuration Settings"]:
   codeString += consumeValue('js', module["Alias"], getVariablePath(v), getCXXVariableName(v["Name"]), getVariableType(v), getVariableDefault(v))
  
 if 'Internal Settings' in module: 
  for v in module["Internal Settings"]:
   varDefault = getVariableDefault(v)
   if (varDefault == ''): varDefault = 'Korali Skip Default'
   codeString += consumeValue('js', module["Alias"], '["Internal"]' + getVariablePath(v),  getCXXVariableName(v["Name"]), getVariableType(v), varDefault)
  
 if 'Termination Criteria' in module:
  for v in module["Termination Criteria"]:
   codeString += consumeValue('js', module["Alias"], '["Termination Criteria"]' + getVariablePath(v), getCXXVariableName(v["Name"]), getVariableType(v), getVariableDefault(v))
 
 if 'Variables Configuration' in module:
  codeString += ' for (size_t i = 0; i < _k->_js["Variables"].size(); i++) { \n'
  for v in module["Variables Configuration"]:
   codeString += consumeValue('_k->_js["Variables"][i]', module["Alias"], getVariablePath(v), '_k->_variables[i]->' + getCXXVariableName(v["Name"]), getVariableType(v), getVariableDefault(v))
  codeString += ' } \n'
   
 if 'Conditional Variables' in module:
  for v in module["Conditional Variables"]:
   codeString += ' ' + getCXXVariableName(v["Name"]) + 'Conditional = "";\n'
   codeString += ' if(js' + getVariablePath(v) + '.is_number()) ' + getCXXVariableName(v["Name"]) + ' = js' + getVariablePath(v) + ';\n'
   codeString += ' if(js' + getVariablePath(v) + '.is_string()) ' + getCXXVariableName(v["Name"]) + 'Conditional = js' + getVariablePath(v) + ';\n'
   codeString += ' Korali::JsonInterface::eraseValue(js, "' + getVariablePath(v).replace('"', "'") + '");\n\n'
 
 codeString += ' ' + getParentClass(module) + '::setConfiguration(js);\n'
 
 codeString += ' _type = "' + module["Alias"] + '";\n'
 codeString += ' if(Korali::JsonInterface::isDefined(js, "[\'Type\']")) Korali::JsonInterface::eraseValue(js, "[\'Type\']");\n'   
 
 codeString += ' if(Korali::JsonInterface::isEmpty(js) == false) Korali::logError("Unrecognized settings for ' + module["Name"] + ' (' + module["Alias"] + '): \\n%s\\n", js.dump(2).c_str());\n'
 codeString += '} \n\n'
  
 return codeString
  
####################################################################
  
def createGetConfiguration(module):  
 codeString = 'void ' + module["C++ Class"]  + '::getConfiguration(nlohmann::json& js) \n{\n\n'
 
 codeString += ' js["Type"] = _type;\n'
 
 if 'Configuration Settings' in module:
  for v in module["Configuration Settings"]: 
   codeString += saveValue('js', getVariablePath(v), getCXXVariableName(v["Name"]), getVariableType(v))
 
 if 'Termination Criteria' in module:
  for v in module["Termination Criteria"]: 
   codeString += saveValue('js', '["Termination Criteria"]' + getVariablePath(v), getCXXVariableName(v["Name"]), getVariableType(v))
   
 if 'Internal Settings' in module:   
  for v in module["Internal Settings"]: 
   codeString += saveValue('js', '["Internal"]' + getVariablePath(v), getCXXVariableName(v["Name"]), getVariableType(v))
   
 if 'Variables Configuration' in module:
  codeString += ' for (size_t i = 0; i <  _k->_variables.size(); i++) { \n'
  for v in module["Variables Configuration"]:
   codeString += saveValue('_k->_js["Variables"][i]', getVariablePath(v), '_k->_variables[i]->' + getCXXVariableName(v["Name"]), getVariableType(v))
  codeString += ' } \n'  
   
 if 'Conditional Variables' in module: 
  for v in module["Conditional Variables"]:
   codeString += ' if(' + getCXXVariableName(v["Name"]) + 'Conditional == "") js' + getVariablePath(v) + ' = ' + getCXXVariableName(v["Name"]) + ';\n'
   codeString += ' if(' + getCXXVariableName(v["Name"]) + 'Conditional != "") js' + getVariablePath(v) + ' = ' + getCXXVariableName(v["Name"]) + 'Conditional;\n'
 
 codeString += ' ' + getParentClass(module) + '::getConfiguration(js);\n'
 
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
 
   codeString += ' hasFinished = hasFinished || ' + getParentClass(module) + '::checkTermination();\n' 
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
   
 if 'Conditional Variables' in module:
  for v in module["Conditional Variables"]:
   headerString += ' double ' + getCXXVariableName(v["Name"]) + ';\n'
   headerString += ' std::string ' + getCXXVariableName(v["Name"]) + 'Conditional;\n'
 
 return headerString
 
  
####################################################################

def createVariableDeclarations(module):  
 variableDeclarationString = ''
 
 if 'Variables Configuration' in module:
  for v in module["Variables Configuration"]:
   variableDeclarationString += '  ' + getVariableType(v) + ' ' + getCXXVariableName(v["Name"]) + ';\n'
 
 return variableDeclarationString
 
####################################################################
# Main Parser Routine
####################################################################

koraliDir = os.path.abspath(os.path.dirname(os.path.realpath(__file__)))

# modules List
moduleDetectionList = ''
moduleIncludeList = ''

# Variable Declaration List
varDeclarationSet = set()

# Detecting modules' json file
for moduleDir, relDir, fileNames in os.walk(koraliDir):
 for fileName in fileNames: 
  if '.json' in fileName:
   with open(moduleDir + '/' + fileName, 'r') as file: moduleConfig = json.load(file)
   moduleName = fileName.replace('.json', '')
   
   ####### Adding module to list
   if (not '(Base)' in moduleConfig["Name"]):
    relpath = os.path.relpath(moduleDir, koraliDir)
    filepath = os.path.join(relpath, moduleName + '.hpp')
    moduleIncludeList += '#include "' + filepath + '" \n'
    moduleDetectionList += '  if(moduleType == "' + moduleConfig["Alias"] + '") module = new ' + moduleConfig["C++ Class"] + '();\n'
   
   ###### Producing module code

   moduleCodeString = createSetConfiguration(moduleConfig)
   moduleCodeString += createGetConfiguration(moduleConfig)
   moduleCodeString += createCheckTermination(moduleConfig)
 
   ####### Producing header file
   
   # Loading template header .hpp file
   moduleTemplateHeaderFile = moduleDir + '/' + moduleName + '._hpp'
   with open(moduleTemplateHeaderFile, 'r') as file: moduleTemplateHeaderString = file.read()
   
   # Adding overridden function declarations
   functionOverrideString = ''
   functionOverrideString += ' bool checkTermination() override;\n'
   functionOverrideString += ' void getConfiguration(nlohmann::json& js) override;\n'
   functionOverrideString += ' void setConfiguration(nlohmann::json& js) override;\n'
   newHeaderString = moduleTemplateHeaderString.replace('public:', 'public: \n' + functionOverrideString + '\n')
   
   # Adding declarations
   declarationsString = createHeaderDeclarations(moduleConfig)
   newHeaderString = newHeaderString.replace('public:', 'public: \n' + declarationsString + '\n')
   
   # Retrieving variable declarations
   for varDecl in createVariableDeclarations(moduleConfig).splitlines():
    varDeclarationSet.add(varDecl)
   
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

###### Updating module source file 

moduleBaseCodeFileName = koraliDir + '/module._cpp' 
moduleNewCodeFile = koraliDir + '/module.cpp'
baseFileTime = os.path.getmtime(moduleBaseCodeFileName)
newFileTime = baseFileTime
if (os.path.exists(moduleNewCodeFile)): newFileTime = os.path.getmtime(moduleNewCodeFile)

if (baseFileTime >= newFileTime):
  with open(moduleBaseCodeFileName, 'r') as file: moduleBaseCodeString = file.read()
  newBaseString = moduleBaseCodeString.replace('// Module Include List',  moduleIncludeList)
  newBaseString = newBaseString.replace(' // Module Selection List', moduleDetectionList)
  print('[Korali] Creating: ' + moduleNewCodeFile + '...')
  with open(moduleNewCodeFile, 'w') as file: file.write(newBaseString)

###### Updating module header file

moduleBaseHeaderFileName = koraliDir + '/module._hpp'
moduleNewHeaderFile = koraliDir + '/module.hpp'
with open(moduleBaseHeaderFileName, 'r') as file: moduleBaseHeaderString = file.read()
newBaseString = moduleBaseHeaderString
print('[Korali] Creating: ' + moduleNewHeaderFile + '...')
with open(moduleNewHeaderFile, 'w+') as file: file.write(newBaseString)

###### Updating variable header file
variableDeclarationList = ''
for varDecl in varDeclarationSet:
 variableDeclarationList += varDecl + '\n'

variableBaseHeaderFileName = koraliDir + '/variable/variable._hpp'
variableNewHeaderFile = koraliDir + '/variable/variable.hpp'
with open(variableBaseHeaderFileName, 'r') as file: variableBaseHeaderString = file.read()
newBaseString = variableBaseHeaderString
newBaseString = newBaseString.replace(' // Variable Declaration List', variableDeclarationList)
print('[Korali] Creating: ' + variableNewHeaderFile + '...')
with open(variableNewHeaderFile, 'w+') as file: file.write(newBaseString)