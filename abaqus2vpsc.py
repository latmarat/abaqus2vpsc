## author: Marat Latypov <latmarat@postech.edu>
## created: 2014-09-01

"""
vel4vpsc
========

This script writes deformation history
from an Abaqus/Standard simulation to a file for 
subsequent use in VPSC. 

To use, run the script from ABAQUS/CAE.
When asked, provide 
- path to the odb containing field 
  output for velocity gradient in SDV; 
- instance name of the deformable part of interest
- label of the element for which deformation history is needed

This script is written specifically for use in pair with isoVelOut.for
user subroutine. However, it can be also modified for use with other 
user subroutines that store velocity gradient in SDV. 

The script requires numpy module. 
Numpy module comes with Abaqus ver. 6.11 or older 
or can be installed manually. Otherwise, lines with 
numpy arrays can be rewritten with lists instead.

"""

from abaqus import *
from abaqusConstants import *
from odbAccess import *
import __main__

import os
import numpy as np

def vel4vpsc():
	"""Write history of velocity gradient to a file for VPSC."""

	
	# Request path to the odb, instance name and the element label for which deformation history is needed
	myFields = (('Full path to odb','C:\\Temp\\.odb' ), ('Instance Name:', 'PART-1-1'), ('Element Number:', '1'), )
	odbPath, instanceName, elementNo = getInputs(fields=myFields, label='Input:', dialogTitle='Input', )

	# Handle Cancel button
	if elementNo == None:
		print 'Me: Input cancelled. Exit operation'
		return
	else:
		# Get integer from string for the element label
		elementNo = int(elementNo)
	
	print 'Me: Starting the procedure of writing FE deformation history for VPSC'
	
	# Open the odb and request re-input if the odb is not found
	try:
		myOdb = session.openOdb(name=odbPath)
	except OdbError:
		newOdbPath = getInput('odb was not found! Re-input path to the odb:','C:\\Temp\\.odb')
		if (newOdbPath == None) or (newOdbPath =='C:\\Temp\\.odb'):
			print 'Me: ERROR! Correct path to odb was not provided'
			return
		else:
			odbPath = newOdbPath
			myOdb = session.openOdb(name=odbPath)
			print 'Me: odb is successfully opened at %s' % odbPath
				
	# Name the Step objects for convenience
	myStepName = myOdb.steps.keys()[0]
	myStep = myOdb.steps[myStepName]
	print 'Me: Working with step %s and instance %s' % (myStepName, instanceName)
	
	# Check if the given instance exists and request re-input if it doesn't
	instanceNames = myOdb.rootAssembly.instances.keys()
	if instanceName not in instanceNames:
		instanceList = '\n'.join(iInstance for iInstance in instanceNames)
		instMsg = '%s was not found! \nRe-input the instance name. \nInstances in the odb:\n%s'  % (instanceName, instanceList)
		newInstanceName = getInput(instMsg,'PART-1-1') 
		if newInstanceName not in myOdb.rootAssembly.instances.keys() or newInstanceName==None:
			print 'Me: ERROR! Correct instance name was not provided'
			return
		else: 
			instanceName = newInstanceName
	
	# Check if the element with the given label exists in the instance
	try:
		myOdb.rootAssembly.instances[instanceName].elements[elementNo-1]
	except IndexError:
		print 'Me: ERROR! Element label was incorrect. Re-check the element label and try again.'
		return
	
	# Create a tuple containing element number
	el4out = (elementNo,)
	
	# Create an element set containing the element of interest		
	setName = 'el4vpsc'
	myOdb.rootAssembly.ElementSetFromElementLabels(name = setName, elementLabels = ((instanceName,el4out),)) 
	el4outSet = myOdb.rootAssembly.elementSets['el4vpsc']
	print 'Me: Deformation history will be written for element #%d, which is placed to a temporary set %s' % (elementNo, setName)
	
	# Create a list of variables for output
	variables = ['SDV14', 'SDV15', 'SDV16', 'SDV17', 'SDV18', 'SDV19', 'SDV20', 'SDV21', 'SDV22']
	print 'Me: Velocity gradient is assumed to be stored in variables SDV14 through SDV22'
	
	# Check that all SDV are present in the odb and exit if not
	for var in variables:
		try:
			myStep.frames[1].fieldOutputs[var]
		except IndexError:
			print 'Me: ERROR! There are no frames with field output. Re-run FE simulation with proper field output and try again.'
			return
		except KeyError:
			print 'Me: ERROR! At least variable %s is not found in the odb. Re-run FE simulation with proper field output and try again.' % var
			return
	
	# Get the number of frames with field output
	numFrames = len(myStep.frames)
	print 'Me: Reading output for %d frames.....' % numFrames
	# Allocate a numpy array that will contain all the data for output
	velGrad = np.zeros((numFrames,11))

	# Loop over velocity gradient components (i) and frames (j)
	for i in range(11):
		for j in range(1,numFrames):
			if i == 0:
				# then get the step number
				velGrad[j,i] = j
			elif i == 10:
				# then get the time increment for this step
				velGrad[j,i] = myStep.frames[j].frameValue-myStep.frames[j-1].frameValue
			else:
				# then get the components of the velocity gradient 
				velGradField = myStep.frames[j].fieldOutputs[variables[i-1]]
				field = velGradField.getSubset(region=el4outSet, position=CENTROID)
				velGrad[j,i] = field.values[0].data

	# Get rid of very small values in the numpy array
	velGrad[abs(velGrad) <= 10e-6]	 = 0.0	

	# Open the file for output and write the header there
	outFileName = os.path.dirname(os.path.abspath(odbPath)) + '\FE-Lij_hist.dat'
	outFile = open(outFileName,'w') 
	outFile.write('%4d' % (numFrames-1))
	outFile.write('%4d' % 7)
	outFile.write('%7.4f' % velGrad[1,10])
	outFile.write('%8.f' % 298)
	outFile.write('         nsteps  ictrl  eqincr  temp\n')
	outFile.write(' step         L11         L12         L13         L21         L22         L23         L31         L32         L33         tincr\n')

	# Write step number, velocity gradient, and time increment to the file skipping the starting line where L = 0
	np.savetxt(outFile, velGrad[1:,:], fmt='%3i %12.4e %12.4e %12.4e %12.4e %12.4e %12.4e %12.4e %12.4e %12.4e %12.4e')
	print 'Me: Deformation history for VPSC is written to file %s' % outFileName
	print '---------------------------------------------------------------------'
	
	# Close the output file and the odb
	outFile.close()
	myOdb.close()
	
	return

vel4vpsc()