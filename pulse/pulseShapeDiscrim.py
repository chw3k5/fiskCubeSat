import getpass, numpy, os

from pulseOperations import extractPulseInfo
from quickPlots import quickHistograms


folderList = [
    'CHC alpha traces',
    'CHC alpha traces thrsh 180',
    'CHC alpha_gamma traces',
    'CHC gamma traces']
numOfExponents = 2
pulseDataTypesToExtract = ['integral', 'fittedCost']
for index in range(numOfExponents):
    pulseDataTypesToExtract.extend(['fittedAmp' + str(index + 1), 'fittedTau' + str(index + 1)]) # this turn into keys for a dictionary that extractPulseInfo Outputs
pulseDataForHistogram = pulseDataTypesToExtract[:]
pulseDataTypesToSave = []

showTestPlots_Pulses = False
showHistPlots = False
saveHistPlots = True
verbose = True


if getpass.getuser() == "chw3k5": # Caleb Wheeler's User name on his own computer
    parentFolder = '/Users/chw3k5/Desktop/new CHC traces'
else:
    parentFolder = ''
plotFolder = os.path.join(parentFolder, 'plots')

# folderList = [
#     'CHC alpha traces']

for singleFolder in folderList:
    folderName = os.path.join(parentFolder, singleFolder)
    outPutFileBase = os.path.join(parentFolder, singleFolder + '_trimmedData')
    plotFileName = os.path.join(plotFolder, "hist_" + singleFolder)


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
                         numOfExponents=numOfExponents,
                         upperBoundAmp=float,
                         pulseDataTypesToSave=pulseDataTypesToSave,
                         outPutFileBase=outPutFileBase,
                         saveAsColumns=True,
                         maxDataArraysPerFile=100,
                         showTestPlots_Pulses=showTestPlots_Pulses,
                         testModeReadIn=False,
                         verbose=verbose)

    if not os.path.exists(plotFolder):
        os.mkdir(plotFolder)

    quickHistograms(extractedDataDict, columns=2, bins=10, keys=pulseDataForHistogram,
                    plotFileName=plotFileName + 'hist', savePlots=saveHistPlots, doEps=False,
                    showPlots=showHistPlots,
                    verbose=verbose)
