## author: Marat Latypov <latmarat@postech.edu>
## created: 2014-09-01

"""
elasplas2umat
=============

This script creates a user material storing elastic and plastic properties 
consequently to "Mechanical Constants" table from a material 
with "Elastic" and "Plastic" tables  

To use, run the script from ABAQUS/CAE with your model opened. 
The model must contain at least one material with 
separate tables containing elastic and plastic properties

This script is useful when, instead of conventional simulations, 
user subroutine UMAT with isotropic plasticity (e.g. j2isoVelGradOut) is used.

"""
from abaqus import *
from abaqusConstants import *
import __main__

def elasplas2umat():
	"""Create a UMAT material for isoVelOut user subroutine given material with elastic and plastic properties."""
	
	def selitem(allItems, itemType, errFlag=True):
		"""Select item if there is ambiguity"""
		
		if (allItems == []) and errFlag:
			print 'Me: ERROR! No %s found. Create proper %s and try again' % (itemType, itemType)		
			return None
		elif len(allItems) > 1:
			itemList = '\n'.join(iItem for iItem in allItems)
			itemRequest = 'Found several %s:\n%s \nEnter the number of the %s\nto work with starting from 0' % (itemType+'s', itemList, itemType)
			itemNo = eval(getInput(itemRequest,'0'))
		elif len(allItems) == 1:
			itemNo = 0
		return allItems[itemNo]
	
	import material
	print 'Me: -------------------------------------------------------------'
	print 'Me: Starting the procedure for transferring properties to umat file'
	
	# Select the model
	allModels = mdb.models.keys()
	myModelName = selitem(allModels, 'model')
	myModel = mdb.models[myModelName]	
	print 'Me: Working with %s model' % myModelName
	
	# Select the material to get properties from
	allMaterials = myModel.materials.keys()
	oldMatName = selitem(allMaterials, 'material')
	if oldMatName == None:
		return 'Me: Error! There is no material in the model. Creat a material, assign elastic and plastic properties, and try again.'
	oldMat = myModel.materials[oldMatName]
	print 'Me: Properties will be transferred from %s material' % oldMatName
	
	# Get elastic and plastic properties from the existing material
	try: 
		elas = oldMat.elastic.table
		plas = oldMat.plastic.table
	except AttributeError:
		print 'Me: Error! There are no elastic or plastic properties in the material. Assign elastic and plastic properties, and try again.'
		return
		
	# Create a single list with elastic and plastic properties
	umatProp = []
	propList = elas+plas
	for pair in propList:
		for item in pair:
			umatProp.append(float(item))
	
	# Create UMAT material with elastic and plastic  
	# properties stored in mechanical constants
	uMatName = oldMatName + '_uMat'
	uMat = myModel.Material(name=uMatName)
	uMat.UserMaterial(mechanicalConstants=umatProp)	
	uMat.Depvar(n=22)
	print 'Me: %s material is created' % uMatName
	print 'Me: Elastic and plastic properties are stored to Mechanical Constants'
	print 'Me: 22 Solution Devepndent Variables are allocated'
	print 'Me: elasplas2umat has completed successfully'
	print 'Me: -------------------------------------------------------------'
	return

elasplas2umat()
