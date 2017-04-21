import getpass, numpy, os

from pulseOperations import extractPulseInfo



folderList = [
    'CHC alpha traces',
    'CHC alpha traces thrsh 180',
    'CHC alpha_gamma traces',
    'CHC gamma traces']

pulseDataTypesToExtract = ['keptData', 'keptXData'] # this turn into keys for a dictionary that extractPulseInfo Outputs
pulseDataTypesToSave = ['keptData']
# folderList = [
#     'CHC alpha traces']

for singleFolder in folderList:
    if getpass.getuser() == "chw3k5": # Caleb Wheeler's User name on his own computer
        parentFolder = '/Users/chw3k5/Desktop/new CHC traces'
    else:
        parentFolder = ''
    folderName = os.path.join(parentFolder, singleFolder)
    outPutFileBase = os.path.join(parentFolder, singleFolder + '_trimmedData')



    extractedDataDict = \
        extractPulseInfo(folderName=folderName,
                         fileNamePrefix=singleFolder + '_',
                         filenameSuffix='.txt',
                         columnNamesToIgnore=['time'],
                         pulseDataTypesToExtract=pulseDataTypesToExtract,
                         skipRows=3,
                         delimiter='\t',
                         trimBeforeMin=True,
                         conv_channels=1,
                         pulseDataTypesToSave=pulseDataTypesToSave,
                         outPutFileBase=outPutFileBase,
                         saveAsColumns=True,
                         maxDataArraysPerFile=5,
                         showTestPlots_Pulses=False,
                         testModeReadIn = True,
                         verbose=True)