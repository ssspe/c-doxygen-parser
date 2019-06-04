import xml.etree.ElementTree as ET
import os
import sys
from docx import Document	
import argparse

class Function:
	def __init__(self):
		self.funcName = ''
		self.funcDesc = ''
		self.funcParam = []
		
	def setFuncName(self, funcName):
		self.funcName = funcName
		
	def setFuncDesc(self, funcDesc):
		self.funcDesc = funcDesc
		
	def addFuncParam(self, funcParam):
		self.funcParam.append(funcParam)
		
	def __repr__(self):
		return f'Function Name: {self.funcName}, Function Desc: {self.funcDesc}, Function Paramaters: {self.funcParam}'
		
		
class Struct:
	def __init__(self):
		self.structName = ''
		self.structDesc = ''
		self.structDefs = []
		
	def setStructName(self, structName):
		self.structName = structName
		
	def setStructDesc(self, structDesc):
		self.structDesc = structDesc
		
	def addStructDef(self, structDef):
		self.structDefs.append(structDef)
		
	def __repr__(self):
		return f'Struct Name: {self.structName}, Struct Desc: {self.structDesc}, Struct Defs: {self.structDefs}'

		
class StructDef:
	def __init__(self):
		self.defName = ''
		self.defType = ''
		self.defDesc = ''
		
	def setStructDefName(self, name):
		self.defName = name
	
	def setStructDefType(self, type):
		self.defType = type
	
	def setStructDefDesc(self, desc):
		self.defDesc = desc
			
	def __repr__(self):
		return f'Struct Def Type: {self.defType}, Struct Def Name: {self.defName}, Struct Def Desc: {self.defDesc}' 
		
		
class Enum:
	def __init__(self):
		self.enumName = ''
		self.enumDesc = ''
		self.enumDefs = []
		
	def setEnumName(self, enumName):
		self.enumName = enumName
		
	def addEnumDef(self, enumDef):
		self.enumDefs.append(enumDef)
		
	def setEnumDesc(self, enumDesc):
		self.enumDesc = enumDesc
	
	def __repr__(self):
		return f'Enum Name: {self.enumName}, Enum Desc: {self.enumDesc}, Enum Defs: {self.enumDefs}'
	
	
class Macro:
	def __init__(self):
		self.macroName = ''
		self.macroValue = ''
		
	def setMacroName(self, macroName):
		self.macroName = macroName
		
	def setMacroValue(self, macroValue):
		self.macroValue = macroValue
	
	def __repr__(self):
		return f'Macro Name: {self.macroName}, Macro Value: {self.macroValue}'
		

class Params:
	def __init__(self):
		self.paramName = ''
		self.paramType = ''
		self.paramDesc = ''
		self.isInput = False
		
	def setParamName(self, paramName):
		self.paramName = paramName
		
	def setParamType(self, paramType):
		self.paramType = paramType
	
	def setParamDesc(self, paramDesc):
		self.paramDesc = paramDesc
		
	def setParamDirection(self, paramDirection):
		self.isInput = ( paramDirection == "in" )
		
	def __repr__(self):
		return f'Param Name: {self.paramName}, Param Type: {self.paramType}, Param Desc: {self.paramDesc}, Is Input?: {self.isInput}'
		
		
def processStructures(xmlRoot, baseFilePath):
	""" Processes the XML to find all structures
	
	Searches through the file for structure references.
	Will then grab the associated file and parse to find the name and description of the Struct
	as well as the name, type and description of the Struct members
    
	Args:
        xmlRoot (Element): The root of the XML file.
		
	Returns:
		A list of Struct objects
    """
	
	structList = []

	for struct in xmlRoot.findall('compounddef/innerclass'):
		structDefList = []
		tempStruct = Struct()
		
		# Finding referenced file and parsing it
		structFileName = struct.attrib['refid'] 
		structFile = os.path.join(baseFilePath, f'{structFileName}.xml')
		structDefTree = ET.parse(structFile)
		structDefRoot = structDefTree.getroot()
		
		structName = structDefRoot.find('compounddef/compoundname')
		structDesc = structDefRoot.find('compounddef/detaileddescription/para')
		
		if structDesc is None:
			# Struct description may be brief or detailed
			structDesc = structDefRoot.find('compounddef/briefdescription/para')
			
		tempStruct.setStructName(structName.text)
		tempStruct.setStructDesc(structDesc.text)
		
		# Parsing all members of the Struct
		for structMember in structDefRoot.findall('compounddef/sectiondef/memberdef'):
			tempStructDef = StructDef()
			name = structMember.find("name").text
			type = structMember.find("type").text
			desc = structMember.find("briefdescription/para").text
			
			if type is None:
				# Struct type may be hidden in ref if it is a local type
				type = structMember.find("type/ref").text
				
			tempStructDef.setStructDefName(name)
			tempStructDef.setStructDefDesc(desc)
			tempStructDef.setStructDefType(type)
	
			tempStruct.addStructDef(tempStructDef)
			
		structList.append(tempStruct)
	
	return structList
	
	
def processEnumerators(xmlRoot):
	""" Processes the XML to find all enumerators
	
	Searches through the file for all Enums.
	Will then grab the name and description of the Enum
	as well as the name of the Enum members
    
	Args:
        xmlRoot (Element): The root of the XML file.
		
	Returns:
		A list of Enum objects
    """
	
	enumList = []
	
	enumContainer = xmlRoot.find("compounddef/sectiondef[@kind='enum']")
	try:
		for enum in enumContainer.findall('memberdef'):
			tempEnum = Enum()
			
			enumName = enum.find("name")
			enumDesc = enum.find('detaileddescription/para')
			if enumDesc is None:
				# Enum description may be brief of detailed
				enumDesc = enum.find('briefdescription/para')
				
			tempEnum.setEnumName(enumName.text)
			tempEnum.setEnumDesc(enumDesc.text)
			
			# Parsing all members of the Enum
			for enumValue in enum.findall('enumvalue'):
				tempEnum.addEnumDef(enumValue.find("name").text)
				
			enumList.append(tempEnum)
	except:
		print("No Enums")
	
	return enumList

	
def processMacros(xmlRoot):
	""" Processes the XML to find all macros
	
	Searches through the file for all Macros.
	Will then grab the name and value of the Macro
    
	Args:
        xmlRoot (Element): The root of the XML file.
		
	Returns:
		A list of Macro objects
    """
	
	macroList = []
	
	macroContainer = xmlRoot.find("compounddef/sectiondef[@kind='define']")
	for macro in macroContainer.findall('memberdef'):
		tempMacro = Macro()
		
		macroName = macro.find('name').text
		macroValue = macro.find('initializer').text
		
		if macroValue == "( ":
			# Value is hidden in ref, getting ref and adding brackets
			macroValue = "( " + macro.find('initializer/ref').text + " )"
			
		tempMacro.setMacroName(macroName)
		tempMacro.setMacroValue(macroValue)
		
		macroList.append(tempMacro)
		
	return macroList

	
def processFunctions(xmlRoot):
	""" Processes the XML to find all functions
    
	Creates an array of private and public function along with their
	input params, name and description.
	
	Args:
        xmlRoot (Element): The root of the XML file.
		
	Returns:
		A list of Function objects
    """
	
	funcList = []
	
	funcContainer = xmlRoot.find("compounddef/sectiondef[@kind='func']")
	for func in funcContainer.findall('memberdef'):
		tempFunc = Function()
		
		funcName = func.find('name').text
		funcDesc = func.find('detaileddescription/para')
		if funcDesc is None:
			# Enum description may be brief or detailed
			funcDesc = func.find('briefdescription/para')
		
		# Need to recheck in case no description is available
		if funcDesc is None:
			tempFunc.setFuncDesc("No Description")
		else:
			tempFunc.setFuncDesc(funcDesc.text)
			
		tempFunc.setFuncName(funcName)
		
		# Getting all params
		for param in func.findall('param'):
			tempParam = Params()
			paramType = param.find('type').text

			# We have inputs!
			if paramType != "void":
				localType = param.find('type/ref')
				
				# Local type hidden in ref
				if localType is not None:
					paramType = xstr(paramType) + localType.text
				paramName = param.find('declname').text

				# Getting the description of the input
				paramList = func.find('detaileddescription/para/parameterlist')
				for paramElement in paramList.findall('parameteritem'):
					tempName = paramElement.find('parameternamelist/parametername').text
					paramDirection = paramElement.find('parameternamelist/parametername').attrib['direction']
					
					# Finding the extended description of our param
					if tempName == paramName:
						paramDesc = paramElement.find('parameterdescription/para').text
						tempParam.setParamDesc(paramDesc);
						tempParam.setParamName(paramName)
						tempParam.setParamType(paramType)
						tempParam.setParamDirection(paramDirection)
				
				tempFunc.addFuncParam(tempParam)
		
		funcList.append(tempFunc)
		
	return funcList

	
def xstr(string):
	""" Checks if the input is None, if not return the value
	
	Args:
        string (Unknown): The element to be processed
		
	Returns:
		Empty string if None, the original value if not
    """

	if string is None:
		return ''
	return str(string)

			
def parse_arguments():
	""" Argument parser to get the file paths of the XML documents
	
	Adds helpful text for the user as well as optional arguments for style.
	
	Returns:
		Dictionary of arguments passed to the program
    """
	
	parser=argparse.ArgumentParser(
		description='''Doxygen XML to Word parser. 3 arguments should be passed in, base file path 
		of the source/header files, the name of the code file and then the name of the header file. e.g. 
		"...\cid\comms\code\" "sf__random_function_&c.xml" "sf__random_function_&h.xml" ''',
		epilog="""All's well that ends well.""")
	parser.add_argument('filePath', help="Base file path, pointing to just before the source/include directory")
	parser.add_argument('codeFile', help="Code file name in XML after doxygen, normally ending in &c.xml")
	
	return vars(parser.parse_args())
			
			
if __name__ == "__main__":
	args = parse_arguments()
	
	# Getting file paths
	baseCodeFile = os.path.join(args['filePath'], args['codeFile'])
	
	print(f"Processing: {baseCodeFile}")
	
	# Parsing code file
	codeTree = ET.parse(baseCodeFile)
	codeRoot = codeTree.getroot()
	
	structList = processStructures(codeRoot, os.path.join(args['filePath']))
	enumList = processEnumerators(codeRoot)
	macroList = processMacros(codeRoot)
	funcList = processFunctions(codeRoot)
	
	print("All Done")












