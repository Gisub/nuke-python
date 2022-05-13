# Creates a Read node for the selected Write node

import nuke
import os 
import re

def readFromWrite():
	print 'executing script'

	w = nuke.selectedNode()

	filePath = w.knob('file').getValue()
	print 'filePath is: '+filePath

	dirName = os.path.dirname(filePath)
	print 'dirName is: '+dirName

	fileDirList = re.split('/', filePath)
	fileName = fileDirList [-1]
	print 'fileName is: '+fileName

	extList = os.path.splitext(filePath)
	ext = extList [-1]
	print 'extension is '+ext

	if '_' in fileName:
		fileBaseName = re.split('_', fileName) [0]
	else:
		fileBaseName = re.split('\.', fileName) [0]
	print fileBaseName

	print 'these are all the files in folder'
	fileList = os.listdir(dirName)
	print fileList

	print 'these are the files matching to the write nodes file name'
	res = sorted([k for k in fileList if ext in k])
	res = sorted ([k for k in fileList if fileBaseName in k])
	print res

	firstFileName = res [0]
	print 'firstFileName is: '+firstFileName
	firstFnWithoutExt = os.path.splitext(firstFileName)[0]
	print 'firstFnWithoutExt is '+firstFnWithoutExt
	try:
		firstFrameNr = int(re.split ('_', firstFnWithoutExt) [-1])

	except:
		try:
			firstFrameNr = int(re.split ('\.', firstFnWithoutExt) [-1])
		except:
			firstFrameNr = int(1)
	print 'first frame is: '+str(firstFrameNr)

	lastFileName = res [-1]
	lastFnWithoutExt = os.path.splitext(lastFileName)[0]
	try:
		lastFrameNr = int(re.split ('_', lastFnWithoutExt) [-1])

	except:
		try:
			lastFrameNr = int(re.split ('\.', lastFnWithoutExt) [-1])
		except:
			lastFrameNr = int(1)
	print 'last frame is: '+str(lastFrameNr)

	colorspace = w.knob('colorspace').value()
        if 'default ' in colorspace:
            colorspace = colorspace.replace('default ', '')
            colorspace = colorspace.replace('(', '')
            colorspace = colorspace.replace(')', '')
        print 'colorspace is: '+str(colorspace)

	r = nuke.createNode('Read', "file "+filePath, inpanel=False)

	r.knob('first').setValue(firstFrameNr)
	r.knob('origfirst').setValue(firstFrameNr)

	r.knob('last').setValue(lastFrameNr)
	r.knob('origlast').setValue(lastFrameNr)

	r.knob('colorspace').setValue(colorspace)
