import numpy

from quickPlots import quickPlotter
from pulseReadIn import loadPulses, saveProcessedData


def initializeTestPlots(doShow, verbose):
    plotDict = {}
    plotDict['verbose'] = verbose
    # These must be a single value
    plotDict['title'] = 'Pulse Data Read in and Trim.'
    plotDict['xlabel'] = 'Time'
    plotDict['ylabel'] = 'Voltage'
    plotDict['legendAutoLabel'] = False
    plotDict['doLegend'] = True
    plotDict['legendLoc'] = 0
    plotDict['legendNumPoints'] = 3
    plotDict['legendHandleLength'] = 5
    plotDict['doShow'] = True

    # These can be a list or a single value
    plotDict['yData'] = []
    plotDict['xData'] = []
    plotDict['legendLabel'] = []
    plotDict['fmt'] = []
    plotDict['markersize'] = []
    plotDict['alpha'] = []
    plotDict['ls'] = []
    plotDict['lineWidth'] = []
    return plotDict


def appendToTestPlots(plotDict, arrayData, xData, legendLabel, fmt, markersize, alpha, ls, lineWidth):
    # These can be a list or a single value
    plotDict['yData'].append(arrayData)
    if xData is None:
        plotDict['xData'].append(range(len(arrayData)))
    else:
        plotDict['xData'].append(xData)
    plotDict['legendLabel'].append(legendLabel)
    plotDict['fmt'].append(fmt)
    plotDict['markersize'].append(markersize)
    plotDict['alpha'].append(alpha)
    plotDict['ls'].append(ls)
    plotDict['lineWidth'].append(lineWidth)
    return plotDict


def convData(arrayData, conv_channels):
    kernel1 = numpy.ones(conv_channels) / float(conv_channels)
    smoothedData = numpy.convolve(arrayData, kernel1, 'same')
    return smoothedData


def trimToMin(arrayData, smoothedData, xData):
     # trim the data before the minimum value
    dataMinIndex = numpy.argmin(smoothedData)
    keptData = arrayData[dataMinIndex:]
    keptXData = xData[dataMinIndex:]
    return keptData, keptXData



def pulsePipeline(pulseDict, plotDict, conv_channels, trimBeforeMin):
    arrayData = pulseDict['arrayData']
    xData = pulseDict['xData']
    # Make x data, and send the raw data to the plot
    if plotDict['doShow']:
        plotDict = appendToTestPlots(plotDict,
                                     arrayData,
                                     xData,
                                     legendLabel='Read In Data ' + str(pulseDict['uniqueID']),
                                     fmt='None',
                                     markersize=6,
                                     alpha=1.0,
                                     ls='solid',
                                     lineWidth=2)
    # Convolutions
    if conv_channels > 1:
        smoothedData = convData(arrayData, conv_channels)
        pulseDict['smoothedData'] = smoothedData
        if plotDict['doShow']:
            plotDict = appendToTestPlots(plotDict,
                                         smoothedData,
                                         xData,
                                         legendLabel='Smoothed Data, n=' + str(conv_channels),
                                         fmt='None',
                                         markersize=6,
                                         alpha=1.0,
                                         ls='dotted',
                                         lineWidth=1)
    else:
        smoothedData = arrayData
        pulseDict['smoothedData'] = None

    # trim all the data prior to the minimum
    if trimBeforeMin:
        keptData, keptXData = trimToMin(arrayData, smoothedData, xData)
        pulseDict['keptData'] = keptData
        pulseDict['keptXData'] = keptXData
        if plotDict['doShow']:
            plotDict = appendToTestPlots(plotDict,
                                         keptData,
                                         keptXData,
                                         legendLabel='trimmed data',
                                         fmt='None',
                                         markersize=6,
                                         alpha=1.0,
                                         ls='dashed',
                                         lineWidth=1)
    else:
        keptData = smoothedData
        keptXData = xData
        pulseDict['keptData'] = None
        pulseDict['keptXData'] = None

    return pulseDict, plotDict


def extractPulseInfo(folderName, fileNamePrefix='', filenameSuffix='',
                     columnNamesToIgnore=['time'],
                     pulseDataTypesToExtract=[],
                     skipRows=1, delimiter=',',
                     trimBeforeMin=True,
                     conv_channels=1,
                     pulseDataTypesToSave=[],
                     outPutFileBase='trimmedData.csv',
                     saveAsColumns=True,
                     maxDataArraysPerFile=100,
                     showTestPlots_Pulses=False,
                     testModeReadIn=False,
                     verbose=True):
    if 'uniqueID' not in pulseDataTypesToExtract:
        pulseDataTypesToExtract.append('uniqueID')


    listOfDataDicts = loadPulses(folderName,
                                 fileNamePrefix=fileNamePrefix,
                                 filenameSuffix=filenameSuffix,
                                 skipRows=skipRows,
                                 delimiter=delimiter,
                                 testMode=testModeReadIn,
                                 verbose=verbose)

    numOfDataDicts = len(listOfDataDicts)
    modLen = max((int(numOfDataDicts / 200.0), 1))
    if verbose:
        if conv_channels > 1:
            print "The data is to be smoothed with a top hat kernel of " + str(conv_channels) + " channels."
        if trimBeforeMin:
            print "All the data values before the minimum value will be trimmed away before being saved."
        print " "
    columnNamesToIgnore.append('fileName'.lower())
    columnNamesToIgnore.append('uniqueID'.lower())
    columnNamesToIgnore.append('xData'.lower())

    # initialize the dictionary to extract data from processed pulses
    extractedDataDict = {}
    for pulseDataType in pulseDataTypesToExtract:
        extractedDataDict[pulseDataType] = []


    for IDindex in range(numOfDataDicts):
        tableDict = listOfDataDicts[IDindex]
        uniqueID = tableDict['uniqueID']
        tableDict = listOfDataDicts[IDindex]
        dataKeys = []
        tableDict['xData'] = None
        tableDictKeys = tableDict.keys()
        for testKey in tableDictKeys:
            if not testKey.lower() in columnNamesToIgnore:
                dataKeys.append(testKey)
            if 'time' == testKey.lower():
                tableDict['xData'] = tableDict[testKey]
        plotDict = initializeTestPlots(showTestPlots_Pulses, verbose)
        for key in dataKeys:
            # make a new dictionary for each pulse, there may be many pulses in tableDict
            pulseDict = {}
            # assign the pulse yData
            pulseDict['arrayData'] = tableDict[key]
            # if the pulse has x Data, assign it
            if tableDict['xData'] is None:
                pulseDict['xData'] = len(pulseDict['arrayData'])
            else:
                pulseDict['xData'] = tableDict['xData']
            # assign a unique iD to this pulse for later identification.
            pulseDict['uniqueID'] = key.replace(' ', '_') + '_' + uniqueID
            pulseDict['rawDataFileName'] = tableDict['fileName']

            # process the pulse
            pulseDict, plotDict = pulsePipeline(pulseDict, plotDict, conv_channels, trimBeforeMin)

            # extract the required data types for output
            for pulseDataType in pulseDataTypesToExtract:
                extractedDataDict[pulseDataType].append(pulseDict[pulseDataType])
        if showTestPlots_Pulses:
            quickPlotter(plotDict=plotDict)

        if verbose:
            if IDindex % modLen == 0:
                print "File read-in and operations are " \
                      + str('%02.2f' % (IDindex*100.0/float(numOfDataDicts))) + " % complete."

    for saveDataType in pulseDataTypesToSave:
        listOfHeaderNames = extractedDataDict['uniqueID']
        listOfDataArrays = extractedDataDict[saveDataType]
        fileBaseName = outPutFileBase + '_' + saveDataType
        saveProcessedData(listOfHeaderNames, listOfDataArrays, fileBaseName,
                          maxDataArraysPerFile=maxDataArraysPerFile, delimiter=delimiter,
                          saveAsColumns=saveAsColumns, verbose=verbose)
    return extractedDataDict
